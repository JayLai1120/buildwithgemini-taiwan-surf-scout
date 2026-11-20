"""Firestore backend tools for Taiwan surf spots and surf session logs.

Project ID is hardcoded as required for Agent Platform compatibility.
"""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-a1008e70ae07"

_db: Optional[firestore.Client] = None

def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project=PROJECT_ID)
    return _db


def list_surf_spots(county: Optional[str] = None) -> List[Dict[str, Any]]:
    """List surf spots from the catalog, optionally filtered by county.

    Args:
        county: Optional county or region filter (e.g. '苗栗', '台中', '苗栗縣竹南鎮', '大安').

    Returns:
        A list of surf spot dictionaries with details including name, county, seabed, optimal wind and tide.
    """
    db = get_db()
    collection = db.collection("surf_spots")
    docs = collection.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        if county:
            spot_county = data.get("county", "")
            spot_region = data.get("region", "")
            if county not in spot_county and county not in spot_region:
                continue
        results.append(data)
    return results


def get_surf_spot_details(spot_id: str) -> Dict[str, Any]:
    """Get complete details for a specific surf spot by ID.

    Args:
        spot_id: The unique identifier of the surf spot (e.g. 'zhunan-holiday-forest', 'songbo-port', 'waipu-port').

    Returns:
        A dictionary with full spot specifications, or an error message if not found.
    """
    db = get_db()
    doc_ref = db.collection("surf_spots").document(spot_id)
    doc = doc_ref.get()
    if not doc.exists:
        return {"error": f"Surf spot with ID '{spot_id}' not found."}
    return doc.to_dict()


def save_surf_session_log(
    surfer_name: str,
    spot_id: str,
    board_used: str,
    wave_notes: str,
    rating: int = 5,
) -> Dict[str, Any]:
    """Save a surf session log or personal field review for a spot.

    Args:
        surfer_name: Name or nickname of the surfer.
        spot_id: Surf spot ID where the session took place (e.g. 'zhunan-holiday-forest', 'songbo-port', 'waipu-port').
        board_used: Surfboard used (e.g. '9.2 Single Fin Longboard', '6.0 Fish', 'Shortboard').
        wave_notes: Wave observation notes (e.g. 'Clean waist-to-chest waves around low tide incoming, light offshore wind').
        rating: Rating of wave quality from 1 to 5 (default 5).

    Returns:
        A status dictionary confirming the log has been recorded into Firestore.
    """
    db = get_db()
    logs_ref = db.collection("surf_session_logs")
    new_doc = logs_ref.document()
    data = {
        "surfer_name": surfer_name,
        "spot_id": spot_id,
        "board_used": board_used,
        "wave_notes": wave_notes,
        "rating": rating,
    }
    new_doc.set(data)
    return {"status": "saved", "log_id": new_doc.id, "data": data}


