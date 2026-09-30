# main.py


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from algorithms.d8_flow import calculate_flow
from algorithms.gen_advisories import generate_warnings
from algorithms.surge_inundation import predict_surge
from algorithms.vulnerability_scorer import calculate_vulnerability

import json, os, uvicorn


app = FastAPI(title = "Storm Grid Live API")
app.add_middleware(CORSMiddleware, allow_origins = ['*'], allow_methods = ['*'], allow_headers = ['*'])


class StormParameters(BaseModel):
    lat: float
    lon: float
    wind_kph: float
    pressure_mb: float


@app.post('/api/forecast')
def generate_live_forecast_stream(storm: StormParameters):
    def event_generator():
        # Step 1: Flow
        yield json.dumps({'status': "Mapping topographic flow..."}) + '\n'

        flow_data = calculate_flow(storm.lat, storm.lon)
        
        # Step 2: Surge
        yield json.dumps({'status': "Predicting storm surge zones..."}) + '\n'

        surge_poly = predict_surge(storm.lat, storm.lon, storm.wind_kph, storm.pressure_mb)
        
        # Step 3: Intersection & Scoring
        yield json.dumps({'status': "Scoring infrastructure vulnerability..."}) + '\n'

        at_risk_assets = calculate_vulnerability('data/puri_infra.geojson', surge_poly, flow_data)
        
        # Push all map data to the frontend immediately before making the LLM wait
        yield json.dumps({'status': "Awaiting Gemini advisory generation...", 'partial_data': {'flow': flow_data, 'surge': surge_poly, 'assets': at_risk_assets}}) + '\n'
        
        # Step 4: LLM Orchestration
        advisories = generate_warnings(at_risk_assets)
        
        # Final Completion
        yield json.dumps({'status': 'COMPLETE', 'final_data': advisories}) + '\n'

    return StreamingResponse(event_generator(), media_type = 'application/x-ndjson')


port = int(os.environ.get('PORT', 10000))

uvicorn.run('main:app', host = '0.0.0.0', port = port)
