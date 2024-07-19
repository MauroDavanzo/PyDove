import networkx as nx
import matplotlib.pyplot as plt

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
        pass
    
import time

class Semaphore_color(State):
    previous = None
    counter = 0

    def run(self):
        print(self.name)

    def update(self, choices):
        if Semaphore_color.previous is red:
            return green
        elif Semaphore_color.previous is green:
            return red

    def __str__(self):
        return '[Semaphore: ' + self.name + ']'

    def __repr__(self):
        return str(self)


green = Semaphore_color('green')
yellow = Semaphore_color('yellow')
red = Semaphore_color('red')

def main():

    Machine = FiniteStateMachine()

    Machine.add_state(green)
    Machine.add_state(yellow)
    Machine.add_state(red)

    Machine.add_transition(green, yellow, fun=lambda t: time.sleep(t), dur=0)
    Machine.add_transition(yellow, red, fun=lambda t: time.sleep(t), dur=0)
    Machine.add_transition(red, yellow, fun=lambda t: time.sleep(t), dur=0)
    Machine.add_transition(yellow, green, fun=lambda t: time.sleep(t), dur=0)

    Machine.set_start_state(red)
    Machine.initialize()

    # Machine.draw()

    max_count = 3
    exit = False
    while not exit:
        if Machine.state == red:
            Semaphore_color.counter += 1
            print("Round:", Semaphore_color.counter)
            if Semaphore_color.counter >= max_count:
                print("Max count reached!")
                Machine.add_final_state(red)

        Machine.eval_current()

        target = None
        if Machine.state not in Machine.final_states:
            target = Machine.update()
            Semaphore_color.previous = Machine.state

        if not target:
            print("EXIT FROM FSM")
            exit = True
        else:
            Machine.do_transition(target, Machine.get_transition_attributes(target, 'dur'))
            Machine.draw()

    return Machine
machine = main()
