// App.jsx


import {useEffect, useState} from 'react'
import Map, {Layer, Marker, Source} from 'react-map-gl'

import axios from 'axios'

import 'mapbox-gl/dist/mapbox-gl.css'


const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN


export default function App() {
    
    const [surgeData, setSurgeData] = useState(null)
    const [advisory, setAdvisory] = useState(null)
    const [assets, setAssets] = useState([])

    useEffect(() => {
        axios.get('http://localhost:8000/api/hazards/surge').then(res => setSurgeData(res.data)).catch(err => console.error("Failed to load surge data", err))
        axios.get('http://localhost:8000/api/advisories').then(res => {
            if (res.data && res.data.length > 0) setAdvisory(res.data[0])
        }).catch(err => console.error("Failed to load advisories", err))
        axios.get('http://localhost:8000/api/vulnerabilities').then(res => setAssets(res.data)).catch(err => console.error("Failed to load assets", err))
    }, [])

    return (

        <div className = "h-screen w-screen flex p-4 gap-4 box-border">
            <div className = "h-full w-1/3 bg-brutal-surface border-4 border-brutal-border shadow-brutal flex flex-col">
                <div className = "bg-brutal-border text-white p-4 font-bold text-xl uppercase tracking-widest">
                    Puri Command Center
                </div>
                
                <div className = "p-6 grow overflow-y-auto">
                    <h2 className = "font-bold text-lg border-b-2 border-brutal-border mb-4 p-2">
                        Active Warnings
                    </h2>

                    {advisory ? (
                        <div className = "border-2 border-brutal-border shadow-brutal-sm p-4 bg-brutal-accent text-white mb-6">
                            <div className = "font-bold text-xl mb-2 underline decoration-4">
                                LEVEL: {advisory.severity_level}
                            </div>

                            <p className = "mb-4 font-mono text-sm leading-relaxed">
                                {advisory.advisory_text_en}
                            </p>

                            <div className = "bg-white text-black p-3 border-2 border-black font-sans text-sm">
                                <span className = "block font-bold mb-1 text-xs text-gray-500 uppercase">
                                    Odia Translation
                                </span>

                                {advisory.advisory_text_od}
                            </div>
                        </div>
                    ) : (
                        <div className = "animate-pulse bg-gray-200 h-32 border-2 border-dashed border-gray-400 flex items-center justify-center">
                            Awaiting Response...
                        </div>
                    )}
                </div>
            </div>

            <div className = "h-full w-2/3 border-4 border-brutal-border shadow-brutal relative">
                <Map
                    initialViewState = {{longitude: 85.8, latitude: 19.8, zoom: 10}}
                    mapStyle = "mapbox://styles/mapbox/dark-v11"
                    mapboxAccessToken = {MAPBOX_TOKEN}
                >
                    {surgeData && (
                        <Source
                            id = 'surge'
                            type = 'geojson'
                            data = {surgeData}
                        >
                            {assets.map((asset, index) => (
                                <Marker
                                    key = {index}
                                    longitude = {asset.lon || (asset.geometry && asset.geometry.coordinates[0])}
                                    latitude = {asset.lat || (asset.geometry && asset.geometry.coordinates[1])}
                                >
                                    <div
                                        className = "h-4 w-4 bg-yellow-400 border-2 border-brutal-border shadow-brutal-sm cursor-pointer hover:bg-white"
                                        title = {asset.name || "Critical Infra"}
                                    />
                                </Marker>
                            ))}

                            <Layer
                                id = 'surge-layer'
                                type = 'fill'
                                paint = {{'fill-color': '#ff3b3b', 'fill-opacity': 0.4}}
                            />

                            <Layer
                                id = 'surge-outline'
                                type = 'line'
                                paint = {{'line-color': '#ff0000', 'line-width': 2}}
                            />
                        </Source>
                    )}
                </Map>
            </div>
        </div>

    )

}
