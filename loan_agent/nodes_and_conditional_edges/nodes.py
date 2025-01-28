import json
import logging
import os
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, AnyMessage
from dotenv import load_dotenv
from smolagents import ToolCallingAgent, HfApiModel


'''LOCAL IMPORTS'''
from schemas import State
from prompts.prompts import PROMPT_PARSER_PROMPT, API_CALL_EXECUTOR_PROMPT
from models.chatgroq import BuildChatGroq
from tools.api_caller import APICallerTool
from tools.query_chromadb import ChromaDBQueryTool

load_dotenv()

# list of tools
make_api_call = APICallerTool()
query_chromadb = ChromaDBQueryTool()
toolkit = [make_api_call, query_chromadb]

# choosing llm, creating agent.
model_id = "meta-llama/Llama-3.3-70B-Instruct"
model = HfApiModel(model_id=model_id)   
empty_prompt = """{{managed_agents_descriptions}}"""
agent = ToolCallingAgent(model=model, tools=toolkit, system_prompt=empty_prompt)

# node definitions
def prompt_parser(state: State) -> State:
    """
    Reads the user prompt and returns a list of docs from the chromadb vectorstore that point to the right API request info.
    """
    user_prompt = state["user_prompt"]
    sys_prompt = PROMPT_PARSER_PROMPT
    # Combine system prompt with user prompt
    combined_prompt = sys_prompt + user_prompt
    # Write the combined prompt to a file
    output_path = "/Users/ketankunkalikar/Desktop/tmt/loan_agent_poc/loan_agent/outputs/prompt_parser.txt"
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"HERE'S THE COMBINED PROMPT: {combined_prompt}\n\n\n")
    except Exception as e:
        logging.error(f"Failed to write prompt to file: {str(e)}")

    # Call the smolagent
    response = agent.provide_final_answer(combined_prompt)

    # Extract vectordb_query from response JSON
    try:
        response_dict = json.loads(response)
        vectordb_query = response_dict["vectordb_query"]
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {str(e)}")
        vectordb_query = ""
    except KeyError as e:
        logging.error(f"vectordb_query key not found in response: {str(e)}")
        vectordb_query = ""

    # Write vectordb_query to file
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"HERE'S THE VECTORDB QUERY: {vectordb_query}\n\n\n")
    except Exception as e:
        logging.error(f"Failed to write vectordb_query to file: {str(e)}")

    # call query_chromadb tool
    list_of_docs = query_chromadb(
            "/Users/ketankunkalikar/Desktop/tmt/loan_agent_poc/ingest_data/mychroma_db",  # Use path from config
            "sentence-transformers/all-MiniLM-L6-v2",  # Use model setting from config
            vectordb_query
            )
    
    # Add to state
    state["list_of_docs"] = list_of_docs

    # Write to file
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write("HERE'S THE LIST OF DOCS:\n")
            for i, doc in enumerate(list_of_docs, 1):
                f.write(f"{i}. {doc}\n")
            f.write("\n\n")
    except Exception as e:
        logging.error(f"Failed to write list of docs to file: {str(e)}")

    return state


def api_call_executor(state: State):
    """
    This function is used to create an API request given some context documents, and then firing that request.
    """
    list_of_docs = state["list_of_docs"]
    user_query = state["user_prompt"]
    sys_prompt = f"{API_CALL_EXECUTOR_PROMPT}Here is the user query: {user_query}Here is the list of documents: {list_of_docs}"
    
    output_path = "/Users/ketankunkalikar/Desktop/tmt/loan_agent_poc/loan_agent/outputs/api_call_executor.txt"
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"HERE'S THE SYSTEM PROMPT:\n{sys_prompt}\n\n\n")
    except Exception as e:
        logging.error(f"Failed to write prompt to file: {str(e)}")

    # call the llm
    response = agent.provide_final_answer(sys_prompt)

    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"HERE'S THE LLM RESPONSE:\n{response}\n\n\n")
    except Exception as e:
        logging.error(f"Failed to write LLM response to file: {str(e)}")

    response_json = json.loads(response)
    print(f"HERE'S THE RESPONSE JSON: {response_json}\n\n\n\n\n\n\n")

    api_request = response_json if isinstance(response_json, dict) else json.loads(response_json)
        
    # Create a complete API request with default values for missing fields
    complete_api_request = {
        'endpoint': api_request.get('endpoint'),
        'base_url': api_request.get('base_url'),
        'method': api_request.get('method', 'GET'),
        'params': api_request.get('params', {}),
        'data': api_request.get('data', {}),
        'headers': api_request.get('headers', {}),
        'json_data': api_request.get('json_data', {}),
        'timeout': api_request.get('timeout', 30)
    }

    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"HERE'S THE COMPLETE API REQUEST:\n{json.dumps(complete_api_request, indent=2)}\n\n\n")
    except Exception as e:
        logging.error(f"Failed to write API request to file: {str(e)}")
    
    # Call the API
    api_response = make_api_call.forward(**complete_api_request)
    
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"HERE'S THE API RESPONSE:\n{json.dumps(api_response, indent=2)}\n\n\n")
    except Exception as e:
        logging.error(f"Failed to write API response to file: {str(e)}")

    # Add natural language interpretation of API response
    interpretation_prompt = f"""Given the user's original question and the API response, please provide a natural language answer that addresses their query.

    User's question: {user_query}

    API Response: {api_response}

    Please interpret this API response and provide a clear, helpful answer to the user's question."""

    # Call the LLM for interpretation
    natural_language_response = agent.provide_final_answer(interpretation_prompt)

    print(f"HERE'S THE NATURAL LANGUAGE RESPONSE: {natural_language_response}\n\n\n\n\n\n\n")

    # Log the interpretation
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"NATURAL LANGUAGE INTERPRETATION:\n{natural_language_response}\n\n\n")
    except Exception as e:
        logging.error(f"Failed to write natural language interpretation to file: {str(e)}")

    return state