"""Teen Patti hand ranking utilities

Features:
- generate_deck(): returns 52 cards as strings like "A♠"
- generate_all_hands(): returns all 3-card combinations
- get_hand_category(hand): returns category name
- rank_hand(hand): returns numeric rank where lower is stronger
- CLI: simple input and sample outputs

Teen Patti ranking order (strongest to weakest):
1. Trail (three of a kind)
2. Pure sequence (straight flush)
3. Sequence (straight)
4. Color (flush)
5. Pair
6. High card

"""
from itertools import combinations
from functools import cmp_to_key
import math

RANK_ORDER = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
RANK_VALUE = {r:i for i,r in enumerate(RANK_ORDER, start=2)}  # 2->2 ... A->14
SUITS = ['♠','♥','♦','♣']

TOTAL_HANDS = math.comb(52,3)

def generate_deck():
    """Return list of 52 cards as strings like 'A♠'"""
    deck = []
    for r in RANK_ORDER:
        for s in SUITS:
            deck.append(f"{r}{s}")
    return deck

def parse_card(card):
    """Return (rank_str, suit) from card string like '10♣'"""
    # suit is last char, rank is rest
    rank = card[:-1]
    suit = card[-1]
    return rank, suit

def card_value(card):
    r,_ = parse_card(card)
    return RANK_VALUE[r]

def is_sequence(values):
    """Check if sorted integer rank values form a sequence (including A-2-3 and Q-K-A)"""
    values = sorted(values)
    # handle wheel A-2-3: treat Ace as 1
    if values == [2,3,14]:
        return True
    return values[0]+1==values[1] and values[1]+1==values[2]


def get_hand_category(hand):
    """Return category name as per Teen Patti rules"""
    ranks = []
    suits = []
    for c in hand:
        r,s = parse_card(c)
        ranks.append(r)
        suits.append(s)
    values = [RANK_VALUE[r] for r in ranks]
    unique_ranks = set(ranks)
    unique_suits = set(suits)

    if len(unique_ranks)==1:
        return 'Trail'
    is_seq = is_sequence(values)
    is_flush = len(unique_suits)==1
    if is_seq and is_flush:
        return 'Pure Sequence'
    if is_seq:
        return 'Sequence'
    if is_flush:
        return 'Color'
    if len(unique_ranks)==2:
        return 'Pair'
    return 'High Card'


def hand_comparator(a,b):
    """Compare two hands, return -1 if a stronger than b, 1 if weaker, 0 if equal"""
    # Compare categories first
    order = ['Trail','Pure Sequence','Sequence','Color','Pair','High Card']
    ca = get_hand_category(a)
    cb = get_hand_category(b)
    if order.index(ca) < order.index(cb):
        return -1
    if order.index(ca) > order.index(cb):
        return 1
    # Same category -> tie-break rules
    # We'll compute a key tuple where higher items are better.
    def tie_key(hand):
        ranks = [card_value(c) for c in hand]
        ranks.sort(reverse=True)
        # For sequences treat A-2-3 as [3,2,1] but Ace low.
        # For comparison, normalize sequence highest card (use 3 for A-2-3)
        cat = get_hand_category(hand)
        if cat in ('Pure Sequence','Sequence'):
            vals = sorted([card_value(c) for c in hand])
            if vals == [2,3,14]:
                # wheel, high card is 3
                return (3,2,1)
            return tuple(sorted([card_value(c) for c in hand], reverse=True))
        if cat == 'Trail':
            # value of the trip
            return (ranks[0],)
        if cat == 'Color' or cat == 'High Card':
            # compare highest to lowest
            return tuple(ranks)
        if cat == 'Pair':
            # pair rank then kicker
            # find pair value
            vals = [card_value(c) for c in hand]
            # pair value is the one that appears twice
            from collections import Counter
            cnt = Counter(vals)
            pair_val = max(k for k,v in cnt.items() if v==2)
            kicker = max(k for k,v in cnt.items() if v==1)
            return (pair_val, kicker)
        return tuple(ranks)

    ka = tie_key(a)
    kb = tie_key(b)
    # compare tuples
    if ka>kb:
        return -1
    if ka<kb:
        return 1
    return 0


