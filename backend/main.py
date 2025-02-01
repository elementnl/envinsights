# backend/main.py
from fastapi import FastAPI, HTTPException, Query
import requests
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAQ_URL = "https://api.openaq.org/v3/locations"
API_KEY = os.getenv("OPENAQ_API_KEY")

@app.get("/air_quality")
def get_air_quality(lat: float = Query(..., description="Latitude"), lon: float = Query(..., description="Longitude"), radius: int = Query(12000, description="Radius in meters (max: 25000)"), limit: int = Query(100, description="Limit of results")):
    if radius <= 0 or radius > 25000:
        raise HTTPException(status_code=422, detail="Radius must be between 1 and 25000 meters.")
    
    headers = {"X-API-Key": API_KEY}
    params = {"coordinates": f"{lon},{lat}", "radius": radius, "limit": limit}
    response = requests.get(OPENAQ_URL, headers=headers, params=params)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from OpenAQ API")
    
    response_json = response.json()
    if "results" not in response_json or not response_json["results"]:
        return {"message": "No air quality data available."}
    
    data = []
    for item in response_json["results"]:
        avg_pm25 = next((sensor["value"] for sensor in item.get("sensors", []) if sensor["parameter"]["name"] == "pm25"), None)
        if avg_pm25 is not None:
            avg_pm25 = float(avg_pm25)  # Ensure it's a float value
            data.append({
                "id": item["id"],
                "name": item["name"],
                "locality": item.get("locality", "Unknown"),
                "country": item["country"]["name"],
                "latitude": item["coordinates"]["latitude"],
                "longitude": item["coordinates"]["longitude"],
                "pm25": avg_pm25,
                "color": get_air_quality_color(avg_pm25)
            })
    
    return data


def get_air_quality_color(pm25_value):
    if pm25_value <= 12:
        return "#00FF00"  # Green (Good)
    elif pm25_value <= 35:
        return "#FFFF00"  # Yellow (Moderate)
    elif pm25_value <= 55:
        return "#FFA500"  # Orange (Unhealthy for Sensitive Groups)
    elif pm25_value <= 150:
        return "#FF0000"  # Red (Unhealthy)
    else:
        return "#800080"  # Purple (Hazardous)
