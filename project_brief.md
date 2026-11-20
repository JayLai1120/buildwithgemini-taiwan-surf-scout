# My agent: taiwan-surf-scout
One-liner: A conversational agent that helps Taiwan west-coast surfers find optimal surf sessions by analyzing live wind directions, tides, and spot characteristics (including Zhunan Holiday Forest, Songbo Port, and Waipu Port).

Tool coverage:
- Memory: Surfer's home base, skill level, quiver (longboard/mid-length/shortboard), wind tolerance
- Tools: Query west coast surf spots in Firestore, fetch live wind and tide conditions, calculate wave cleanliness & offshore wind score, save surf session notes
- Catalog/UI: Catalog of Taiwan west coast surf spots (Zhunan Holiday Forest, Songbo Port, Waipu Port) with seabed type, optimal tide, and shelter effects, rendered as A2UI cards
- Image gen: Spot wave preview illustrations and surf session log postcards
- Sandbox: Angle calculation between winter NE monsoon vs. beach/jetty shelter orientation to score wave cleanliness

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Wind & tide suitability score algorithm, CWA coastal observation data
