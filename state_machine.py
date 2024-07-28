from collections import defaultdict
from typing import Dict, DefaultDict
from pydantic import BaseModel
from abc import ABC, abstractmethod

class State(BaseModel, ABC):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """

    id: str

    def __init__(self, id: str):
        assert id, "State id cannot be empty"
        super().__init__(id=id)
        print('Processing current state:', str(self))

    class Config:
        extra = 'allow'

    @abstractmethod
    def on_event(self, event: str) -> 'State':
        """
        Handle events that are delegated to this State.
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__

    def __eq__(self, other: object) -> bool:
        """
        Checks if two State objects are equal by comparing their names.
        """
        if isinstance(other, State):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        """
        Returns the hash of the State object based on its name.
        """
        return hash(self.id)

class Transition:
    def __init__(self, state: State, event: str, next_state: State):
        self.state = state
        self.event = event
        self.next_state = next_state

    def __repr__(self):
        return f"Transition: {self.state} -> {self.event} -> {self.next_state}"


class StateMachine:
    def __init__(self, initial_state: State):
        self.current_state = initial_state
        self.transitions: DefaultDict[State, Dict[str, State]] = defaultdict(dict)

    def add_transition(self, state: State, event: str, next_state: State) -> 'StateMachine':
        if state in self.transitions and event in self.transitions[state]:
            raise ValueError(f"Transition for event '{event}' in state '{state}' already exists")
        self.transitions[state][event] = next_state
        return self

    def on_event(self, event: str) -> 'StateMachine':
        if self.current_state in self.transitions and event in self.transitions[self.current_state]:
            self.current_state = self.transitions[self.current_state][event]
            return self
        else:
            raise ValueError(f"No transition for event '{event}' in state '{self.current_state}'")
    
    @property
    def state(self):
        return self.current_state
