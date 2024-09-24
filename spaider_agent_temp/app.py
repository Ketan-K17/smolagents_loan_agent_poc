from langchain_core.runnables.config import RunnableConfig

# LOCAL IMPORTS.
from spaider_agent_temp.graph import create_graph, compile_graph, print_stream
from spaider_agent_temp.prompts.prompts import FS_MANAGER_PROMPT



config = RunnableConfig(recursion_limit=10)
print(config)

if __name__ == "__main__":
    # creating graph workflow instance and then compiling it.
    verbose = True
    builder = create_graph()
    graph = compile_graph(builder)
        
    # infinite loop to take user input and print the output stream.
    while True:
        user_input = input("############# User: ")
        print_stream(graph.stream({"messages": [("system", FS_MANAGER_PROMPT), ("user", user_input)]}, stream_mode="values", config=config))
