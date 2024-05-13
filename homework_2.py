#==============================================================================
# GLOBALS

#------------------------------------------------------------------------------
# IMPORT LIBRARIES
import json
import numpy as np
import networkx as nx

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
    # NEW        
    def add_object(self,name,n_item):
        try:
            self.items[name] += n_item
        except KeyError:
            self.items[name] = n_item
            
        if self.items[name]>10:
            self.items[name] = 10
            
    # NEW
    def view_object(self):
        for item_num, item in enumerate(self.items.keys()):
            print(str(item_num+1) + ') ' + item +  ": " + str(self.items[item]))
            
    # NEW
    def remove_object(self):
        print('Which item do you want to remove?\n')
        self.view_object()
        item_num = int(input('\nRemove object number:\n')) -1
        item_qt = int(input('\nHow much do you want to remover:\n')) 
        
        if item_qt >= self.items[list(self.items.keys())[item_num]]:
            ask = input("\nYou are removing all the " + list(self.items.keys())[item_num] +" are you sure to continue? (y/n)\n" )
            if ask == "y":
                self.items[list(self.items.keys())[item_num]] = 0
        else:
            self.items[list(self.items.keys())[item_num]] -= item_qt

                
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
# FINITE STATE MACHINE

class FiniteStateMachine:
    def __init__(self):
        self.G = nx.MultiDiGraph()
        self.state = None
        self.start_state = None
        self.final_states = set()

    # Method to initialize the FSM to the start state
    def initialize(self):
        self.state = self.start_state

    # Method to add a state to the FSM
    def add_state(self, state, **kwargs):
        self.G.add_node(state, **kwargs)

    # Method to add a transition between two states of the FSM
    def add_transition(self, state1, state2, **kwargs):
        self.G.add_edge(state1, state2, **kwargs)

    # Method to remove a state from the FSM
    def remove_state(self, state):
        if state not in list(self.G):
            print("State", state, "is not present!")
            return False
        self.G.remove_node(state)

    # Method to remove a transition from the FSM
    def remove_transition(self, state1, state2):
        if state1 not in list(self.G):
            print("State", state1, "is not present!")
            return False
        if state2 not in list(self.G):
            print("State", state2, "is not present!")
            return False
        if (state1, state2) not in [e for e in self.G.edges]:
            print("Transition", (state1, state2), "is not present!")
            return False
        self.G.remove_edge(state1, state2)

    # Method to set the start state of the FSM
    def set_start_state(self, state):
        if state not in list(self.G):
            print("State", state, "is not present!")
            return False
        self.start_state = state

    # Method to set the final states of the FSM
    def set_final_states(self, states):
        for s in states:
            if s not in list(self.G):
                print("State", s, "is not present!")
                return False
        self.final_states = set(states)

    # Method to add a final state to the FSM
    def add_final_state(self, state):
        if state not in list(self.G):
            print("State", state, "is not present!")
            return False
        self.final_states.add(state)

    # Method to remove a final state from the FSM
    def remove_final_state(self, state):
        if state not in self.final_states:
            print("State", state, "is not present!")
            return False
        self.final_states.remove(state)

    # Method to reset the final states of the FSM
    def clear_final_states(self):
        self.final_states = set()

    # Method to extract one or more attributes from the current state of the FSM
    def get_state_attributes(self, attr=None):
        if not attr:
            return self.G.nodes[self.state]
        else:
            return self.G.nodes[self.state][attr]

    # Method to extract one or more attributes from the transition between
    # the current state and the target state
    def get_transition_attributes(self, target, attr=None):
        if not attr:
            return self.G[self.state][target][0]
        else:
            return self.G[self.state][target][0][attr]

    # Method to run the current state of the FSM
    def eval_current(self, *args, run='run', **kargs):
        method = getattr(self.state, run, None)
        if callable(method):
            method(*args, **kargs)

    # Method to perform the transition between the current state and the target state
    def do_transition(self, target, *args, attr='fun', **kargs):
        if attr in self.G[self.state][target][0]:
            self.G[self.state][target][0][attr](*args, **kargs)
        self.state = target

    # Method that returns the list of possible transitions from the current state
    def possible_transitions(self):
        return [n for n in self.G.neighbors(self.state)]

    # Method to identify the next transition of the FSM using the state update method
    def update(self, *args, update='update', **kargs):
        choices = self.possible_transitions()
        if not choices:
            print("No transition possible, machine halting.")
            return None
        elif len(choices) == 1:
            return choices[0]
        elif callable(getattr(self.state, update, None)):
            method = getattr(self.state, update, None)
            return method(choices, *args, **kargs)
        else:
            print("Update rule is undefined, machine halting.")
            return None

    # Method to draw the FSM and, eventually, visualize the current state of the FSM
    def draw(self, show_current_state=True, **kwds):
        if show_current_state:
            nodes = list(self.G)
            colors = ['b']*len(nodes)
            colors[nodes.index(self.state)] = 'g'
            nx.draw(self.G, with_labels=True,
                    node_color = colors,
                    connectionstyle='arc3, rad = 0.1', **kwds)
        else:
            nx.draw(self.G, with_labels=True,
                    connectionstyle='arc3, rad = 0.1', **kwds)
        # plt.show()


# Template of the State class for the FSM
class State:
    def __init__(self, name=None):
        self.name = name

    # Method to perform the operation of the current state of the FSM
    # (used by .eval_current() method of the FSM)
    def run(self, *args, **kargs):
        pass

    # Method to select the next state of the FSM
    # (used by .update() method of the FSM)
    def update(self, choices, *args, **kargs):
        pass
#==============================================================================
# MAIN
def main():
    print('Welcome to the Pokèmon world\n')

    # Create the player
    player_name = "Edo"
    player_age = "24"
    player_gender = "M"
    player_pokemons = []
    player_items = dict()

    player = Trainer(player_name, player_age, player_gender, player_pokemons, player_items)

    # Add the starter more times
    starter = "bulbasaur"
    player.add_pokemon(starter)

    # Add item
    player.add_object(name="Potion", n_item=10)
    player.add_object(name="Pokeball", n_item=10)
    
    # player.view_object()
    player.remove_object()
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



