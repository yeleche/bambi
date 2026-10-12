from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import ifcopenshell
import tempfile
import os
from typing import List, Dict, Any

app = FastAPI(title="Bambi BIM Interrogation API", description="Upload and interrogate BIM/IFC models")

# In-memory store for demo (use DB in production)
models = {}

@app.post("/upload")
async def upload_model(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".ifc"):
        raise HTTPException(status_code=400, detail="Only IFC files supported in MVP")
    
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    
    try:
        ifc = ifcopenshell.open(tmp_path)
        model_id = file.filename
        models[model_id] = ifc
        
        # Basic stats
        products = ifc.by_type("IfcProduct")
        return {
            "model_id": model_id,
            "filename": file.filename,
            "element_count": len(products),
            "message": "Model uploaded and parsed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse IFC: {str(e)}")
    finally:
        os.unlink(tmp_path)

@app.get("/models")
async def list_models():
    return {"models": list(models.keys())}

@app.get("/models/{model_id}/elements")
async def get_elements(model_id: str, limit: int = 100):
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    ifc = models[model_id]
    products = ifc.by_type("IfcProduct")[:limit]
    elements = []
    for p in products:
        elements.append({
            "id": p.id(),
            "global_id": getattr(p, "GlobalId", None),
            "name": getattr(p, "Name", None),
            "type": p.is_a()
        })
    return {"elements": elements, "count": len(products)}

@app.get("/models/{model_id}/elements/{element_id}/properties")
async def get_properties(model_id: str, element_id: int):
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    ifc = models[model_id]
    element = ifc.by_id(element_id)
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Extract properties (simplified)
    props = {
        "id": element.id(),
        "type": element.is_a(),
        "name": getattr(element, "Name", None),
        "description": getattr(element, "Description", None),
        "global_id": getattr(element, "GlobalId", None),
    }
    # Property sets
    for definition in getattr(element, "IsDefinedBy", []):
        if definition.is_a("IfcRelDefinesByProperties"):
            pset = definition.RelatingPropertyDefinition
            if pset.is_a("IfcPropertySet"):
                props[pset.Name] = {}
                for prop in pset.HasProperties:
                    if prop.is_a("IfcPropertySingleValue"):
                        props[pset.Name][prop.Name] = prop.NominalValue.wrappedValue if prop.NominalValue else None
    return props

@app.get("/models/{model_id}/search")
async def search_elements(model_id: str, type: str = None, name: str = None):
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    ifc = models[model_id]
    products = ifc.by_type("IfcProduct")
    results = []
    for p in products:
        match = True
        if type and p.is_a() != type:
            match = False
        if name and (not getattr(p, "Name", None) or name.lower() not in p.Name.lower()):
            match = False
        if match:
            results.append({
                "id": p.id(),
                "name": getattr(p, "Name", None),
                "type": p.is_a()
            })
    return {"results": results[:200], "count": len(results)}

@app.get("/models/{model_id}/quantities")
async def get_quantities(model_id: str):
    if model_id not in models:
        raise HTTPException(status_code=404, detail="Model not found")
    ifc = models[model_id]
    type_counts = {}
    for p in ifc.by_type("IfcProduct"):
        t = p.is_a()
        type_counts[t] = type_counts.get(t, 0) + 1
    return {"quantities_by_type": type_counts}

@app.get("/")
async def root():
    return {"message": "Bambi BIM Interrogation API", "docs": "/docs"}
