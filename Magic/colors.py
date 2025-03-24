import requests
import csv
# DATA IS ONLY GETTING COLOR PAIRINGS FOR SINGLE COLORED CARDS

# gets a list of every single-colored card in a set
# returns a csv with card name, the card's color
# and all possible color pairings for that single color
# EX: White (W) would have WU, WB, RW, GW


# NOTE: for the purpose of analysis, we are only looking at single colored cards and their performances
# in general + in a dual-color deck because looking at at multi-colored cards + factoring in splashes
# makes this a whole lot more complicated
# ADDITIONALLY, the list generated from this DOES add a few cards in the list that AREN'T available
# for draft/limited, therefore creating a few complications/extra cards that need to be manually removed
# EX: the alchemy versions of Leyline of Resonance and Heartfire Hero (dubbed A-Leyline of Resonance and
# A-Heartfire Hero) are in the list, but aren't available for draft/limited and so were manually removed
# DSK didn't have too many but BLB had a decent amount.

set_code = "BLB" 



def get_color_pairs(color):
    color_pairs = []
    valid_color_pairs = ['WU', 'UB', 'BR', 'RG', 'GW', 'WB', 'BG', 'GU', 'UR', 'RW']
    for pair in valid_color_pairs:
        if color[0] in pair:
            color_pairs.append(pair)
    return color_pairs
def get_cards_from_set(set_code):
    cards = []
    url = f"https://api.scryfall.com/cards/search?q=set%3A{set_code}"
    
    # Scryfall paginates responses, so we need to loop through pages if necessary
    while url:
        response = requests.get(url)
        data = response.json()
        
        # Add the cards to the list
        for card in data['data']:
            card_colors = card.get('colors', [])
            if len(card_colors) == 1:
                card_name = card['name']
                card_color_pairs = get_color_pairs(card_colors)
                cards.append({'name': card_name, 'colors': card_colors[0], 'color_pairs': ','.join(card_color_pairs)})
        
        # Get the URL for the next page, if it exists
        url = data.get('next_page')
    
    return cards

cards = get_cards_from_set(set_code)


with open(f'{set_code}_color_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['name', 'colors', 'color_pairs']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for card in cards:
        writer.writerow(card)

print(f"Card data saved")