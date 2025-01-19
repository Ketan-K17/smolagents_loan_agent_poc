from smolagents import Tool
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from typing import List

class ChromaDBQueryTool(Tool):
    name = "query_chromadb"
    description = """
    This tool queries a Chroma vector database using semantic search to retrieve relevant documents 
    based on a user query. It returns a list of document contents that best match the query."""
    inputs = {
        "chroma_db_path": {
            "type": "string",
            "description": "Path to the Chroma DB directory",
        },
        "llm_name": {
            "type": "string",
            "description": "Name of the embedding model to use (e.g., 'sentence-transformers/all-MiniLM-L6-v2')",
        },
        "user_query": {
            "type": "string",
            "description": "The user's query to search for in the database",
        }
    }
    output_type = "object"

    def forward(self, chroma_db_path: str, llm_name: str, user_query: str) -> List[str]:
        # Initialize the embedding function
        embedding_function = SentenceTransformerEmbeddings(model_name=llm_name)
        
        # Load Chroma DB from disk
        db = Chroma(persist_directory=chroma_db_path, embedding_function=embedding_function)
        
        # Perform similarity search
        docs = db.similarity_search(user_query, k=10)
        
        # Convert documents to list format
        return [doc.page_content for doc in docs]

chromadb_query_tool = ChromaDBQueryTool()

# Example usage:
if __name__ == "__main__":
    chroma_db_path = "/Users/ketankunkalikar/Desktop/tmt/spaider-agent-template/ingest_data/mychroma_db"
    llm_name = "sentence-transformers/all-MiniLM-L6-v2"
    user_query = "return every sentence the word base-url in it."
    
    retrieved_docs = chromadb_query_tool.forward(chroma_db_path, llm_name, user_query)
    
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"Document {i}:")
        print(f"Content: {doc}")  # Print full content
        print()