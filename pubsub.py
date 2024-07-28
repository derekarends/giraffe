from typing import Callable, Dict, List, Any

class Pubsub:
    def __init__(self) -> None:
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event_type: str, data: Any) -> None:
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(data)

# Example usage
pubsub = Pubsub()

def handle_event(data: Any) -> None:
    print(f"Event received with data: {data}")

# Subscribe to an event
pubsub.subscribe("test_event", handle_event)

# Publish an event
pubsub.publish("test_event", {"key": "value"})

class MathAgent:
    def __init__(self, pubsub: Pubsub) -> None:
        self.pubsub = pubsub
        # self.pubsub.subscribe("add_stuff", self.add)


    def handle_event(data: Any) -> None: # type: ignore
        print(f"Event received with data: {data}")
    def add(self, a: int, b: int) -> int:
        result = a + b
        self.pubsub.publish("math_result", result)
        return result