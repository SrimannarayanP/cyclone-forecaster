# STORM-GRID

STORM-GRID: PARAMETRIC CYCLONE IMPACT ENGINE
**STORM-GRID** is an AI-assisted predictive vulnerability platform engineered for the coastal district of Puri, Odisha. It fuses geospatial hydrology with LLM orchestration to generate localized, actionable early warnings for municipal authorities.

⚠️ LIVE DEMO NOTICE: RENDER FREE TIER
The FastAPI computation engine is deployed on Render's free tier, which spins down after 15 minutes of inactivity. When you trigger your first storm scenario, the backend may take 50–60 seconds to wake up. Please be patient. Once the engine is awake, the NDJSON stream will populate the map in real-time.


### Architecture & Workflow
This system is built for speed & responsiveness, deliberately bypassing computationally heavy hydrodynamic simulations (like ADCIRC) to deliver a 72-hour rapid-response engine.

1. Parametric Hazard Approximation:
- Storm Surge: Calculates dynamic inundation polygons using the Holland (1980) parametric vortex model, SRTM 30m DEMs & live wind/pressure vectors.
- Inland Flooding: Maps rainfall-driven flood pathways using D8 flow-direction & flow-accumulation algorithms via PySheds.

2. Live Vulnerability Intersection:
- The engine spatially intersects the dynamic surge & flood layers against critical infrastructure data (hospitals, shelters, arterial roads, power grids) pulled via the OpenStreetMap Overpass API.
- Assets are assigned an exposure_score based on hazard proximity & base criticality weight.

3. LLM Orchestration (Gemini):
- The ranked risk data is streamed to the Gemini 3.8-Flash API.
- Gemini acts as the emergency orchestrator, instantly generating plain-language evacuation & rerouting advisories in both English & Odia.


### Real-World Context & Validation
STORM-GRID is calibrated against IMD best-track data & verified post-disaster damage reports from the catastrophic landfall of Cyclone Fani (2019) in Puri.

While the recent September 23-24, 2026 depression near Kalingapatnam never achieved classified cyclone status, it highlights the urgent, ongoing need for responsive, localized hazard communication platforms scalable across the Bay of Bengal coastline.


The ranked risk data is streamed to the Gemini 1.5-Flash API.

Gemini acts as the emergency orchestrator, instantly generating plain-language evacuation and rerouting advisories in both English and Odia.


### Tech Stack
- Backend Engine: Python 3.13, FastAPI (ASGI Streaming), PySheds, GeoPandas, Rasterio, Shapely, NumPy.
- Frontend Dashboard: React, Vite, Mapbox GL JS.
- AI / Orchestration: Google Gemini API (1.5-Flash).
- Data Sources: Earth Engine (SRTMGL1_003), OpenStreetMap Overpass API.


### Local Development
To run the simulation engine locally:

##### Backend
```Bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Add your Gemini API key
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Start the ASGI server
uvicorn main:app --reload
```

##### Frontend
```Bash
cd frontend
npm install

# Add your Mapbox token
echo "VITE_MAPBOX_TOKEN=your_token_here" > .env

# Start the Vite dev server
npm run dev
```
