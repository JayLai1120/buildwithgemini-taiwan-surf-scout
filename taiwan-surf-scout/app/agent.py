# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types


MODEL = "gemini-3.8-flash"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    q = query.lower()
    if "sf" in q or "san francisco" in q:
        tz_identifier = "America/Los_Angeles"
    elif "taiwan" in q or "taipei" in q or "台灣" in q or "台北" in q or "asia/taipei" in q:
        tz_identifier = "Asia/Taipei"
    else:
        tz_identifier = "Asia/Taipei"

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from app.tools_firestore import (
    evaluate_surf_conditions,
    fetch_live_marine_wave_data,
    generate_surf_spot_image,
    generate_surf_spot_video,
    get_surf_spot_details,
    list_surf_spots,
    save_surf_session_log,
)
from app.tools_maps import find_nearby_places, geocode_address


from google.adk.code_executors import AgentEngineSandboxCodeExecutor

SANDBOX_RESOURCE_NAME = (
    "projects/76412111890/locations/us-east1/reasoningEngines/2698420337376231424/sandboxEnvironments/9110080557751992320"
)

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.memory import VertexAiMemoryBankService

MEMORY_BANK_ID = "2698420337376231424"
PROJECT_ID = "qwiklabs-gcp-03-a1008e70ae07"
LOCATION = "us-east1"


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: after each turn, send the session to Memory Bank for durable facts extraction."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        print(f"Memory extraction notice: {e}")
    return None


def memory_bank_service_builder():
    """Builds VertexAiMemoryBankService for deployed container on Agent Runtime."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog

    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )

    instruction = schema_manager.generate_system_prompt(
        role_description=(
            "You are an expert travel concierge and Taiwan surf scout assistant. "
            "You remember the user's stated preferences, favorite surf spots, surfboards, and facts across conversations. "
            "CRITICAL: Always remember and strictly respect all user allergies, dietary restrictions, and medical safety needs across all conversations. "
            "Help users plan trips, analyze wave and weather conditions, calculate budgets, "
            "look up surf spots, evaluate offshore wind scores, fetch real-time marine wave metrics, "
            "generate scenic posters and short videos, save notes, discover nearby amenities, and safely execute Python code in a secure sandbox when needed. "
            "When the user asks to generate an image, see a photo/visual, or create an illustrated poster/card for a surf spot (e.g. '產生圖片', '畫一張圖', '看照片'), "
            "ALWAYS proactively call the generate_surf_spot_image tool! Once generate_surf_spot_image returns the public_image_url, "
            "render an A2UI Card containing an Image component with that exact public https URL, along with a title Text row, and also provide the image in markdown. "
            "When the user asks to generate a short video or clip for a surf spot (e.g. '產生影片', '生成影片', '看影片', '短片'), "
            "ALWAYS call the generate_surf_spot_video tool! It generates a video using Google Omni model, saves it as an artifact, uploads it to Cloud Storage, and returns the public https video URL. "
            "Present the public video link cleanly to the user and render a Video component in A2UI: {\"Video\": {\"url\": {\"literalString\": \"https://...\"}}}."
        ),
        workflow_description="Analyze the request and return structured UI when appropriate. If image is requested, call generate_surf_spot_image first. If video is requested, call generate_surf_spot_video first.",
        ui_description=(
            "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows or Rows, and optionally ONE Image or Video. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text, Divider, Image, and Video. Do not use "
            "Table or Heading (unsupported in A2UI Basic Catalog), or Buttons, actions, or forms (they do "
            "nothing in adk web). "
            "TABLE / LIST REPRESENTATION: If the user asks for a table, comparison, or spot list, "
            "DO NOT say 'Table is unsupported' and DO NOT output raw text. Instead, build a clean table-like layout using A2UI: "
            "A Card containing a Column, with an h2 Text header, followed by multiple Rows (each Row representing a table row or spot entry with Text items separated by Divider or space). "
            "When generate_surf_spot_image tool returns a public_image_url (starts with https://storage.googleapis.com/), "
            "include an Image component in the A2UI card with url set to that exact https link: "
            "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
            "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
            "not have a public URL, add a short Text line noting the image instead. "
            "When generate_surf_spot_video returns a public_video_url, include a Video component in the A2UI card: "
            "{\"Video\": {\"url\": {\"literalString\": \"https://...\"}}}. "
            "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
            "headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
            "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
        ),
        include_schema=True,
        include_examples=True,
    )
except ImportError:
    from .a2ui_instruction import INSTRUCTION as instruction

from .a2ui_utils import a2ui_callback


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=AgentEngineSandboxCodeExecutor(
        sandbox_resource_name=SANDBOX_RESOURCE_NAME
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        list_surf_spots,
        get_surf_spot_details,
        fetch_live_marine_wave_data,
        evaluate_surf_conditions,
        generate_surf_spot_image,
        generate_surf_spot_video,
        save_surf_session_log,
        geocode_address,
        find_nearby_places,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

