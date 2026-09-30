// App.jsx


import {useCallback, useEffect, useMemo, useRef, useState} from 'react'
import Map, {Layer, Source} from 'react-map-gl'

import 'mapbox-gl/dist/mapbox-gl.css'


const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN


export default function App() {

    const [stormParams, setStormParams] = useState({lat: 19.8134, lon: 85.8312, wind_kph: 180, pressure_mb: 940})
    const [surgeData, setSurgeData] = useState(null)
    const [flowData, setFlowData] = useState(null)
    const [atRiskAssets, setAtRiskAssets] = useState(null)
    const [advisories, setAdvisories] = useState(null)
    
    // New state for step-by-step UI
    const [progressStatus, setProgressStatus] = useState("Initializing models...")
    const [isCalculating, setIsCalculating] = useState(false)
    
    const abortControllerRef = useRef(null)

    const triggerEngine = useCallback(async () => {
        if (abortControllerRef.current) abortControllerRef.current.abort()
        
        abortControllerRef.current = new AbortController()

        setIsCalculating(true)
        setAdvisories(null);

        try {
            const response = await fetch('http://localhost:8000/api/forecast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(stormParams),
                signal: abortControllerRef.current.signal
            })
            
            if (!response.ok) throw new Error("We couldn't connect to the server to run the simulation.")
            
            const reader = response.body.getReader()
            
            const decoder = new TextDecoder()
            
            let buffer = '' // Initialize the fragment buffer

            while (true) {
                const {value, done} = await reader.read()
                if (done) break
                
                // Append new data to the leftover buffer
                buffer += decoder.decode(value, {stream: true})
                
                const lines = buffer.split("\n")
                
                // Pop the last element (which is likely incomplete) and keep it in the buffer
                buffer = lines.pop();
                
                for (const line of lines) {
                    if (line.trim() === '') continue
                    
                    try {
                        const parsed = JSON.parse(line)
                        setProgressStatus(parsed.status)
                        
                        if (parsed.partial_data) {
                            setFlowData(parsed.partial_data.flow)
                            setSurgeData(parsed.partial_data.surge)
                            setAtRiskAssets(parsed.partial_data.assets)
                        }
                        
                        if (parsed.status === 'COMPLETE') {
                            setAdvisories(parsed.final_data)
                            setIsCalculating(false)
                        }
                    } catch (e) {
                        console.error("Buffer parsing wait...", e)
                    }
                }
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log("Previous request cancelled by new input.")
            } else {
                console.error("Simulation failed:", error)
                
                setProgressStatus("Connection lost. Please try again.")
                setIsCalculating(false)
            }
        }
    }, [stormParams])

    useEffect(() => {triggerEngine()}, [triggerEngine])

    const handleSliderChange = (e) => {
        const {name, value} = e.target
        
        setStormParams(prev => ({...prev, [name]: parseFloat(value)}))
    }

    const assetsGeoJSON = useMemo(() => {
        if (!atRiskAssets) return null

        return {

            type: 'FeatureCollection',
            features: atRiskAssets.map(asset => ({
                type: 'Feature',
                geometry: {type: 'Point', coordinates: [asset.lon, asset.lat]},
                properties: {...asset}
            }))
        
        }
    }, [atRiskAssets])

    return (

        <div className = "flex h-screen w-full bg-neutral-950 text-white font-mono">
            
            <div className = "w-100 p-6 border-r border-neutral-800 flex flex-col gap-6 z-10 bg-neutral-950 shadow-2xl overflow-y-auto">
                <h1 className = "text-xl font-bold tracking-widest uppercase text-neutral-100">
                    Puri Command Center
                </h1>
                
                <div className = "flex flex-col gap-4 bg-neutral-900 p-4 border border-neutral-800">
                    <h2 className = "text-xs text-neutral-500 tracking-wider">
                        STORM VECTORS
                    </h2>

                    <label className = "flex flex-col text-sm text-neutral-300">
                        Sustained Winds:
                        
                        <span className = "font-bold text-white">
                            {stormParams.wind_kph} km/h
                        </span>
                        
                        <input
                            type = 'range'
                            name = 'wind_kph'
                            min = '50'
                            max = '300'
                            step = '5'
                            value = {stormParams.wind_kph}
                            onChange = {handleSliderChange}
                            onMouseUp = {triggerEngine}
                            className = "mt-2 accent-red-600"
                        />
                    </label>

                    <label className = "flex flex-col text-sm text-neutral-300">
                        Central Pressure:
                        
                        <span className = "font-bold text-white">
                            {stormParams.pressure_mb} mb
                        </span>

                        <input
                            type = 'range'
                            name = 'pressure_mb'
                            min = '900'
                            max = '1010'
                            step = '1'
                            value = {stormParams.pressure_mb}
                            onChange = {handleSliderChange}
                            onMouseUp = {triggerEngine}
                            className="mt-2 accent-red-600"
                        />
                    </label>
                </div>

                <div className = "flex flex-col gap-4 mt-4">
                    <h2 className = "text-sm font-semibold border-b border-neutral-800 pb-2 text-neutral-400">
                        Active Warnings
                    </h2>
                    
                    {/* Live Progress Tracker */}
                    {isCalculating ? (
                        <div className = "text-yellow-500 animate-pulse text-sm border border-yellow-900 bg-yellow-900/20 p-3">
                            {progressStatus}
                        </div>
                    ) : advisories ? (
                        <div
                            className = {`
                                p-4 border-2
                                ${['TIMEOUT', 'OFFLINE', 'OVERLOADED', 'PARSE_ERROR'].includes(advisories.severity_level)
                                    ? "bg-neutral-800 border-neutral-600 text-neutral-300"
                                    : advisories.severity_level === 'CRITICAL'
                                        ? "bg-red-600 border-red-900 text-white"
                                        : "bg-yellow-500 border-yellow-700 text-black"
                                }
                            `}
                        >
                            <h3 className = "font-bold text-lg mb-2 underline underline-offset-4">
                                LEVEL: {advisories.severity_level}
                            </h3>
                            
                            <p className = "text-sm mb-4 leading-relaxed">
                                {advisories.advisory_text_en}
                            </p>
                            
                            <div className = "bg-white text-black p-3 text-sm font-sans shadow-inner">
                                <span className = "font-bold block mb-1 text-neutral-500 text-[10px] tracking-wider uppercase">
                                    Odia Translation
                                </span>

                                {advisories.advisory_text_or || advisories.advisory_text_od}
                            </div>
                        </div>
                    ) : (
                        <div className = "text-neutral-600 text-sm">
                            No active threats detected.
                        </div>
                    )}
                </div>
            </div>

            <div className = "flex-1 relative bg-neutral-900">
                <Map
                    initialViewState = {{longitude: 85.8312, latitude: 19.8134, zoom: 10}}
                    mapStyle = "mapbox://styles/mapbox/dark-v11"
                    mapboxAccessToken = {MAPBOX_TOKEN}
                >
                    {surgeData && (
                        <Source
                            id = 'dynamic-surge'
                            type = 'geojson'
                            data = {surgeData}
                        >
                            <Layer
                                id = 'surge-fill'
                                type = 'fill'
                                paint = {{'fill-color': '#ff0000', 'fill-opacity': 0.3}}
                            />
                        </Source>
                    )}

                    {flowData && (
                        <Source
                            id = 'flood-pathways'
                            type = 'geojson'
                            data = {flowData}
                        >
                            <Layer
                                id = 'flood-lines'
                                type = 'line'
                                paint = {{'line-color': '#3b82f6', 'line-width': 2, 'line-opacity': 0.8}}
                            />
                        </Source>
                    )}

                    {assetsGeoJSON && (
                        <Source
                            id = 'at-risk-assets'
                            type = 'geojson'
                            data = {assetsGeoJSON}
                        >
                            <Layer
                                id = 'asset-points'
                                type = 'circle'
                                paint = {{
                                    'circle-radius': 6,
                                    'circle-color': ['step', ['get', 'exposure_score'], '#fbbf24', 0.5, '#f97316', 0.8, '#dc2626'],
                                    'circle-stroke-width': 1,
                                    'circle-stroke-color': '#ffffff'
                                }}
                            />
                        </Source>
                    )}
                </Map>
            </div>
        </div>

    )

}
