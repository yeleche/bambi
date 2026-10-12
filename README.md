# Bambi – BIM Interrogation Platform

A web-based tool that lets users upload BIM/Revit models (primarily IFC, with notes for RVT) and perform advanced interrogation, coordination, and review functions comparable to Autodesk Navisworks—without requiring desktop software.

## Executive Summary

**Bambi** is a cloud-friendly platform for interrogating BIM models. Upload an IFC (or converted RVT), explore in 3D, inspect element properties, search/filter, extract quantities, and support basic coordination workflows.

### Core Capabilities (MVP focus)
- Multi-format upload (IFC primary; RVT via APS or conversion)
- Interactive 3D visualization and navigation (web-ifc / xeokit compatible)
- Deep element interrogation: select objects to view full properties/parameters
- Advanced search, filtering, and selection sets
- Quantification and takeoffs (counts, basic quantities)
- Foundation for clash detection, markups, and collaboration

## Tech Stack (MVP)

- **Backend**: Python FastAPI + [IfcOpenShell](https://ifcopenshell.org/) for parsing, property extraction, queries
- **Frontend**: Placeholder for web-ifc + Three.js or xeokit viewer (or integrate That Open components)
- **Storage**: Local or extend to S3/DB for production

Full native RVT support requires Autodesk Platform Services (APS/Forge) Model Derivative API.

## Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://localhost:8000/docs for API.

Upload an IFC via the `/upload` endpoint, then query elements, properties, etc.

## Roadmap

- [ ] Full web 3D viewer with selection → properties
- [ ] Clash detection (hard/clearance)
- [ ] BCF issues export
- [ ] Multi-model federation
- [ ] Natural language queries
- [ ] RVT native via APS

## License

MIT
