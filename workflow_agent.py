import json
from typing import Dict, Callable, Any, List


from function import create_definition, FunctionDefinition

from openai import OpenAI
from openai.types.chat.chat_completion_message import FunctionCall
from openai.types.chat import (
    ChatCompletionMessageParam,
    completion_create_params,
    ChatCompletionMessage,
)

TransitionFunction = Callable[..., str]
FUNCTION_NAME = "ActionSelector"
INIT = "INIT"
_CURRENT_STEPPING_AGENT = None

class WorkflowAgent:
    def __init__(
        self, 
        client: OpenAI,
        model: str,
        goal: str, 
        transitions: Dict[str, Dict[str, TransitionFunction]]
    ):
        if INIT not in transitions:
            raise Exception(f"Must define {INIT} state")
        
        self._current_state = INIT
        self._next_state = None
        self._client = client
        self._model = model
        self._messages: List[ChatCompletionMessageParam | ChatCompletionMessage] = []
        self._messages.append({"role": "system", "content": goal})
        self._func_defs: Dict[TransitionFunction, FunctionDefinition] = dict()
        
        self._transitions: Dict[str, Dict[str, TransitionFunction]] = transitions
        for name_dict in self._transitions.values():
            for func in name_dict.values():
                if func not in self._func_defs:
                    self._func_defs[func] = create_definition(func, goal)

    @property
    def current_state(self):
        return self._current_state

    @property
    def messages(self) -> List[ChatCompletionMessageParam | ChatCompletionMessage]:
        return self._messages

    @property
    def last_message(self) -> ChatCompletionMessageParam  | ChatCompletionMessage | None:
        if len(self._messages) < 1:
            return None
        return self._messages[-1]

    def add_message(self, message: ChatCompletionMessageParam | ChatCompletionMessage):
        self._messages.append(message)

    def trigger(self, function_call: str, args: List[Any]) -> str:
        transition_func = self._transitions[self._current_state].get(function_call)
        if transition_func:
            try:
                result = transition_func(*args)
            except Exception as e:
                # Function raised an exception.
                # No state update and returning exception.
                return str(e)
            if self._next_state:
                self._current_state = self._next_state
                self._next_state = None
            return result
        # Model trying to call something that is not allowed
        # State stays the same and let's just report back illegal move.
        return f"Illegal function call '{function_call}' in current state."
    
    def function_def_action_selector(self) -> completion_create_params.Function:
        actions: list[str] = []
        action_descriptions: list[str] = []
        argument_descriptions: list[str] = []

        for func in self._transitions[self._current_state].values():
            definition = self._func_defs[func]
            actions.append(definition["function_name"])
            action_descriptions.append(
                f"{definition["function_name"]}:{definition["function_description"]}"
            )
            argument_descriptions.append(
                f"For {definition['function_name']} argument: {definition['argument_description']}"
            )
        return {
            "description": "ActionSelector is a tool that selects next action",
            "name": "ActionSelector",
            "parameters": {
                "type": "object",
                "properties": {
                    "thinking": {
                        "type": "string",
                        "description": (
                            "Reflection about latest learnings."
                            "Assume last function result content will be purged to save space."
                            "Logical thinking about the problem leading to taking this action."
                        ),
                    },
                    "action": {
                        "type": "string",
                        "enum": actions,
                        "description": "\n".join(action_descriptions),
                    },
                    "argument": {
                        "type": "string",
                        "description": "\n".join(argument_descriptions),
                    },
                },
                "required": ["thinking", "action", "argument"],
            },
        }

    def run(self, callback: Callable[[str], Any] | None = None) -> str:
        result = "No result"
        while self._transitions[self.current_state]:
            result = self.step()
            if callback:
                callback(result)
        return result

    def step(self):
        global _CURRENT_STEPPING_AGENT
        response = self._client.chat.completions.create(
            model=self._model,
            messages=self._messages,  # type: ignore
            functions=[self.function_def_action_selector()],
            function_call={"name": "ActionSelector"},
        )
        assert response.usage, "No usage in response"
        print("=" * 80)
        print(
            f"tokens: {response.usage.total_tokens} total; {response.usage.completion_tokens} completion; {response.usage.prompt_tokens} prompt"
        )
        print("=" * 80)
        msg = response.choices[0].message
        assert msg.function_call, "No function call in response"
        _CURRENT_STEPPING_AGENT = self # type: ignore
        res = self._execute_function_call(msg.function_call)
        _CURRENT_STEPPING_AGENT = None # type: ignore
        print(res[:120] + ("..." if len(res) > 120 else ""))
        self.add_message(msg)
        self.add_message(
            {"role": "function", "name": msg.function_call.name, "content": res}
        )
        return res

    def _execute_function_call(self, function_call: FunctionCall) -> str:
        if function_call.name != FUNCTION_NAME:
            return f"Error: function {function_call.name} does not exist"
        
        args = json.loads(function_call.arguments)
        for key in args:
            print(f'{key}: {args[key]}')

        action = args["action"]
        argument = args["argument"]
        return self.trigger(action.lower(), [argument])


def set_next_state(state: str):
    if _CURRENT_STEPPING_AGENT:
        _CURRENT_STEPPING_AGENT._next_state = state # type: ignore