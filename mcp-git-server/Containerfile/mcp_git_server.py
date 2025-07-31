"""
Proper MCP Server for OpenHands Git Tools
Serves FastMCP directly without FastAPI wrapper
Assumes OpenHands library is available in /app
"""

import asyncio
import os
import sys
from unittest.mock import Mock

# Add the app directory to Python path
sys.path.insert(0, '/app')

# Import OpenHands components
from openhands.core.logger import openhands_logger as logger
from openhands.integrations.provider import ProviderToken
from openhands.integrations.service_types import ProviderType
from pydantic import SecretStr

# Set up authentication mocks BEFORE importing MCP server
import openhands.server.user_auth as user_auth_module
import openhands.server.routes.mcp as mcp_module

# Create proper async mock functions
async def mock_get_provider_tokens(request):
    """Mock provider tokens - return GitHub token from environment"""
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        return {
            ProviderType.GITHUB: ProviderToken(
                token=SecretStr(github_token),
                user_id="mcp-server-user",
                host="github.com"
            )
        }
    return {}

async def mock_get_access_token(request):
    """Mock access token - return GitHub token"""
    return os.getenv('GITHUB_TOKEN', '')

async def mock_get_user_id(request):  
    """Mock user ID"""
    return "mcp-server-user"

def mock_get_http_request():
    """Return a minimal mock request"""
    mock_request = Mock()
    mock_request.headers = {
        'X-OpenHands-ServerConversation-ID': 'mcp-server-session'
    }
    return mock_request

# Mock the conversation store to avoid metadata file issues
class MockConversationStore:
    async def get_metadata(self, conversation_id):
        mock_metadata = Mock()
        mock_metadata.pr_number = []
        return mock_metadata
        
    async def save_metadata(self, metadata):
        pass

class MockConversationStoreImpl:
    @staticmethod
    async def get_instance(config, user_id):
        return MockConversationStore()

# Patch all the authentication and storage functions
user_auth_module.get_provider_tokens = mock_get_provider_tokens
user_auth_module.get_access_token = mock_get_access_token  
user_auth_module.get_user_id = mock_get_user_id
mcp_module.get_http_request = mock_get_http_request
mcp_module.get_provider_tokens = mock_get_provider_tokens
mcp_module.get_access_token = mock_get_access_token
mcp_module.get_user_id = mock_get_user_id
mcp_module.ConversationStoreImpl = MockConversationStoreImpl

logger.info("MCP Server authentication mocks configured")
logger.info(f"GitHub token available: {bool(os.getenv('GITHUB_TOKEN'))}")

# NOW import the MCP server after mocks are set up
from openhands.server.routes.mcp import mcp_server

if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "3000"))
    
    logger.info(f"Starting OpenHands MCP Server on {host}:{port}")
    
    try:
        # Try to run the FastMCP server directly with HTTP transport
        # This should serve the proper MCP protocol at the root path
        logger.info("Starting FastMCP server with HTTP transport...")
        
        # Get the HTTP app and serve it directly
        mcp_app = mcp_server.http_app()
        
        import uvicorn
        uvicorn.run(
            mcp_app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start FastMCP server directly: {e}")
        
        # Fallback: try running with uvicorn and manual mounting
        try:
            from fastapi import FastAPI
            
            app = FastAPI(title="OpenHands MCP Server")
            
            @app.get("/health")
            async def health():
                return {"status": "healthy", "service": "openhands-mcp-server"}
            
            # Mount MCP at root to avoid path conflicts
            mcp_app = mcp_server.http_app()
            app.mount("/mcp", mcp_app)
            
            logger.info("Fallback: serving with FastAPI wrapper")
            
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info",
                access_log=True
            )
            
        except Exception as e2:
            logger.error(f"Fallback also failed: {e2}")
            raise