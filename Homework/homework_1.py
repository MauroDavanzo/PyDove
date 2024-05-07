#==============================================================================
# GLOBALS

#------------------------------------------------------------------------------
# IMPORT LIBRARIES
import json
import numpy as np

#------------------------------------------------------------------------------
# IMPORTING FUNCTIONS

def import_method(path,key):
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

    def __init__(self,name, age, gender, pokemons, items):
        self.name = name
        self.age = age
        self.gender = gender
        self.pokemons = pokemons
        self.items = items

    def add_pokemon(self, name):
        if len(self.pokemons)<6:
            self.pokemons.append(Pokemon(name))
        else:
            print('Your team is full the pokemon will added to ' + self.name + "'s PC.")
            
    def view_team(self):
        for pkm_num, pkm in enumerate(self.pokemons):
            print(str(pkm_num+1) + ') ' + pkm.name + ' LV: ' + str(pkm.level)+ ', HP: ' + str(pkm.currentHP)+'/'+str(pkm.baseStats["hp"]))
            
    def remove_pokemon(self):
        print('Which pokemon do you want to remove?\n')
        self.view_team()
        pokemon = int(input('\nRemove pokemon number:\n')) -1
        del self.pokemons[pokemon]
        
    def rename_pokemon(self):
        print('Which pokemon do you want to rename?\n')
        self.view_team()
        pokemon = int(input('\nRename pokemon number:\n')) -1
        new_pokemon_name = input('Which name do you want to assign to your pokemon?\n')
        self.pokemons[pokemon].name = new_pokemon_name
        
    def enemy_encounter(self):     
        pkm_num = 0
        while self.pokemons[pkm_num].currentHP == 0:
            pkm_num += 1        
        
        active_pokemon = self.pokemons[pkm_num]
        
        print('What do you want to do?\n1)Attack\n2)Switch Pokemon\n3)Use item\n4)Run')
        action = int(input('\nChoose your action: '))
        
        if action == 1:
            # Check if all PP of all moves are zero
            if sum(active_pokemon.movesPP) == 0:
                print(active_pokemon.name + 'has no PP left. ' + active_pokemon.name + ' uses struggle.' )
                chosen_move = 'struggle'
                
                # Use the move
                active_pokemon.UseMove(chosen_move,Pokemon("charmander"))
                
            else:
                # Print the avaible moves
                for move_idx, move in enumerate(active_pokemon.moves):
                    print(str(move_idx+1)+') ' + move + ' PP: ' + str(active_pokemon.movesPP[move_idx]) + '/' + str(moves[move]['pp']))
                chosen_move = int(input('What move should ' + active_pokemon.name + ' use? '))-1
                
                while active_pokemon.movesPP[chosen_move] == 0:
                    chosen_move = int(input(active_pokemon.moves[chosen_move] + 'has no PP left for this move. What move should ' + active_pokemon.name + ' use? ')-1)
                
                # Decrease moves PP
                active_pokemon.movesPP[chosen_move] -= 1
                
                # Use the move
                enemy_pokemon = Pokemon("charmander")
                damage = active_pokemon.UseMove(active_pokemon.moves[chosen_move],enemy_pokemon)
                
                enemy_pokemon.currentHP = enemy_pokemon.currentHP - damage
                print(enemy_pokemon.name + ' has ' + str(int(enemy_pokemon.currentHP)) +'/' + str(enemy_pokemon.baseStats['hp']) + ' HP left.')
                
#==============================================================================
# CLASS POKEMON

class Pokemon:

    def __init__(self,name):

        self.national_pokedex_number = pokedex[name]['national_pokedex_number']
        self.name = name
        self.types = pokedex[name]['types']
        self.level = 1
        self.baseStats = pokedex[name]['baseStats']
        self.currentHP = self.baseStats["hp"]
        self.moves = pokemon_movesets[self.national_pokedex_number]['moves']
        self.movesPP = [moves[move]['pp'] for move in self.moves]
        
    def UseMove(self, move, enemy):
        
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

        luck = np.random.uniform(0.85,1)
      
        # Type effectivness
        effect = 1
        for enemy_type in enemy.types:
            effect *= type_effectiveness[(movetype,enemy_type)]['effectiveness']
        
        
        modifier = stab*effect*critical*luck    
        if category == "physical":
            attack = self.baseStats['attack']
            defense = enemy.baseStats['defense']
        else:
            attack = self.baseStats['special']
            defense = enemy.baseStats['special']

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
    print('Welcome to the Pokèmon world\n')

    # # Silence inputs

    # print('What is your name?')
    # name = input()
    # print('What is your age?')
    # age = input()
    # print('What is your gender? (M/F)')
    # gender = input()
    # print('What is starter? (Charmender/Bulbasaur/Squirtle)')
    # starter = input()

    # Create the player
    player_name = "Edo"
    player_age = "24"
    player_gender = "M"
    player_pokemons = []
    player_items = []

    player = Trainer(player_name, player_age, player_gender, player_pokemons, player_items)

    # Add the starter more times
    starter = "bulbasaur"
    for i in range(0,3):
        player.add_pokemon(starter)

    # # Rename pokemon
    # player.rename_pokemon()
    
    # # Remove a pokemon
    # player.remove_pokemon()
    # View team    
    player.view_team()

    # # Encounter
    # player.enemy_encounter()

    # Rival
    if starter == "bulbasaur":
        rival_pokemons = pokedex["charmander"]
    elif starter == "squirtle":
        rival_pokemons = pokedex["bulbasaur"]
    else:
        rival_pokemons = pokedex["squirtle"]

    rival = Trainer(name="Tony", age="27", gender="Fluid", pokemons=rival_pokemons, items = [])

    return player, rival, pokedex, pokemon_movesets


if __name__ == "__main__":
    player, rival, pokedex, pokemon_movesets = main()



