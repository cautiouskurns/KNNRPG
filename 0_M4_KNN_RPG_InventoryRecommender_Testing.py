# Necessary imports
import ipywidgets as widgets
from IPython.display import display, HTML
import random

# Define color scheme
COLOR_SCHEME = {
    'background': '#2b2b2b',
    'text': '#FFFFFF',
    'primary': '#3498DB',
    'secondary': '#E74C3C',
    'accent': '#2ECC71',
}

# CSS styles
styles = f"""
<style>
    .inventory-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 10px;
        padding: 20px;
        background-color: {COLOR_SCHEME['background']};
    }}
    .item {{
        width: 60px;
        height: 60px;
        background-color: {COLOR_SCHEME['primary']};
        border: 2px solid {COLOR_SCHEME['accent']};
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        color: {COLOR_SCHEME['text']};
    }}
</style>
"""

# Function to create a single item
def create_item(name):
    return f'<div class="item">{name}</div>'

# Function to create the inventory grid
def create_inventory_grid(items):
    grid = '<div class="inventory-grid">'
    for item in items:
        grid += create_item(item)
    grid += '</div>'
    return grid

# Main game class
class RPGInventory:
    def __init__(self):
        self.items = ['Sword', 'Shield', 'Potion', 'Gem', 'Coin']
    
    def display_inventory(self):
        inventory_html = styles + create_inventory_grid(self.items)
        display(HTML(inventory_html))

# Create and display the game
game = RPGInventory()
game.display_inventory()