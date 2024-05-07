"""Simulation of a basic Pokémon battle game. It includes classes for Pokémon, Trainer, and methods for importing data and simulating battles."""
#==============================================================================
# GLOBAL SECTION

#------------------------------------------------------------------------------
# IMPORT LIBRARIES
import json
import numpy as np

#------------------------------------------------------------------------------
# IMPORTING FUNCTIONS
def import_method(path,key):
    """Import data from a file and organize it into a dictionary using the specified key(s).
 
     Inputs
     ------
     - path: str, Path to the file containing the data.
     - key: str or tuple, Key(s) used to organize the data into the dictionary.
     
     Returns
     -------
     dict: Data organized into a dictionary.
     """
    if len(key) == 2:
        data = dict()
        with open(path, 'r', encoding="utf-8") as file:
            for line in file:
                d = json.loads(line)
                data[(d[key[0]], d[key[1]])] = d
    else:
        data = dict()
        with open(path, 'r', encoding="utf-8") as file:
            for line in file:
                d = json.loads(line)
                data[d[key]] = d
    return data


# Import pokedex and moves
pokedex = import_method('pokemon_data/pokemons.json','name')
moves = import_method('pokemon_data/moves.json','name')
pokemon_movesets = import_method('pokemon_data/pokemon_movesets.json','pokemonID')
type_effectiveness = import_method('pokemon_data/type_effectiveness.json',['attack','defend'])

#==============================================================================
# TRAINER
class Trainer:
    """Class representing a Pokémon trainer.
    
    Attributes
    ----------
    - name: str, Name of the trainer.
    - age: int, Age of the trainer.
    - gender: str, Gender of the trainer.
    - pokemons: list, List of Pokémon in the trainer's possession.
    - items: list, List of items in the trainer's possession.
    
    Methods
    -------
    - __init__(self, name, age, gender, pokemons, items):
        Initialize a Trainer object. 
    - add_pokemon(self, name):
        Add a Pokémon to the trainer's team. 
    - view_team(self):
        View the trainer's Pokémon team. 
    - remove_pokemon(self):
        Remove a Pokémon from the trainer's team.     
    - rename_pokemon(self):
        Rename a Pokémon in the trainer's team.
    - enemy_encounter(self):
        Simulate an encounter with an enemy Pokémon.
    """
    
    def __init__(self,name, age, gender, pokemons, items):
        """Initialize a Trainer object.
    
        Inputs
        ------
        - name: str, Name of the trainer.
        - age: int, Age of the trainer.
        - gender: str, Gender of the trainer.
        - pokemons: list, List of Pokémon in the trainer's possession.
        - items: list, List of items in the trainer's possession.
        """
        self.name = name
        self.age = age
        self.gender = gender
        self.pokemons = pokemons
        self.items = items

    def add_pokemon(self, name):
        """Add a Pokémon to the trainer's team.
    
        Inputs
        ------
        - name: str, Name of the Pokémon to be added.
        """
        # Check if team is full
        if len(self.pokemons)<6:
            self.pokemons.append(Pokemon(name))
        else:
            print('Your team is full the pokemon will added to ' + self.name + "'s PC.")
            
    def view_team(self):
        """View the trainer's Pokémon team."""
        for pkm_num, pkm in enumerate(self.pokemons):
            print(str(pkm_num+1) + ') ' + pkm.name + ' LV: ' + str(pkm.level)+ ', HP: ' + str(pkm.currentHP)+'/'+str(pkm.baseStats["hp"]))
            
    def remove_pokemon(self):
        """Remove a Pokémon from the trainer's team."""
        print('Which pokemon do you want to remove?\n')
        self.view_team()
        pokemon = int(input('\nRemove pokemon number:\n')) -1
        del self.pokemons[pokemon]
        
    def rename_pokemon(self):
        """Rename a Pokémon in the trainer's team."""
        print('Which pokemon do you want to rename?\n')
        self.view_team()
        pokemon = int(input('\nRename pokemon number:\n')) -1
        new_pokemon_name = input('Which name do you want to assign to your pokemon?\n')
        self.pokemons[pokemon].name = new_pokemon_name
        
    def enemy_encounter(self):
        """Simulate an encounter with an enemy Pokémon."""
        # Find the first non-fainted Pokemon
        pkm_num = 0
        while self.pokemons[pkm_num].currentHP == 0:
            pkm_num += 1        
        
        active_pokemon = self.pokemons[pkm_num]
        
        # Choose the action to perform in battle (in this Homework only "Attack" is implemented)
        print('What do you want to do?\n1)Attack\n2)Switch Pokemon\n3)Use item\n4)Run')
        action = int(input('\nChoose your action: '))
        
        # Attack
        if action == 1:
            
            # If Pokemon has no PP left it autmoatically uses the move: struggle
            if sum(active_pokemon.movesPP) == 0:
                print(active_pokemon.name + 'has no PP left. ' + active_pokemon.name + ' uses struggle.' )
                chosen_move = 'struggle'   
                # Use the move
                active_pokemon.UseMove(chosen_move,Pokemon("charmander"))
           
            # Select the move that Pokemon uses
            else:
                # Print the avaible moves
                for move_idx, move in enumerate(active_pokemon.moves):
                    print(str(move_idx+1)+') ' + move + ' PP: ' + str(active_pokemon.movesPP[move_idx]) + '/' + str(moves[move]['pp']))
               
                # Select a move
                chosen_move = int(input('What move should ' + active_pokemon.name + ' use? '))-1
                
                # Check that the move has PPs left
                while active_pokemon.movesPP[chosen_move] == 0:
                    chosen_move = int(input(active_pokemon.moves[chosen_move] + 'has no PP left for this move. What move should ' + active_pokemon.name + ' use? ')-1)
                
                # Decrease moves PP
                active_pokemon.movesPP[chosen_move] -= 1
                
                # Use the move
                enemy_pokemon = Pokemon("charmander")
                damage = active_pokemon.UseMove(active_pokemon.moves[chosen_move],enemy_pokemon)
                
                # Update enemy Pokemon HP's
                enemy_pokemon.currentHP = enemy_pokemon.currentHP - damage
                print(enemy_pokemon.name + ' has ' + str(int(enemy_pokemon.currentHP)) +'/' + str(enemy_pokemon.baseStats['hp']) + ' HP left.')
                
