import ipywidgets as widgets
from IPython.display import display, HTML, Javascript
import random
import json
import plotly.graph_objs as go
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import numpy as np


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

class Character:
    def __init__(self, name, char_class, level=1):
        self.name = name
        self.char_class = char_class
        self.level = level
        self.strength = random.randint(1, 20)
        self.intelligence = random.randint(1, 20)
        self.dexterity = random.randint(1, 20)
        self.inventory = []

    def to_dict(self):
        return {
            'name': self.name,
            'class': self.char_class,
            'level': self.level,
            'strength': self.strength,
            'intelligence': self.intelligence,
            'dexterity': self.dexterity,
            'inventory': [item.to_dict() for item in self.inventory]
        }

    @classmethod
    def from_dict(cls, data):
        character = cls(data['name'], data['class'], data['level'])
        character.strength = data['strength']
        character.intelligence = data['intelligence']
        character.dexterity = data['dexterity']
        character.inventory = [Item(**item_data) for item_data in data['inventory']]
        return character

class KNNRecommender:
    def __init__(self, game):
        self.game = game
        self.scaler = StandardScaler()
        self.knn_model = None

    def prepare_data(self):
        data = [char.to_dict() for char in self.game.characters]
        df = pd.DataFrame(data)
        features = ['strength', 'intelligence', 'dexterity', 'level']
        X = df[features]
        return X, df

    def fit(self, n_neighbors=5):
        X, _ = self.prepare_data()
        X_scaled = self.scaler.fit_transform(X)
        self.knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
        self.knn_model.fit(X_scaled)

    def get_recommendations(self, character, n_recommendations=5):
        if self.knn_model is None:
            self.fit()

        character_features = [[character.strength, character.intelligence, character.dexterity, character.level]]
        character_scaled = self.scaler.transform(character_features)
        
        distances, indices = self.knn_model.kneighbors(character_scaled)
        
        X, df = self.prepare_data()
        recommendations = df.iloc[indices[0][1:]]  # Exclude the first one as it's the character itself
        
        return recommendations

    def visualize_knn(self, character):
        X, df = self.prepare_data()
        X_scaled = self.scaler.transform(X)
        
        character_features = [[character.strength, character.intelligence, character.dexterity, character.level]]
        character_scaled = self.scaler.transform(character_features)
        
        distances, indices = self.knn_model.kneighbors(character_scaled)
        
        fig = go.Figure()

        # Plot all characters
        fig.add_trace(go.Scatter3d(
            x=X_scaled[:, 0],
            y=X_scaled[:, 1],
            z=X_scaled[:, 2],
            mode='markers',
            marker=dict(size=4, color='blue', opacity=0.5),
            text=df['name'],
            name='All Characters'
        ))

        # Plot the input character
        fig.add_trace(go.Scatter3d(
            x=[character_scaled[0][0]],
            y=[character_scaled[0][1]],
            z=[character_scaled[0][2]],
            mode='markers',
            marker=dict(size=8, color='red'),
            text=[character.name],
            name='Input Character'
        ))

        # Plot the nearest neighbors
        fig.add_trace(go.Scatter3d(
            x=X_scaled[indices[0][1:], 0],
            y=X_scaled[indices[0][1:], 1],
            z=X_scaled[indices[0][1:], 2],
            mode='markers',
            marker=dict(size=6, color='green'),
            text=df.iloc[indices[0][1:]]['name'],
            name='Nearest Neighbors'
        ))

        fig.update_layout(
            scene=dict(
                xaxis_title='Strength (Scaled)',
                yaxis_title='Intelligence (Scaled)',
                zaxis_title='Dexterity (Scaled)'
            ),
            width=700,
            margin=dict(r=20, b=10, l=10, t=10),
            title='KNN Visualization'
        )

        fig.show()


