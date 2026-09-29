# main.py


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import os


app = FastAPI(title = "Puri Cyclone Command Center API")
app.add_middleware(CORSMiddleware, allow_origins = ['*'], allow_credentials = True, allow_methods = ['*'], allow_headers = ['*'])

DATA_DIR = 'data'
OUTPUT_DIR = 'outputs'


def serve_file(path):
    if not os.path.exists(path):
        raise HTTPException(status_code = 404, detail = f"File not found: {path}")

    return FileResponse(path)


@app.get('/api/infra')
def get_infra():

    return serve_file(os.path.join(DATA_DIR, 'puri_infra.geojson'))

@app.get('/api/hazards/surge')
def get_surge():

    return serve_file(os.path.join(DATA_DIR, 'surge_polygon.geojson'))

@app.get('/api/hazards/flood')
def get_flood():

    return serve_file(os.path.join(OUTPUT_DIR, 'flood_pathways.geojson'))

@app.get('/api/vulnerabilities')
def get_vulnerabilities():

    return serve_file(os.path.join(OUTPUT_DIR, 'at_risk_assets.json'))

@app.get('/api/advisories')
def get_advisories():

    return serve_file(os.path.join(OUTPUT_DIR, 'advisories.json'))

@app.get('/health')
def health_check():

    return {'status': 'operational', 'engine': "FastAPI + Gemini"}
