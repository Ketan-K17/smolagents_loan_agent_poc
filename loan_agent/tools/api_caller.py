from smolagents import Tool
import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin

class APICallerTool(Tool):
    name = "make_api_call"
    description = """
    This tool makes an API call with the given parameters and returns the response as a dictionary.
    It supports various HTTP methods and can handle different types of request data."""
    inputs = {
        "endpoint": {
            "type": "string",
            "description": "The API endpoint (e.g., '/api/v1/users')",
        },
        "base_url": {
            "type": "string",
            "description": "Base URL for the API (e.g., 'https://api.example.com')",
            "nullable": True
        },
        "method": {
            "type": "string",
            "description": "HTTP method ('GET', 'POST', 'PUT', 'DELETE', etc.)",
            "nullable": True
        },
        "params": {
            "type": "object",
            "description": "URL parameters to be added to the request",
            "nullable": True
        },
        "data": {
            "type": "object",
            "description": "Form-encoded data to be sent in the request body",
            "nullable": True
        },
        "headers": {
            "type": "object",
            "description": "HTTP headers to be sent with the request",
            "nullable": True
        },
        "json_data": {
            "type": "object",
            "description": "JSON data to be sent in the request body",
            "nullable": True
        },
        "timeout": {
            "type": "integer",
            "description": "Request timeout in seconds",
            "nullable": True
        }
    }
    output_type = "object"

    def forward(
        self,
        endpoint: str,
        base_url: Optional[str] = None,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        # Prepare the URL
        if base_url:
            # Remove trailing slash from base_url if it exists
            base_url = base_url.rstrip('/')
            # Remove leading slash from endpoint if it exists
            endpoint = endpoint.lstrip('/')
            url = f"{base_url}/{endpoint}"
        else:
            url = endpoint
        
        # Default headers if none provided
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                headers=headers,
                json=json_data,
                timeout=timeout
            )
            
            # Raise an error for bad status codes
            response.raise_for_status()
            
            # Convert response to dictionary before returning
            return {
                "status_code": response.status_code,
                "content": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "headers": dict(response.headers)
            }
            
        except requests.exceptions.RequestException as e:
            # Log the error here if needed
            print(f"API call failed: {str(e)}")
            raise


if __name__ == "__main__":
    api_caller_tool = APICallerTool()
    response = api_caller_tool.forward(
        base_url="https://api.wheretheiss.at/v1",
        endpoint="/satellites/25544",
        method="GET"
    )
    print(response)