class RPGInventory:
    def __init__(self):
        self.items = []
        self.max_items = 10
        self.item_database = self.create_item_database()
        self.characters = []
        self.recommender = KNNRecommender(self)

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

    def save_game_state(self, filename='game_state.json'):
        # Convert DataFrame to a JSON-serializable format and ensure all numbers are native Python types
        item_database_serializable = self.item_database.applymap(
            lambda x: int(x) if isinstance(x, (pd._libs.tslibs.timestamps.Timestamp, pd.Timestamp, pd._libs.tslibs.nattype.NaTType, pd.Series, pd.Index)) or isinstance(x, (pd.Series, pd.Index)) else x
        ).to_dict(orient='records')

        game_state = {
            'characters': [character.to_dict() for character in self.characters],
            'item_database': item_database_serializable
        }

        # Convert any int64 to int in the characters' data
        for character in game_state['characters']:
            for key, value in character.items():
                if isinstance(value, pd.Series) or isinstance(value, pd.Index):
                    character[key] = int(value)

        with open(filename, 'w') as f:
            json.dump(game_state, f, default=int)  # Default to converting numbers to int
        print(f"Game state saved to {filename}")

    def load_game_state(self, filename='game_state.json'):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                game_state = json.load(f)
            self.characters = [Character.from_dict(char_data) for char_data in game_state['characters']]
            self.item_database = pd.DataFrame(game_state['item_database'])
            print(f"Game state loaded from {filename}")
        else:
            print(f"No saved game state found at {filename}")

    def generate_simulated_players(self, num_players=100):
        classes = ['Warrior', 'Mage', 'Rogue']
        simulated_players = []
        for i in range(num_players):
            name = f"Player{i+1}"
            char_class = random.choice(classes)
            level = random.randint(1, 50)
            character = Character(name, char_class, level)
            for _ in range(random.randint(0, self.max_items)):
                random_item = self.item_database.sample(1).iloc[0]
                item = Item(
                    random_item['name'],
                    random_item['item_type'],
                    random_item['rarity'],
                    random_item['power'],
                    random_item['required_stats']
                )
                character.inventory.append(item)
            simulated_players.append(character)
        self.characters.extend(simulated_players)
        print(f"Generated {num_players} simulated players")

    def visualize_player_data(self):
        data = [char.to_dict() for char in self.characters]
        df = pd.DataFrame(data)

        # Scatter plot of Strength vs Intelligence
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        sns.scatterplot(data=df, x='strength', y='intelligence', hue='class', ax=ax1)
        ax1.set_title('Strength vs Intelligence by Class')

        # Heatmap of average stats by class
        class_stats = df.groupby('class')[['strength', 'intelligence', 'dexterity']].mean()
        sns.heatmap(class_stats, annot=True, cmap='YlGnBu', ax=ax2)
        ax2.set_title('Average Stats by Class')

        plt.tight_layout()
        plt.show()

        # Item distribution
        item_counts = df['inventory'].apply(len)
        plt.figure(figsize=(10, 5))
        sns.histplot(item_counts, kde=True)
        plt.title('Distribution of Items per Player')
        plt.xlabel('Number of Items')
        plt.ylabel('Count of Players')
        plt.show()

    def get_recommendations_for_character(self, character):
        recommendations = self.recommender.get_recommendations(character)
        print(f"Recommendations for {character.name}:")
        for _, rec in recommendations.iterrows():
            print(f"- {rec['name']} (Class: {rec['class']}, Level: {rec['level']})")
        
        self.recommender.visualize_knn(character)

class CharacterCreator:
    def __init__(self, game):
        self.game = game
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
            self.game.characters.append(character)
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



# Create an interactive character creator with recommendations
class InteractiveCharacterCreator(CharacterCreator):
    def __init__(self, game):
        super().__init__(game)
        self.level_input = widgets.IntSlider(min=1, max=50, step=1, value=1, description='Level:')
        self.strength_input = widgets.IntSlider(min=1, max=20, step=1, value=10, description='Strength:')
        self.intelligence_input = widgets.IntSlider(min=1, max=20, step=1, value=10, description='Intelligence:')
        self.dexterity_input = widgets.IntSlider(min=1, max=20, step=1, value=10, description='Dexterity:')
        self.recommend_button = widgets.Button(description='Get Recommendations')
        self.recommend_button.on_click(self.get_recommendations)

    def display(self):
        display(self.name_input, self.class_dropdown, self.level_input, self.strength_input, 
                self.intelligence_input, self.dexterity_input, self.create_button, 
                self.recommend_button, self.output)

    def create_character(self, _):
        with self.output:
            self.output.clear_output()
            name = self.name_input.value
            char_class = self.class_dropdown.value
            level = self.level_input.value
            character = Character(name, char_class, level)
            character.strength = self.strength_input.value
            character.intelligence = self.intelligence_input.value
            character.dexterity = self.dexterity_input.value
            self.game.characters.append(character)
            print(f"Character created: {character.name} the {character.char_class}")
            self.display_character_stats(character)

    def get_recommendations(self, _):
        with self.output:
            self.output.clear_output()
            character = Character(self.name_input.value, self.class_dropdown.value, self.level_input.value)
            character.strength = self.strength_input.value
            character.intelligence = self.intelligence_input.value
            character.dexterity = self.dexterity_input.value  # Fixed this line
            self.game.get_recommendations_for_character(character)


# Create the game instance
game = RPGInventory()

# Display the inventory
game.display_inventory()

# Set up JavaScript functions
js_code = """
// ... [Previous JavaScript code remains the same] ...
"""

display(Javascript(js_code))

# Initial inventory update to ensure everything is set up
game.update_inventory()

print("Items in inventory:", [item.name for item in game.items])

# Create and display the character creator
creator = CharacterCreator(game)
creator.display()

# Display the item database
print("\nItem Database:")
game.display_item_database()

# Generate simulated players
game.generate_simulated_players(100)

# Visualize player data
game.visualize_player_data()

# Save game state
game.save_game_state()

# Load game state (for demonstration)
game.load_game_state()

# Fit the KNN model after generating simulated players
game.recommender.fit()

# Create and display the interactive character creator
interactive_creator = InteractiveCharacterCreator(game)
interactive_creator.display()