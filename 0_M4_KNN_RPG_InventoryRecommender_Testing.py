import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
import random
import json
import plotly.graph_objs as go
import pandas as pd

COLOR_SCHEME = {
    'background': '#2b2b2b',
    'text': '#FFFFFF',
    'primary': '#3498DB',
    'secondary': '#E74C3C',
    'accent': '#2ECC71',
    'hover': '#9b9b9b',
    'common': '#B0B0B0',
    'uncommon': '#55AA55',
    'rare': '#5555FF',
    'epic': '#AA55AA',
    'legendary': '#FFAA00',
}

styles = f"""
<style>
    #inventory-container {{
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }}
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
        cursor: move;
        position: relative;
    }}
    .item:hover {{
        background-color: {COLOR_SCHEME['hover']};
    }}
    .tooltip {{
        visibility: hidden;
        width: 120px;
        background-color: {COLOR_SCHEME['secondary']};
        color: {COLOR_SCHEME['text']};
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .item:hover .tooltip {{
        visibility: visible;
        opacity: 1;
    }}
    .control-panel {{
        margin-top: 20px;
        display: flex;
        justify-content: space-around;
    }}
    .character-stats {{
        display: flex;
        align-items: flex-start;
        margin-top: 20px;
        background-color: {COLOR_SCHEME['background']};
        padding: 20px;
        border-radius: 8px;
        color: {COLOR_SCHEME['text']};
    }}
    .character-image {{
        width: 100px;
        height: 100px;
        background-color: {COLOR_SCHEME['primary']};
        border-radius: 50%;
        margin-right: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        font-weight: bold;
    }}
    .character-details {{
        flex: 1;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }}
    .stat-label {{
        font-weight: bold;
    }}
    .radar-chart {{
        margin-top: 20px;
    }}
    .item-card {{
        width: 200px;
        background-color: {COLOR_SCHEME['background']};
        border: 2px solid {COLOR_SCHEME['accent']};
        border-radius: 8px;
        padding: 10px;
        margin: 10px;
        color: {COLOR_SCHEME['text']};
    }}
    .item-name {{
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 5px;
    }}
    .item-type {{
        font-style: italic;
        margin-bottom: 5px;
    }}
    .item-stats {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 5px;
    }}
    .common {{ color: {COLOR_SCHEME['common']}; }}
    .uncommon {{ color: {COLOR_SCHEME['uncommon']}; }}
    .rare {{ color: {COLOR_SCHEME['rare']}; }}
    .epic {{ color: {COLOR_SCHEME['epic']}; }}
    .legendary {{ color: {COLOR_SCHEME['legendary']}; }}
</style>
"""

class Item:
    def __init__(self, name, item_type, rarity, power, required_stats):
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.power = power
        self.required_stats = required_stats

    def to_dict(self):
        return {
            'name': self.name,
            'item_type': self.item_type,  # Changed 'type' to 'item_type'
            'rarity': self.rarity,
            'power': self.power,
            'required_stats': self.required_stats
        }

    def create_item_card(self):
        return f"""
        <div class="item-card">
            <div class="item-name {self.rarity.lower()}">{self.name}</div>
            <div class="item-type">{self.item_type}</div>
            <div class="item-stats">
                <div>Rarity:</div><div class="{self.rarity.lower()}">{self.rarity}</div>
                <div>Power:</div><div>{self.power}</div>
                <div>Required Stats:</div><div>{', '.join(f'{k}: {v}' for k, v in self.required_stats.items())}</div>
            </div>
        </div>
        """

class RPGInventory:
    def __init__(self):
        self.items = []
        self.max_items = 10
        self.item_database = self.create_item_database()

    def create_item_database(self):
        items = [
            Item("Steel Sword", "Weapon", "Common", 10, {"strength": 5}),
            Item("Magic Staff", "Weapon", "Uncommon", 15, {"intelligence": 8}),
            Item("Leather Armor", "Armor", "Common", 8, {"dexterity": 3}),
            Item("Healing Potion", "Consumable", "Common", 5, {}),
            Item("Dragon Scale", "Material", "Rare", 50, {}),
            Item("Enchanted Bow", "Weapon", "Rare", 25, {"dexterity": 10}),
            Item("Mithril Chainmail", "Armor", "Epic", 40, {"strength": 15, "dexterity": 10}),
            Item("Philosopher's Stone", "Artifact", "Legendary", 100, {"intelligence": 20}),
        ]
        return pd.DataFrame([item.to_dict() for item in items])

    def add_item(self, item):
        if len(self.items) < self.max_items:
            self.items.append(item)
            return True
        return False

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
            return True
        return False

    def create_item_html(self, item, index):
        return f"""
        <div class="item {item.rarity.lower()}" draggable="true" ondragstart="drag(event)" id="item-{index}">
            {item.name}
            <span class="tooltip">{item.item_type}</span>
        </div>
        """

    def create_inventory_grid(self):
        grid = '<div class="inventory-grid">'
        for i, item in enumerate(self.items):
            grid += self.create_item_html(item, i)
        for _ in range(len(self.items), self.max_items):
            grid += '<div class="item" ondrop="drop(event)" ondragover="allowDrop(event)"></div>'
        grid += '</div>'
        return grid

    def display_inventory(self):
        inventory_html = f"""
        {styles}
        <div id="inventory-container">
            {self.create_inventory_grid()}
        </div>
        """
        display(HTML(inventory_html))
        
        add_button = widgets.Button(description="Add Random Item")
        remove_button = widgets.Button(description="Remove Last Item")
        
        add_button.on_click(self.add_random_item)
        remove_button.on_click(self.remove_last_item)
        
        display(widgets.HBox([add_button, remove_button]))

    def add_random_item(self, _):
        if len(self.items) < self.max_items:
            random_item = self.item_database.sample(1).iloc[0]
            new_item = Item(
                random_item['name'],
                random_item['item_type'],  # Changed 'type' to 'item_type'
                random_item['rarity'],
                random_item['power'],
                random_item['required_stats']
            )
            self.items.append(new_item)
            self.update_inventory()

    def remove_last_item(self, _):
        if self.remove_item(len(self.items) - 1):
            self.update_inventory()

    def update_inventory(self):
        inventory_data = json.dumps([item.to_dict() for item in self.items])
        js_code = f"""
        console.log("Updating inventory...");
        console.log("Inventory data:", {inventory_data});
        updateInventory({inventory_data});
        """
        display(Javascript(js_code))

    def display_item_database(self):
        item_cards = ''.join([Item(**item).create_item_card() for _, item in self.item_database.iterrows()])
        display(HTML(f"{styles}<div style='display: flex; flex-wrap: wrap;'>{item_cards}</div>"))

