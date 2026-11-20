# Taiwan Surf Scout (台灣西海岸衝浪探路員) 🏄‍♂️🌊

An intelligent, agent-first travel concierge and wave forecasting assistant tailored for Taiwan west-coast surfers. Built on Google Agent Development Kit (ADK) and deployed to Vertex AI Agent Runtime, **Taiwan Surf Scout** analyzes coastal bathymetry, real-time marine metrics, offshore wind windows, and tide cycles to help surfers pick the best spots and log their surf sessions.

---

## 🌟 Capabilities & Features

Based strictly on the codebase implementation:

- 🧠 **Cross-Session Memory Bank**: Remembers surfer facts, quiver specifications (longboard, mid-length, shortboard), home base, skill level, and safety/allergy considerations across distinct chat sessions using Google Cloud Vertex AI Memory Bank (`PreloadMemoryTool` + automatic session fact extraction callback).
- 🗄️ **Firestore Catalog & Session Storage**:
  - Catalogs Taiwan west-coast spots (e.g., Zhunan Holiday Forest 竹南假日之森, Songbo Port 松柏港北堤, Waipu Port 外埔漁港沙灘) with coordinates, seabed type, shelter characteristics, and optimal tide windows.
  - Persists field reviews and session journals with board choice, wave ratings, and notes directly into Google Cloud Firestore.
- 🌊 **Real-Time Marine Wave Data**: Queries live oceanic metrics (significant wave height, wave period, wave direction, and wind wave height) via Open-Meteo Marine API.
- 🌬️ **Wave Cleanliness & Offshore Wind Scoring**: Proprietary evaluation model calculating wave cleanliness, jetty shelter effects against winter NE monsoons, and tide suitability scores (0–100 scale).
- 🎨 **Spot Visual & Postcard Generation**: Generates scenic surf spot artwork and session postcards using Google Gemini on Vertex AI (`location="global"`), saving images as session artifacts and serving them via Google Cloud Storage.
- 🎬 **AI Video Generation**: Produces dynamic 3-second spot wave clips using Google's Omni model (`gemini-omni-flash-preview` in `global` region), saved as artifacts and uploaded to Google Cloud Storage.
- 🗺️ **Google Maps Integration**: Geocodes locations and discovers nearby surf rental shops, beach showers, and dining amenities using Google Maps Platform Geocoding and Places API.
- 🧪 **Cloud Code Sandbox Execution**: Securely runs Python code snippets and mathematical models within an isolated Google Agent Engine Code Sandbox environment.
- 🪟 **Agent-to-User Interface (A2UI)**: Renders structured UI cards, columns, tabular comparison rows, badges, and media previews directly in both the ADK Web Playground and the custom chat web client.

> **Note on planned features**: Real-time integration with Central Weather Administration (CWA) coastal radar stations was planned in `project_brief.md`, but is currently marked as **planned, not yet implemented** (Open-Meteo Marine API is currently used for live wave metrics).

---

## 🏗️ Architecture & Google Cloud Services

| Layer | Service / Technology | Implementation in Repo |
|---|---|---|
| **Agent Reasoning Engine** | Google ADK (`google-adk`), Gemini 2.5 Flash (`gemini-2.5-flash`) | [`app/agent.py`](app/agent.py) |
| **Long-Term Memory** | Vertex AI Memory Bank (`VertexAiMemoryBankService`) | Agent ID `2698420337376231424` (`PreloadMemoryTool`) |
| **Database & Records** | Google Cloud Firestore (Native Mode) | Collections: `surf_spots`, `surf_session_logs` ([`app/tools_firestore.py`](app/tools_firestore.py)) |
| **Blob / Asset Storage** | Google Cloud Storage (GCS) | Public asset bucket for generated images & videos |
| **Image & Video Generation** | Vertex AI GenAI (`gemini-2.5-flash` / `gemini-omni-flash-preview`) | Tools in [`app/tools_firestore.py`](app/tools_firestore.py) |
| **Location Services** | Google Maps Platform (Geocoding & Places API) | [`app/tools_maps.py`](app/tools_maps.py) |
| **Secure Code Sandbox** | Vertex AI Agent Engine Sandbox Environment | `AgentEngineSandboxCodeExecutor` |
| **Rich Card UI** | A2UI (Agent to UI, Schema v0.8 Basic Catalog) | [`app/a2ui_utils.py`](app/a2ui_utils.py) & frontend renderer |
| **Chat Frontend** | FastAPI + A2A SDK client | [`frontend/main.py`](frontend/main.py) + [`frontend/static/index.html`](frontend/static/index.html) |
| **Deployment Target** | Vertex AI Agent Engine / Agent Runtime | Deployed via `agents-cli deploy` (A2A Protocol) |

---

## 🧰 Implemented Agent Tools

The `root_agent` is equipped with the following ADK tools:

1. `PreloadMemoryTool`: Injects relevant user preferences and past surfing profile facts at the start of each turn.
2. `list_surf_spots`: Lists indexed surf spots from Firestore, with optional county/region filtering.
3. `get_surf_spot_details`: Retrieves deep technical details for a specific spot ID.
4. `fetch_live_marine_wave_data`: Fetches real-time wave height, period, and direction.
5. `evaluate_surf_conditions`: Analyzes local wind angle, beach orientation, speed, and tide level to produce an actionable 0–100 suitability score.
6. `generate_surf_spot_image`: Synthesizes surf spot illustrations and postcards, saving artifacts to Cloud Storage.
7. `generate_surf_spot_video`: Synthesizes short coastal surf video clips using `gemini-omni-flash-preview`.
8. `save_surf_session_log`: Records user surf logs, board models, ratings, and notes into Firestore.
9. `geocode_address`: Converts coastal locations or landmarks into GPS coordinates.
10. `find_nearby_places`: Finds nearby attractions, surf shops, and services.
11. `get_current_time`: Provides localized time and timezone calculations.

---

## 🚀 Getting Started & Local Setup

### Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager
- [`google-agents-cli`](https://google.github.io/agents-cli/): `uv tool install google-agents-cli`
- Google Cloud SDK (`gcloud`) authenticated to your GCP project:
  ```bash
  gcloud auth login
  gcloud auth application-default login
  gcloud config set project <YOUR_PROJECT_ID>
  ```

### Environment Configuration

Create a `.env` file in the project directory (or copy from `.env.example`):

```bash
GOOGLE_MAPS_API_KEY=your_maps_key
```

### 1. Running Locally via ADK Playground

To test the agent locally with memory service and live reload enabled:

```bash
# Install dependencies
uv sync

# Launch the ADK Playground
agents-cli playground
```

Or run with the ADK CLI directly:

```bash
uv run adk web . --port 8080 --reload_agents
```

### 2. Running the Custom Chat Frontend

The project includes a standalone FastAPI chat proxy that communicates with the deployed agent over the Agent-to-Agent (A2A) protocol and renders A2UI cards natively:

```bash
cd frontend

# Install frontend dependencies
pip install -r requirements.txt

# Run the frontend server
export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_NUM>/locations/<REGION>/reasoningEngines/<ENGINE_ID>"
export AGENT_DIRECTORY="app"
python main.py
```

### 3. Deploying to Vertex AI Agent Runtime

To deploy or update the agent on Google Cloud Vertex AI Agent Runtime:

```bash
agents-cli deploy --project <YOUR_PROJECT_ID> --no-confirm-project
```