def evaluate_surf_conditions(
    spot_id: str,
    wind_direction_degrees: float,
    wind_speed_knots: float,
    current_tide_stage: str = "incoming",
) -> Dict[str, Any]:
    """Evaluate wave cleanliness and offshore wind suitability score for a Taiwan west coast surf spot.

    Args:
        spot_id: Surf spot ID ('zhunan-holiday-forest', 'songbo-port', or 'waipu-port').
        wind_direction_degrees: Wind direction in degrees (0=North, 90=East/offshore, 180=South, 270=West/onshore).
        wind_speed_knots: Wind speed in knots (1 knot ~= 1.85 km/h).
        current_tide_stage: Current tide status: 'low_incoming', 'incoming', 'high', 'outgoing', or 'low'.

    Returns:
        A dictionary with offshore wind status, surface cleanliness level, suitability score (0-100), and practical advice.
    """
    spot = get_surf_spot_details(spot_id)
    if "error" in spot:
        return spot

    spot_orientations = {
        "zhunan-holiday-forest": {"beach_facing_deg": 270, "has_jetty_shelter": False},
        "songbo-port": {"beach_facing_deg": 260, "has_jetty_shelter": True},
        "waipu-port": {"beach_facing_deg": 280, "has_jetty_shelter": True},
    }
    config = spot_orientations.get(spot_id, {"beach_facing_deg": 270, "has_jetty_shelter": False})
    beach_facing = config["beach_facing_deg"]

    diff = abs((wind_direction_degrees - beach_facing + 180) % 360 - 180)

    if diff > 135:
        wind_type = "離岸風 (Offshore)"
        base_score = 90
    elif diff > 90:
        wind_type = "側離岸風 (Cross-Offshore)"
        base_score = 75
    elif diff > 45:
        wind_type = "側陸風 (Cross-Onshore)"
        base_score = 50
    else:
        wind_type = "迎風/陸風 (Direct Onshore)"
        base_score = 30

    if config["has_jetty_shelter"] and (315 <= wind_direction_degrees or wind_direction_degrees <= 60):
        base_score += 15
        shelter_note = "受防波堤遮蔽，北側東北季風被有效阻擋。"
    else:
        shelter_note = "無防波堤遮蔽，完全受風向影響。"

    if wind_speed_knots < 8:
        cleanliness = "鏡面微風 (Glassy/Clean)"
        base_score += 10
    elif wind_speed_knots < 15:
        cleanliness = "微浪碎屑 (Light Chop / Fair)"
    elif wind_speed_knots < 22:
        cleanliness = "水面雜亂 (Chop / Bumpy)"
        base_score -= 15
    else:
        cleanliness = "風暴吹亂 (Blown Out)"
        base_score -= 30

    if "incoming" in current_tide_stage.lower() or "low" in current_tide_stage.lower():
        tide_fit = "潮水狀態良好（符合西海岸乾潮反漲起浪黃金窗口）"
        base_score += 5
    else:
        tide_fit = "滿潮水深，浪壁可能偏厚或貼壁"
        base_score -= 10

    score = max(0, min(100, int(base_score)))

    return {
        "spot_name": spot.get("name"),
        "score": score,
        "wind_type": wind_type,
        "wind_speed_knots": wind_speed_knots,
        "cleanliness": cleanliness,
        "shelter_status": shelter_note,
        "tide_assessment": tide_fit,
        "recommendation": (
            "強烈推薦下水！浪面乾淨，離岸風推力佳。" if score >= 80 else
            "值得下水，注意風力調節與板型選擇。" if score >= 60 else
            "浪況較為雜亂，建議選擇防波堤避風側或等待風向轉東。"
        ),
    }


def fetch_live_marine_wave_data(spot_id: str) -> Dict[str, Any]:
    """Fetch real-time live marine wave and ocean conditions for a Taiwan surf spot via Open-Meteo Marine API.

    Args:
        spot_id: The surf spot ID (e.g. 'zhunan-holiday-forest', 'songbo-port', 'waipu-port').

    Returns:
        A dictionary with live wave height in meters, wave direction, wave period in seconds, and wind wave height.
    """
    import json
    import urllib.request

    spot = get_surf_spot_details(spot_id)
    if "error" in spot:
        return spot

    coords = spot.get("coordinates", {})
    lat = coords.get("latitude", 24.6972)
    lng = coords.get("longitude", 120.8524)

    url = (
        f"https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={lat}&longitude={lng}"
        f"&current=wave_height,wave_direction,wave_period,wind_wave_height"
        f"&timezone=Asia%2FTaipei"
    )

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "taiwan-surf-scout/1.0"})
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))
            current = data.get("current", {})
            return {
                "spot_name": spot.get("name"),
                "observation_time": current.get("time"),
                "wave_height_meters": current.get("wave_height"),
                "wave_period_seconds": current.get("wave_period"),
                "wave_direction_degrees": current.get("wave_direction"),
                "wind_wave_height_meters": current.get("wind_wave_height"),
            }
    except Exception as e:
        return {"error": f"Failed to fetch live marine wave data: {str(e)}"}


SURF_ASSETS_BUCKET = "taiwan-surf-scout-assets-qwiklabs-gcp-03-a1008e70ae07"