#==============================================================================
# CLASS POKEMON
class Pokemon:
    """Class representing a Pokémon.

    Attributes
    ----------
    - national_pokedex_number: int, National Pokédex number of the Pokémon.
    - name: str, Name of the Pokémon.
    - types: list, List of types of the Pokémon.
    - level: int, Level of the Pokémon.
    - baseStats: dict, Base statistics of the Pokémon.
    - currentHP: int, Current HP of the Pokémon.
    - moves: list, List of moves known by the Pokémon.
    - movesPP: list, List of remaining PP for each move.
    
    Methods
    -------
    - __init__(self, name):
        Initialize a Pokémon object.
        
    - UseMove(self, move, enemy):
        Simulate using a move by the Pokémon against an enemy Pokémon.
    """

    def __init__(self,name):
        """Initialize a Pokémon object.
    
        Inputs
        ------
        - name: str, Name of the Pokémon.
        """
        self.national_pokedex_number = pokedex[name]['national_pokedex_number']
        self.name = name
        self.types = pokedex[name]['types']
        self.level = 1
        self.baseStats = pokedex[name]['baseStats']
        self.currentHP = self.baseStats["hp"]
        self.moves = pokemon_movesets[self.national_pokedex_number]['moves']
        self.movesPP = [moves[move]['pp'] for move in self.moves]
        
    def UseMove(self, move, enemy):
        """Simulate using a move by the Pokémon against an enemy Pokémon.
        
        Inputs
        -----_
        - move: str, Name of the move to be used.
        - enemy: Pokemon, Enemy Pokémon object.
        
        Returns
        -------
        int: Damage dealt to the enemy Pokémon.
        """
        # Extract move used informations
        accuracy = moves[move]['accuracy']
        category = moves[move]['category']
        power = moves[move]['power']
        movetype = moves[move]['type']
        
        # Check if the move has an high probability to crit
        try:
            highcrit = moves[move]['highCriticalHitRatio']
            improve_crit = 2
        except KeyError:
            improve_crit = 1
            
        # Compute probability to crit
        if self.baseStats['speed']/512 * improve_crit > np.random.rand():
            critical = 2
        else: 
            critical = 1    
            
        # Calculate the damage
        if movetype in self.types:
            stab = 1.5
        else:
            stab = 1
        
        # Calculate the luck
        luck = np.random.uniform(0.85,1)
      
        # Calculate the modifier associate to type effectivness
        effect = 1
        for enemy_type in enemy.types:
            effect *= type_effectiveness[(movetype,enemy_type)]['effectiveness']
        
        # Calculate global modifier
        modifier = stab*effect*critical*luck
        
        # Calculate defending pokemon defense statistics to use
        if category == "physical":
            attack = self.baseStats['attack']
            defense = enemy.baseStats['defense']
        else:
            attack = self.baseStats['special']
            defense = enemy.baseStats['special']
        
        # Compute accuracy to hit and calculate the damage
        if np.random.rand()<accuracy:
            print(self.name +"'s attack hit the target")
            if critical ==2:
                print('Critical Hit!')
            if effect > 1:
                print('It is super effective!')
            elif effect <1:
                print('It is not very effective...')
            return np.floor(((2*self.level+10)/250*attack/defense*power+2)*modifier)
        else:
            print('Oh NO! '+ self.name +"'s attack missed")
            return 0

