import inspect
from typing import Callable, Any, Literal, get_type_hints
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam

class Tool:
    """
    A tool that can be used in a workflow.
    """
    name: str

    def __init__(self, func: Callable[..., Any], schema: ChatCompletionToolParam):
        """
        Initialize a tool.
        """
        self.name = func.__name__
        self.func = func
        self.schema = schema

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Make the tool callable.
        """
        return self.func(*args, **kwargs)


class Toolbox:
    """
    A collection of tools.
    """
    def __init__(self):
        self.tools: list[Tool] = []

    def add_tool(self, tool: Tool) -> "Toolbox":
        """
        Add a tool to the toolbox.

        Args:
            tool: The tool to add.
        """
        self.tools.append(tool)
        return self

    def get_tool(self, name: str | None) -> Tool:
        """
        Get a tool by name.

        Args:
            name: The name of the tool to get.
        """
        if name is None:
            raise ValueError("Tool name must be provided")
        
        for tool in self.tools:
            if tool.name == name:
                return tool
        raise ValueError(f"Tool {name} not found")

def tool(func: Callable[..., Any]) -> Tool:
    """
    Decorator to create a Tool from a function.
    """
    schema = generate_schema(func)
    return Tool(func, schema)


def infer_param_type(annotation: Any) -> str:
    """
    Infer the JSON schema type from a Python type annotation.
    """
    if annotation == int:
        return "integer"
    elif annotation == float:
        return "number"
    elif annotation == bool:
        return "boolean"
    elif annotation == str:
        return "string"
    else:
        return "string"

def generate_schema(func: Callable[..., Any]) -> ChatCompletionToolParam:
    """
    Generate a JSON schema for a function.

    Args:
        func: The function to generate a schema for.
    """
    # Parse the function signature
    sig = inspect.signature(func)
    parameters = sig.parameters
    type_hints = get_type_hints(func)

    # Parse the function docstring
    docstring = inspect.getdoc(func) or ""
    doc_lines = docstring.split("\n")
    description = doc_lines[0] if doc_lines else ""
    param_descriptions: dict[str, str] = {}
    for line in doc_lines[1:]:
        if ":" in line:
            param, desc = line.split(":", 1)
            if desc.strip() != "":
                param_descriptions[param.strip()] = desc.strip()

    # Build the schema
    properties: dict[str, object] = {}
    required: list[str] = []
    for param_name, param in parameters.items():
        annotation = type_hints.get(param_name, str)
        param_type = infer_param_type(type_hints.get(param_name, str))
        property_schema: dict[str, str | list[str]] = {
            "type": param_type,
            "description": param_descriptions.get(param_name, "")
        }
        
        if hasattr(annotation, '__origin__') and annotation.__origin__ == Literal:
            property_schema["enum"] = list(type_hints[param_name].__args__)

        properties[param_name] = property_schema
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
    }