async def generate_surf_spot_image(
    prompt: str,
    spot_id: str,
    tool_context: Any = None,
) -> Dict[str, Any]:
    """Generate a photo or artistic visual of a Taiwan surf spot, wave condition, or surfboard gear.

    Args:
        prompt: Detailed description of the image to generate (e.g. 'A surfer gliding on a stylish longboard at sunset over Zhunan Holiday Forest, clear clean peeling waves').
        spot_id: Related surf spot ID ('zhunan-holiday-forest', 'songbo-port', 'waipu-port', or 'general').

    Returns:
        A dictionary containing the public image URL from Cloud Storage, artifact filename, and status.
    """
    import uuid
    from google import genai
    from google.genai import types
    from google.genai.types import Part
    from google.cloud import storage

    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    full_prompt = f"Taiwan coastal surf culture: {prompt}. Beautiful ocean lighting, waves, authentic surfing vibe."

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(aspect_ratio="1:1", image_size="1K"),
        ),
    )

    image_bytes = None
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            break

    if not image_bytes:
        return {"error": "Failed to generate image bytes from model."}

    file_id = uuid.uuid4().hex[:8]
    filename = f"surf_{spot_id}_{file_id}.png"

    # 1. Save artifact in Playground Artifacts panel
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = Part.from_bytes(data=image_bytes, mime_type="image/png")
            await tool_context.save_artifact(filename, artifact_part)
        except Exception as e:
            print(f"Warning: tool_context.save_artifact failed: {e}")

    # 2. Upload same bytes directly to public GCS bucket (no local file)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(SURF_ASSETS_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/png")

    public_url = f"https://storage.googleapis.com/{SURF_ASSETS_BUCKET}/{filename}"

    return {
        "status": "success",
        "prompt": prompt,
        "spot_id": spot_id,
        "artifact_filename": filename,
        "public_image_url": public_url,
    }


async def generate_surf_spot_video(
    prompt: str,
    spot_id: str,
    tool_context: Any = None,
) -> Dict[str, Any]:
    """Generate a short video for a Taiwan surf spot or wave condition using Google Omni model.

    Args:
        prompt: Detailed description of the video to generate (e.g. 'A 3-second cinematic clip of waves breaking cleanly at sunset over Zhunan Holiday Forest, surfers paddling into peelers').
        spot_id: Related surf spot ID ('zhunan-holiday-forest', 'songbo-port', 'waipu-port', or 'general').
        tool_context: ToolContext for saving the video artifact to the Playground Artifacts panel.

    Returns:
        A dictionary containing the public video URL from Cloud Storage, artifact filename, and status.
    """
    import base64
    import uuid
    from google import genai
    from google.genai.types import Part
    from google.cloud import storage

    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")

    full_prompt = (
        f"A short video of Taiwan surf spot {spot_id}: {prompt}. "
        "Dynamic ocean waves, authentic coastal atmosphere, natural sunlight, cinematic motion."
    )

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=full_prompt,
    )

    video_bytes = None

    # Extract video from interaction outputs
    output_video = getattr(interaction, "output_video", None)
    if output_video and getattr(output_video, "data", None):
        video_bytes = base64.b64decode(output_video.data)
    elif hasattr(interaction, "steps") and interaction.steps:
        for step in reversed(interaction.steps):
            content = getattr(step, "content", None) or []
            for item in content:
                item_type = getattr(item, "type", None) or (item.get("type") if isinstance(item, dict) else None)
                if item_type == "video":
                    data = getattr(item, "data", None) or (item.get("data") if isinstance(item, dict) else None)
                    if data:
                        video_bytes = base64.b64decode(data)
                        break
            if video_bytes:
                break

    if not video_bytes:
        return {"error": "Failed to generate video bytes from Omni model."}

    file_id = uuid.uuid4().hex[:8]
    filename = f"surf_{spot_id}_{file_id}.mp4"

    # 1. Save artifact in Playground Artifacts panel
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = Part.from_bytes(data=video_bytes, mime_type="video/mp4")
            await tool_context.save_artifact(filename, artifact_part)
        except Exception as e:
            print(f"Warning: tool_context.save_artifact failed: {e}")

    # 2. Upload same bytes directly to public GCS bucket (no local file)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(SURF_ASSETS_BUCKET)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{SURF_ASSETS_BUCKET}/{filename}"

    return {
        "status": "success",
        "prompt": prompt,
        "spot_id": spot_id,
        "artifact_filename": filename,
        "public_video_url": public_url,
    }