class Character:
    def __init__(self, name, char_class, level=1):
        self.name = name
        self.char_class = char_class
        self.level = level
        self.strength = random.randint(1, 20)
        self.intelligence = random.randint(1, 20)
        self.dexterity = random.randint(1, 20)

    def to_dict(self):
        return {
            'name': self.name,
            'class': self.char_class,
            'level': self.level,
            'strength': self.strength,
            'intelligence': self.intelligence,
            'dexterity': self.dexterity
        }

class CharacterCreator:
    def __init__(self):
        self.name_input = widgets.Text(description='Name:')
        self.class_dropdown = widgets.Dropdown(
            options=['Warrior', 'Mage', 'Rogue'],
            description='Class:'
        )
        self.create_button = widgets.Button(description='Create Character')
        self.create_button.on_click(self.create_character)
        self.output = widgets.Output()

    def display(self):
        display(self.name_input, self.class_dropdown, self.create_button, self.output)

    def create_character(self, _):
        with self.output:
            self.output.clear_output()
            name = self.name_input.value
            char_class = self.class_dropdown.value
            character = Character(name, char_class)
            print(f"Character created: {character.name} the {character.char_class}")
            self.display_character_stats(character)

    def display_character_stats(self, character):
        stats = ['Strength', 'Intelligence', 'Dexterity']
        values = [character.strength, character.intelligence, character.dexterity]

        fig = go.Figure(data=go.Scatterpolar(
            r=values + values[:1],
            theta=stats + stats[:1],
            fill='toself'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 20])
            ),
            showlegend=False
        )

        character_html = f"""
        {styles}
        <div class="character-stats">
            <div class="character-image">?</div>
            <div class="character-details">
                <div class="stat-label">Name:</div> <div>{character.name}</div>
                <div class="stat-label">Class:</div> <div>{character.char_class}</div>
                <div class="stat-label">Level:</div> <div>{character.level}</div>
                <div class="stat-label">Strength:</div> <div>{character.strength}</div>
                <div class="stat-label">Intelligence:</div> <div>{character.intelligence}</div>
                <div class="stat-label">Dexterity:</div> <div>{character.dexterity}</div>
            </div>
        </div>
        <div class="radar-chart" id="plotly-figure"></div>
        """

        display(HTML(character_html))
        fig.show()

# Create the game instance
game = RPGInventory()

# Display the inventory
game.display_inventory()

# Set up JavaScript functions
js_code = """
console.log("Setting up JS functions...");
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    console.log("Drag started", ev.target.id);
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    console.log("Drop event", data);
    if (ev.target.classList.contains('item') && !ev.target.firstChild) {
        ev.target.appendChild(document.getElementById(data));
    }
}

function updateInventory(inventoryData) {
    console.log("Updating inventory in JS", inventoryData);
    var grid = document.querySelector('.inventory-grid');
    grid.innerHTML = '';
    inventoryData.forEach((item, index) => {
        var itemDiv = document.createElement('div');
        itemDiv.className = `item ${item.rarity.toLowerCase()}`;
        itemDiv.draggable = true;
        itemDiv.ondragstart = drag;
        itemDiv.ondrop = drop;
        itemDiv.ondragover = allowDrop;
        itemDiv.id = 'item-' + index;
        itemDiv.innerHTML = item.name + `<span class="tooltip">${item.item_type}</span>`;
        grid.appendChild(itemDiv);
    });
    for (let i = inventoryData.length; i < 10; i++) {
        var emptyDiv = document.createElement('div');
        emptyDiv.className = 'item';
        emptyDiv.ondrop = drop;
        emptyDiv.ondragover = allowDrop;
        grid.appendChild(emptyDiv);
    }
}

// Attach event listeners to all items
document.querySelectorAll('.item').forEach(item => {
    item.ondragstart = drag;
    item.ondrop = drop;
    item.ondragover = allowDrop;
});

// Make sure updateInventory is available globally
window.updateInventory = updateInventory;
"""

display(Javascript(js_code))

# Initial inventory update to ensure everything is set up
game.update_inventory()

print("Items in inventory:", [item.name for item in game.items])

# Create and display the character creator
creator = CharacterCreator()
creator.display()

# Display the item database
print("\nItem Database:")
game.display_item_database()
