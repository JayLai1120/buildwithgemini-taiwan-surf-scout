"""Google Maps Platform tools: Geocoding and Places API (New).

API key is read from GOOGLE_MAPS_API_KEY environment variable.
"""

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional


def get_maps_api_key() -> str:
    """Read Google Maps API key from environment."""
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY is not set in environment or .env file.")
    return key


def geocode_address(address: str) -> Dict[str, Any]:
    """Turn an address or landmark name into geographical coordinates (latitude and longitude).

    Args:
        address: The street address, city, or landmark to geocode (e.g. 'Eiffel Tower, Paris', 'Kinkaku-ji, Kyoto').

    Returns:
        A dictionary with formatted address, latitude, longitude, and place_id.
    """
    api_key = get_maps_api_key()
    encoded_address = urllib.parse.quote(address.strip())
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "travel-agent/1.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("status") != "OK" or not data.get("results"):
                return {"error": f"Geocoding failed for '{address}': {data.get('status')}"}

            first = data["results"][0]
            loc = first["geometry"]["location"]
            return {
                "address": address,
                "formatted_address": first.get("formatted_address"),
                "latitude": loc.get("lat"),
                "longitude": loc.get("lng"),
                "place_id": first.get("place_id"),
            }
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 1000.0,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """Find nearby places of a specific type using the Places API (New) searchNearby endpoint.

    Args:
        latitude: Latitude coordinate of the search center.
        longitude: Longitude coordinate of the search center.
        place_type: Type of place to search for (e.g. 'tourist_attraction', 'restaurant', 'cafe', 'museum', 'hotel', 'park').
        radius_meters: Radius around the center point in meters (default 1000.0).
        max_results: Maximum number of places to return (default 5, up to 20).

    Returns:
        A list of place dictionaries containing name, address, and coordinates location.
    """
    api_key = get_maps_api_key()
    url = "https://places.googleapis.com/v1/places:searchNearby"

    payload = {
        "includedTypes": [place_type.strip()],
        "maxResultCount": min(max_results, 20),
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": float(radius_meters),
            }
        },
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        "User-Agent": "travel-agent/1.0",
    }

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
            places = data.get("places", [])
            results = []
            for p in places:
                display_name = p.get("displayName", {}).get("text", "")
                address = p.get("formattedAddress", "")
                location = p.get("location", {})
                results.append({
                    "name": display_name,
                    "address": address,
                    "location": {
                        "latitude": location.get("latitude"),
                        "longitude": location.get("longitude"),
                    },
                })
            return results
    except Exception as e:
        return [{"error": f"Nearby search failed: {str(e)}"}]
