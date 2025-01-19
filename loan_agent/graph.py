from langgraph.graph import StateGraph, END, START
from langgraph.constants import END
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv

# LOCAL IMPORTS
from nodes_and_conditional_edges.nodes import prompt_parser, api_call_executor
from nodes_and_conditional_edges.conditional_edges import *
from tools import *
from schemas import State


load_dotenv()

def create_graph():
    # GRAPH INSTANCE
    builder = StateGraph(State)

    # ADD NODES TO THE GRAPH
    # dummy node
    builder.add_node("prompt_parser", prompt_parser)
    builder.add_node("api_call_executor", api_call_executor)


    # ADD EDGES/CONDITIONAL EDGES FOR THE GRAPH
    builder.add_edge(START, "prompt_parser")
    builder.add_edge("prompt_parser", "api_call_executor")
    builder.add_edge("api_call_executor", END)

    return builder

def compile_graph(builder):
    '''COMPILE GRAPH'''
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    return graph

def print_stream(stream):
    """Print all fields from the state, with fallback handling for empty messages"""
    for s in stream:
        print("\n=== State Update ===")
        
        # Handle messages separately with fallback for empty list
        if "messages" in s:
            if s["messages"]:  # If messages list is not empty
                message = s["messages"][-1]
                print("\nLatest Message:")
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
            else:
                print("\nMessages: []")
        
        # Print all other fields in the state
        for key, value in s.items():
            if key != "messages":  # Skip messages as we handled them above
                print(f"\n{key}:")
                print(value)
        
        print("\n" + "="*20)