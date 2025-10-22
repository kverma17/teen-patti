# teen-patti
Teen Patti Hand Ranking
========================

Teen Patti - web UI
-------------------

This folder contains a small Flask web app that lets you select 3 cards from a mobile-friendly grid and evaluates the hand using Teen Patti ranking rules.

Quick start
-----------

1. Create a Python 3 virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app:

```bash
python3 app.py
```

3. Open http://127.0.0.1:5000 in your mobile browser or desktop. Tap cards to select/deselect. When 3 cards are selected the server will compute the category and rank and display stats.

Notes
-----
- The backend precomputes all 22,100 hands on startup for fast ranking.
- If you'd like a different UI (Streamlit or React), tell me and I can add it.
