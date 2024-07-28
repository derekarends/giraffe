import json
from typing import Any
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

from messages import BaseMessage, SystemMessage, UserMessage
from tools import Tool, Toolbox


class Runner:
    """
    A runner that can run tools.
    """
    def __init__(self):
        self.toolbox: Toolbox = Toolbox()
        self.history: list[BaseMessage] = []

    def add_llm(self, client: Any, model: str) -> "Runner":
        """
        Add the client and model to the runner.

        Args:
            client: The client to add.
            model: The model to add.
        """
        self.client = client
        self.model = model
        return self
    
    def add_system_message(self, message: str) -> "Runner":
        """
        Add a system message to the runner.

        Args:
            message: The message to add.
        """
        self.system_message = SystemMessage(message)
        return self
    
    def add_user_message(self, message: str) -> "Runner":
        """
        Add a user message to the runner.

        Args:
            message: The message to add.
        """
        self.user_message = UserMessage(message)
        return self
    
    def add_history(self, history: list[BaseMessage]) -> "Runner":
        """
        Add a history of messages to the runner.

        Args:
            history: The history of messages to add.
        """
        self.history.extend(history)
        return self

    def add_tool(self, tool: Tool) -> "Runner":
        """
        Add a tool to the toolbox.

        Args:
            tool: The tool to add.
        """
        self.toolbox.add_tool(tool)
        return self
    
    def add_tools(self, toolbox: Toolbox) -> "Runner":
        """
        Add a list of tools to the toolbox.

        Args:
            tools: The tools to add.
        """
        self.toolbox.tools.extend(toolbox.tools)
        return self
    
    def run(self) -> list[Any]:
      messages = [msg.dict() for msg in [self.system_message] + self.history + [self.user_message]]
      completion = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        tools=[t.schema for t in self.toolbox.tools]
      )

      return self.call_tools(completion.choices[0].message.tool_calls)

    
    def call_tools(self, tool_calls: list[ChatCompletionMessageToolCall] | None) -> list[Any]:
        """
        Run a tool call.

        Args:
            tool_calls: The tool calls to run.
        """
        if tool_calls is None:
            return []

        results: list[Any] = []

        for tool_call in tool_calls:
            tool_call_func = tool_call.function.model_dump()
            tool_name: str | None = tool_call_func.get("name")
            function_args: str | None = tool_call_func.get("arguments")

            tool = self.toolbox.get_tool(tool_name)

            args: dict[str, Any] = {}
            if function_args is not None:
                args = json.loads(function_args)
            
            results.append(tool(**args))
      
        return results
