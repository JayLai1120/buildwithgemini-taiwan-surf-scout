#!/usr/bin/env python3
"""Seed script for Taiwan West Coast surf spots catalog."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-a1008e70ae07"

WEST_COAST_SURF_SPOTS = [
    {
        "id": "zhunan-holiday-forest",
        "name": "竹南假日之森 (Zhunan Holiday Forest)",
        "county": "苗栗縣竹南鎮",
        "region": "苗栗西海岸",
        "coordinates": {"latitude": 24.6972, "longitude": 120.8524},
        "seabed": "沙灘沙洲 (Sandbar Beachbreak)",
        "best_wind": "東風、東南風（離岸風）或微弱東北風",
        "best_tide": "乾潮轉漲潮（低潮反漲）",
        "optimal_tide_stage": "low_to_mid_incoming",
        "suitable_boards": ["長板", "短板", "風箏衝浪"],
        "difficulty": "初級~進階",
        "features": "台灣西海岸衝浪精神地標，沙洲變化豐富，浪小順風時長板極順，冬季東北季風減弱或轉東南離岸風時起浪絕佳，背靠防風林。",
        "hazards": ["強勁沿岸流 (Rip current)", "冬季強風吹亂水面"]
    },
    {
        "id": "songbo-port",
        "name": "松柏港北堤 (Songbo Port)",
        "county": "台中市大安區",
        "region": "台中西海岸",
        "coordinates": {"latitude": 24.4285, "longitude": 120.5752},
        "seabed": "沙灘混消波塊 (Jetty Beachbreak)",
        "best_wind": "東北風（北堤擋風）、東風（離岸風）",
        "best_tide": "退潮中段至乾潮底反漲",
        "optimal_tide_stage": "mid_to_low_incoming",
        "suitable_boards": ["長板", "中長板 (Mid-length)", "短板"],
        "difficulty": "初級~中級",
        "features": "中部冬天最指標避風浪點，北堤有效遮蔽強烈東北季風，退潮至乾潮底反漲時浪型開口最順，滿潮時浪貼波堤易敲壁反彈。",
        "hazards": ["堤防消波塊 (Tetrapods)", "滿潮反彈浪 (Backwash)"]
    },
    {
        "id": "waipu-port",
        "name": "外埔漁港沙灘 (Waipu Port)",
        "county": "苗栗縣後龍鎮",
        "region": "苗栗西海岸",
        "coordinates": {"latitude": 24.6214, "longitude": 120.7718},
        "seabed": "平緩沙質底 (Mellow Sandbreak)",
        "best_wind": "偏東風（離岸風）、北向微風",
        "best_tide": "乾潮至乾潮剛轉漲潮 (低潮區間)",
        "optimal_tide_stage": "low_incoming",
        "suitable_boards": ["長板", "復古雙舵 (Fish)"],
        "difficulty": "初級~中級",
        "features": "起浪平緩溫厚，適合長板輕鬆走板滑行，極度吃潮水，滿潮時水深幾乎無浪，乾潮時沙洲現出形狀最漂亮。",
        "hazards": ["滿潮水深無浪", "港區出入口船隻動線"]
    }
]

def seed():
    print(f"Connecting to Firestore with hardcoded project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection = db.collection("surf_spots")
    
    for spot in WEST_COAST_SURF_SPOTS:
        doc_id = spot["id"]
        doc_ref = collection.document(doc_id)
        doc_ref.set(spot)
        print(f"Seeded surf spot: {spot['name']} (ID: {doc_id})")

    print("\nFirestore seeding complete! Verifying count...")
    docs = list(collection.stream())
    print(f"Total surf spots in Firestore: {len(docs)}")

if __name__ == "__main__":
    seed()
