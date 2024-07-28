# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional, Tuple

# class Node(BaseModel):
#     id: str
#     value: Optional[str] = None
    
#     def __init__(self, id: str, value: Optional[str] = None):
#         assert id, "Node id cannot be empty"
#         super().__init__(id=id, value=value)

#     def __repr__(self):
#         """
#         Leverages the __str__ method to describe the State.
#         """
#         return self.__str__()

#     def __str__(self):
#         """
#         Returns the name of the State.
#         """
#         return self.__class__.__name__

#     def __eq__(self, other: object) -> bool:
#         """
#         Checks if two State objects are equal by comparing their names.
#         """
#         if isinstance(other, Node):
#             return self.id == other.id
#         return False

#     def __hash__(self) -> int:
#         """
#         Returns the hash of the State object based on its name.
#         """
#         return hash(self.id)
    
#     def run(self) -> None:
#         print("Running node", self.id)

# class Edge(BaseModel):
#     source: str
#     target: str

# START = "START"
# END = "END"

# class Graph(BaseModel):
#     nodes: Dict[str, Node] = Field(default_factory=dict)
#     edges: List[Edge] = Field(default_factory=list)

#     def add_node(self, node: Node) -> 'Graph':
#         if node.id in self.nodes:
#             raise ValueError(f"Node with id {node.id} already exists.")
#         self.nodes[node.id] = node
#         return self

#     def add_edge(self, edge: Edge) -> 'Graph':
#         if edge.source not in self.nodes or edge.target not in self.nodes:
#             raise ValueError("Both source and target nodes must exist.")
#         if self._creates_cycle(edge):
#             raise ValueError("Adding this edge would create a cycle.")
#         self.edges.append(edge)
#         return self

#     def _creates_cycle(self, new_edge: Edge) -> bool:
#         # Perform a DFS to check for cycles
#         visited: set[str] = set()
#         stack: List[Tuple[str, Optional[str]]] = [(new_edge.source, None)]  # (current_node, previous_node)

#         while stack:
#             current_node, previous_node = stack.pop()
#             if current_node == new_edge.target and previous_node is not None:
#                 if self._has_exit_path(new_edge.target, new_edge.source):
#                     continue
#                 return True
#             if current_node not in visited:
#                 visited.add(current_node)
#                 stack.extend((e.target, current_node) for e in self.edges if e.source == current_node)
        
#         return False

#     def _has_exit_path(self, start_node: str, avoid_node: str) -> bool:
#         # Perform a DFS to check for an exit path that avoids the specified node
#         visited: set[str] = set()
#         stack = [start_node]

#         while stack:
#             current_node = stack.pop()
#             if current_node == avoid_node:
#                 continue
#             if current_node not in visited:
#                 visited.add(current_node)
#                 stack.extend(e.target for e in self.edges if e.source == current_node)
        
#         return avoid_node not in visited

# # Example usage
# dag = Graph()

# # Add nodes
# node_a = Node(id="A")
# node_b = Node(id="B")
# node_c = Node(id="C")

# dag.add_node(node_a)
# dag.add_node(node_b)
# dag.add_node(node_c)

# # Add edges
# edge_ab = Edge(source="A", target="B")
# edge_bc = Edge(source="B", target="C")

# dag.add_edge(edge_ab)
# dag.add_edge(edge_bc)

# # This would raise an error because it creates a cycle
# # edge_ca = Edge(source="C", target="A")
# # dag.add_edge(edge_ca)

from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from IPython.display import display, Markdown # type: ignore

class Node(BaseModel, ABC):
    id: str
    value: Optional[str] = None

    @abstractmethod
    def decide_next_edge(self, edges: List['Edge']) -> Optional['Edge']:
        pass

class Edge(BaseModel):
    source: str
    target: str

class Graph(BaseModel):
    nodes: Dict[str, Node] = Field(default_factory=dict)
    edges: List[Edge] = Field(default_factory=list)

    def add_node(self, node: Node) -> 'Graph':
        if node.id in self.nodes:
            raise ValueError(f"Node with id {node.id} already exists.")
        self.nodes[node.id] = node
        return self

    def add_edge(self, edge: Edge) -> 'Graph':
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("Both source and target nodes must exist.")
        if self._creates_cycle(edge):
            raise ValueError("Adding this edge would create a cycle.")
        self.edges.append(edge)
        return self

    def _creates_cycle(self, new_edge: Edge) -> bool:
        """
        Perform a DFS to check for cycles
        """
        visited: set[str] = set()
        stack: List[Tuple[str, Optional[str]]] = [(new_edge.source, None)]

        while stack:
            current_node, previous_node = stack.pop()
            if current_node == new_edge.target and previous_node is not None:
                if self._has_exit_path(new_edge.target, new_edge.source):
                    continue
                return True
            if current_node not in visited:
                visited.add(current_node)
                stack.extend((e.target, current_node) for e in self.edges if e.source == current_node)
        
        return False

    def _has_exit_path(self, start_node: str, avoid_node: str) -> bool:
        """
        Perform a DFS to check for an exit path that avoids the specified node
        """
        visited: set[str] = set()
        stack = [start_node]

        while stack:
            current_node = stack.pop()
            if current_node == avoid_node:
                continue
            if current_node not in visited:
                visited.add(current_node)
                stack.extend(e.target for e in self.edges if e.source == current_node)
        
        return avoid_node not in visited

    def execute(self, start_node_id: str) -> None:
        """
        Execute the graph starting from the specified node
        """
        current_node_id = start_node_id
        while current_node_id:
            current_node = self.nodes[current_node_id]
            print(f"Executing node {current_node_id}")
            next_edge = current_node.decide_next_edge([e for e in self.edges if e.source == current_node_id])
            if next_edge:
                current_node_id = next_edge.target
            else:
                break
            
    def draw_graph(self) -> None:
        mermaid_str = "```mermaid\ngraph TD\n"
        for edge in self.edges:
            mermaid_str += f"    {edge.source} --> {edge.target}\n"
        mermaid_str += "```"
        display(Markdown(mermaid_str))



class DecisionNode(Node):
    def __init__(self, id: str):
        super().__init__(id=id)

    def decide_next_edge(self, edges: List[Edge]) -> Optional[Edge]:
        return edges[0] if edges else None


class MathNode(Node):
    def __init__(self, id: str, value: str):
        super().__init__(id=id, value=value)

    def decide_next_edge(self, edges: List[Edge]) -> Optional[Edge]:
        return edges[0] if edges else None