#==============================================================================
# MAIN
def main():
    """Call methods and create baisc obejct of Python Pokemon simulator."""
    #--------------------------------------------------------------------------
    # Main player
    print('Welcome to the Pokèmon world\n')
    print('What is your name?')
    player_name = input()
    print('What is your age?')
    player_age = input()
    print('What is your gender? (M/F)')
    player_gender = input()
    print('What is starter? (charmender/bulbasaur/squirtle)')
    starter = input()

    # Initial Pokemons and obejcts are not present
    player_pokemons, player_items = [], []
    
    # Create player object
    player = Trainer(player_name, player_age, player_gender, player_pokemons, player_items)

    # Add the starter more times to test later functions
    for i in range(0,3):
        player.add_pokemon(starter)
        
    #--------------------------------------------------------------------------
    # Rival
    if starter == "bulbasaur":
        rival_pokemons = pokedex["charmander"]
    elif starter == "squirtle":
        rival_pokemons = pokedex["bulbasaur"]
    else:
        rival_pokemons = pokedex["squirtle"]

    rival = Trainer(name="Tony", age="27", gender="Fluid", pokemons=rival_pokemons, items = [])

    #--------------------------------------------------------------------------
    # Possible actions
    
    # View team
    decision = input("Do you want to see your team? (Yes/No)\n")
    if decision == "Yes":
        player.view_team()
        
    # Rename Pokemon
    decision = input("Do you want to rename your Pokemons? (Yes/No)\n")
    if decision == "Yes":
        player.rename_pokemon()
         
    # Free Pokemon
    decision = input("Do you want to free one of your Pokemons? (Yes/No)\n")
    if decision == "Yes":
        player.remove_pokemon()
        
    # Free Pokemon
    decision = input("Do you want to fight a random Pokemon? (Yes/No)\n")
    if decision == "Yes":
        player.enemy_encounter()

    # Outputs
    return player, rival, pokedex, pokemon_movesets  


if __name__ == "__main__":
    player, rival, pokedex, pokemon_movesets = main()



