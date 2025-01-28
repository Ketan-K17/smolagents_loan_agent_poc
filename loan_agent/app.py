# from langchain_core.runnables.config import RunnableConfig

# # LOCAL IMPORTS.
# from graph import create_graph, compile_graph, print_stream

# config = RunnableConfig(recursion_limit=10, configurable={
#         "thread_id": "1",
#     })
# print(config)

# if __name__ == "__main__":
#     builder = create_graph()
#     graph = compile_graph(builder)
#     print(graph.get_graph().draw_mermaid())
    
#     user_input = input("############# User: ")
#     print_stream(graph.stream({"user_prompt": user_input}, stream_mode="values", config=config))

from smolagents import CodeAgent, HfApiModel

model = HfApiModel(model_id="meta-llama/Llama-3.3-70B-Instruct")
agent = CodeAgent(model=model, tools=[])
answer = agent.provide_final_answer("What is the result of 2 power 3.7384?")
print(answer)