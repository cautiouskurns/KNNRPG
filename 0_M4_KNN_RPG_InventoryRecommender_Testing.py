import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
import random
import json

COLOR_SCHEME = {
    'background': '#2b2b2b',
    'text': '#FFFFFF',
    'primary': '#3498DB',
    'secondary': '#E74C3C',
    'accent': '#2ECC71',
    'hover': '#9b9b9b',
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
</style>
"""

class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class RPGInventory:
    def __init__(self):
        self.items = [
            Item("Sword", "A sharp blade"),
            Item("Shield", "Sturdy protection"),
            Item("Potion", "Heals 50 HP"),
            Item("Gem", "Valuable treasure"),
            Item("Coin", "Currency")
        ]
        self.max_items = 10

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
        <div class="item" draggable="true" ondragstart="drag(event)" id="item-{index}">
            {item.name}
            <span class="tooltip">{item.description}</span>
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
        new_item = Item(f"Item {len(self.items) + 1}", f"Description for Item {len(self.items) + 1}")
        if self.add_item(new_item):
            self.update_inventory()

    def remove_last_item(self, _):
        if self.remove_item(len(self.items) - 1):
            self.update_inventory()

    def update_inventory(self):
        inventory_data = json.dumps([{'name': item.name, 'description': item.description} for item in self.items])
        js_code = f"""
        console.log("Updating inventory...");
        console.log("Inventory data:", {inventory_data});
        updateInventory({inventory_data});
        """
        display(Javascript(js_code))

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
    var draggedElement = document.getElementById(data);
    if (ev.target.classList.contains('item') && !ev.target.firstChild) {
        ev.target.appendChild(draggedElement);
    } else if (ev.target.classList.contains('inventory-grid')) {
        ev.target.appendChild(draggedElement);
    }
}

function updateInventory(inventoryData) {
    console.log("Updating inventory in JS", inventoryData);
    var grid = document.querySelector('.inventory-grid');
    grid.innerHTML = '';
    inventoryData.forEach((item, index) => {
        var itemDiv = document.createElement('div');
        itemDiv.className = 'item';
        itemDiv.draggable = true;
        itemDiv.ondragstart = drag;
        itemDiv.ondrop = drop;
        itemDiv.ondragover = allowDrop;
        itemDiv.id = 'item-' + index;
        itemDiv.innerHTML = item.name + '<span class="tooltip">' + item.description + '</span>';
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

display(Javascript(js_code))


# Initial inventory update to ensure everything is set up
game.update_inventory()

print("Items in inventory:", [item.name for item in game.items])