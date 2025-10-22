from flask import Flask, render_template, request, jsonify
from teen_patti import generate_deck, get_hand_stats, precompute_sorted_hands

app = Flask(__name__)

# Precompute sorted hands once on startup to speed rankings
sorted_hands = precompute_sorted_hands()

def normalize_card(card_str):
    # basic normalization - ensure suit is a single char
    return card_str

@app.route('/')
def index():
    deck = generate_deck()
    # group by suit for display order
    suits = {'♠':[], '♥':[], '♦':[], '♣':[]}
    for c in deck:
        suits[c[-1]].append(c)
    return render_template('index.html', suits=suits)

@app.route('/api/rank', methods=['POST'])
def api_rank():
    data = request.json or {}
    hand = data.get('hand')
    try:
        stats = get_hand_stats(hand, precomputed_sorted_hands=sorted_hands)
        return jsonify({'ok': True, 'stats': stats})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

if __name__ == '__main__':
    # Run in single-process mode (no reloader) for predictable behavior.
    # Bind to 127.0.0.1 only (local dev).
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