def generate_all_hands():
    """Generate all 3-card combinations from the deck as lists of strings."""
    deck = generate_deck()
    for comb in combinations(deck,3):
        yield list(comb)


def rank_hand(hand, precomputed_sorted_hands=None):
    """Return numeric rank (1 is best) of hand among all possible hands.
    If precomputed_sorted_hands (list) is provided, use it.
    """
    if precomputed_sorted_hands is None:
        # build and sort once
        all_hands = list(generate_all_hands())
        all_hands.sort(key=cmp_to_key(hand_comparator))
    else:
        all_hands = precomputed_sorted_hands
    # find position (1-based). If multiple identical hands (due to ordering), find first occurrence.
    # We'll compare by category and tie_key equality.
    from collections import defaultdict
    # Build a key map from tuple representation to indices to speed lookup
    def hand_key(hand):
        cat = get_hand_category(hand)
        # key: (cat, tie_key)
        # we need same tie_key logic as comparator
        def tie_key_inner(hand):
            ranks = [card_value(c) for c in hand]
            ranks.sort(reverse=True)
            cat = get_hand_category(hand)
            if cat in ('Pure Sequence','Sequence'):
                vals = sorted([card_value(c) for c in hand])
                if vals == [2,3,14]:
                    return (3,2,1)
                return tuple(sorted([card_value(c) for c in hand], reverse=True))
            if cat == 'Trail':
                return (ranks[0],)
            if cat == 'Color' or cat == 'High Card':
                return tuple(ranks)
            if cat == 'Pair':
                from collections import Counter
                cnt = Counter(ranks)
                pair_val = max(k for k,v in cnt.items() if v==2)
                kicker = max(k for k,v in cnt.items() if v==1)
                return (pair_val, kicker)
            return tuple(ranks)
        return (cat, tie_key_inner(hand))

    # Precompute mapping
    key_to_index = {}
    for idx, h in enumerate(all_hands, start=1):
        if idx%5000==0:
            pass
        k = hand_key(h)
        if k not in key_to_index:
            key_to_index[k] = idx
    kq = hand_key(hand)
    rank = key_to_index.get(kq)
    if rank is None:
        # fallback linear search (shouldn't happen)
        for idx,h in enumerate(all_hands,start=1):
            if hand_comparator(hand,h)==0:
                rank = idx
                break
    return rank, TOTAL_HANDS


def precompute_sorted_hands():
    """Return a list of all hands sorted strongest to weakest."""
    all_hands = list(generate_all_hands())
    all_hands.sort(key=cmp_to_key(hand_comparator))
    return all_hands


def percentile_of_better(rank, total):
    """Return percentile (string) representing what percent of hands are better than the given rank."""
    better = rank-1
    pct = better/total*100
    # show Top x% -> percent of hands as good or better? We'll show probability of better hands
    return pct


if __name__ == '__main__':
    # Quick CLI demo and sample outputs
    print(f"Total possible Teen Patti hands: {TOTAL_HANDS}")
    print("Precomputing and sorting all hands (this may take a moment)...")
    sorted_hands = precompute_sorted_hands()
    print("Done.")

    # Sample hands to display
    samples = [
        ["A♠","K♠","Q♠"],
        ["A♠","A♥","A♦"],
        ["2♣","3♣","4♣"],
        ["10♣","10♦","3♠"],
        ["K♠","Q♥","9♦"],
    ]
    for sh in samples:
        cat = get_hand_category(sh)
        rank, total = rank_hand(sh, precomputed_sorted_hands=sorted_hands)
        pct = percentile_of_better(rank, total)
        print(f"Input hand {sh} -> {cat}, Rank {rank} of {total} (Top {pct:.3f}% have better hands)")
