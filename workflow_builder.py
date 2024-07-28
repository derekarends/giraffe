from typing import Dict
from openai import OpenAI
from workflow_agent import TransitionFunction, WorkflowAgent, INIT


class WorkflowAgentBuilder:
    def __init__(self):
        self._system_message = ""
        self._transitions: Dict[str, Dict[str, TransitionFunction]] = dict()

    def add_llm(self, client: OpenAI, model: str):
        self._client = client
        self._model = model
        return self

    def add_system_message(self, message: str):
        self._system_message = message
        return self

    def add_state_and_transitions(self, state_name: str, transition_functions: set[TransitionFunction]):
        if state_name in self._transitions:
            raise Exception(f"State {state_name} transition already defined")
        self._transitions[state_name] = {
            func.__name__: func for func in transition_functions
        }
        return self

    def add_end_state(self, state_name: str):
        if state_name in self._transitions:
            raise Exception(f"State {state_name} already defined")
        self._transitions[state_name] = {}
        return self

    def build(self) -> WorkflowAgent:
        if INIT not in self._transitions:
            raise Exception(f"Must define {INIT} state")
        if not self._client:
            raise Exception("Must define client")
        if not self._model:
            raise Exception("Must define model")
        
        return WorkflowAgent(
            client=self._client,
            model=self._model,
            goal=self._system_message, 
            transitions=self._transitions
        )