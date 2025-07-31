# OpenHands Headless Commands for Pod/Session Creation and GitHub Repo Cloning

This document provides the essential commands to replicate OpenHands' UI flow in headless mode for creating pods/sessions and cloning GitHub repositories.

## Overview

OpenHands creates pods/sessions and clones GitHub repositories through a multi-step process:

1. **Session Initialization** - Creates runtime environment (Docker/Kubernetes pod)
2. **Repository Cloning** - Clones GitHub repo into the workspace
3. **Environment Setup** - Runs setup scripts and configures workspace
4. **Agent Initialization** - Starts the agent controller

## Key Commands

### 1. Basic Headless Session with GitHub Repo

```bash
# Clone and work on a specific GitHub repository
# Set environment variable for GitHub token
export GITHUB_TOKEN="your-github-token"

openhands \
  --sandbox.selected_repo "owner/repository-name" \
  --task "Your task description here" \
  --runtime docker \
  --max-iterations 50

# Example
export GITHUB_TOKEN="your-github-token"
openhands \
  --sandbox.selected_repo "microsoft/vscode" \
  --task "Fix the TypeScript compilation error in src/vs/editor" \
  --runtime docker \
  --max-iterations 30
```

### 2. Programmatic API Usage

#### Option A: Using AgentSession (Recommended - UI Mode Approach)

```python
# COPY AND PASTE THESE BLOCKS ONE AT A TIME INTO PYTHON TERMINAL

# Block 1: Import and setup - Simple approach
import asyncio
import os
from openhands.core.config import OpenHandsConfig
from openhands.core.config.sandbox_config import SandboxConfig
from openhands.core.config.llm_config import LLMConfig
from openhands.core.main import run_controller
from openhands.core.setup import create_runtime, initialize_repository_for_runtime
from openhands.events.action import MessageAction
from openhands.core.config.mcp_config import OpenHandsMCPConfigImpl

# NOTE: Make sure you have FastMCP installed for the MCP server:
# pip install fastmcp

# Block 2: Environment variables (including verbose logging)
os.environ['GITHUB_TOKEN'] = 'YOUR_GITHUB_TOKEN'  # Replace with your actual token
os.environ['LLM_API_KEY'] = 'YOUR_LLM_API_KEY'    # Replace with your actual API key  
os.environ['LLM_MODEL'] = 'gemini/gemini-2.5-pro'

# Enable real-time verbose logging
os.environ['LOG_ALL_EVENTS'] = 'true'     # Shows all events in real-time
os.environ['DEBUG'] = 'true'              # Enables debug logging everywhere  
os.environ['DEBUG_RUNTIME'] = 'true'      # Shows container logs
os.environ['LOG_LEVEL'] = 'DEBUG'         # Explicit debug level

# Block 3: Configuration setup with MCP support
session_name = "ci"

# Create main config with MCP support enabled
config = OpenHandsConfig(
    runtime='kubernetes', 
    max_iterations=50, 
    workspace_base="/workspace", 
    sandbox=SandboxConfig(
        selected_repo='rhoai-genaiops/genaiops-helmcharts', 
        runtime_container_image='docker.all-hands.dev/all-hands-ai/runtime:0.49-nikolaik'
    ),
)

llm_config = LLMConfig(model='gemini/gemini-2.5-pro', api_key=os.environ['LLM_API_KEY'])
config.set_llm_config(llm_config)

# Enable MCP tools (this is key!)
agent_config = config.get_agent_config()
agent_config.enable_mcp = True
config.set_agent_config(agent_config)

# Configure external MCP server (your dedicated MCP server with Git tools)
config.mcp_host = "openhands-mcp-git-server.openhands-coherence-pipeline.svc.cluster.local:3000/mcp"

# Block 4: Simple session runner with MCP fix (copy as one block)
async def run_session(): 
    # Create runtime and connect
    runtime = create_runtime(config, sid=session_name, headless_mode=True)
    
    # Fix the SHTTP server bug: manually add external MCP server
    if config.mcp_host:
        shttp_server, _ = OpenHandsMCPConfigImpl.create_default_mcp_server_config(
            config.mcp_host, config, None
        )
        if shttp_server:
            # shttp_server.url = shttp_server.url.replace('http://', 'https://')
            runtime.config.mcp.shttp_servers.append(shttp_server)
            print(f"Added external MCP server: {shttp_server.url}")
    
    await runtime.connect()
    repo_directory = initialize_repository_for_runtime(runtime, selected_repository=config.sandbox.selected_repo)
    print(f"Repository cloned to: {repo_directory}")
    
    # Define the task
#     initial_action = MessageAction(content="""
# Please look at the full codebase and then update the README with the following improvements, if they make sense:
# * correct any typos that you find
# * add missing language annotations on codeblocks  
# * if there are references to other files or other sections of the README, turn them into links
# * make sure the readme has an h1 title towards the top
# * make sure any existing sections in the readme are appropriately separated with headings
# * This repo was created from the CAI team

# If there are no obvious ways to improve the README, make at least one small change to make the wording clearer or friendlier.

# After that, please push the changes to GitHub and open a pull request. Please create a meaningful branch name that describes the changes. If a pull request template exists in the repository, please follow it when creating the PR description.
# """)
  initial_action = MessageAction(content="""
Please create a license file.

After that, please push the changes to GitHub and open a pull request. Please create a meaningful branch name that describes the changes. If a pull request template exists in the repository, please follow it when creating the PR description.
""")
    
    # Run with the fixed MCP configuration
    state = await run_controller(
        config=config, 
        initial_user_action=initial_action, 
        runtime=runtime, 
        sid=session_name, 
        headless_mode=True, 
        fake_user_response_fn=lambda state: "continue"
    )
    return state

# Block 5: Conversation printer function (copy as one block)  
def print_conversation(state): print("=" * 80, "CONVERSATION SUMMARY", "=" * 80, sep="\n"); [print(f"\n🤖 AGENT: {event.content}") if hasattr(event, 'action') and event.action.value == 'message' and hasattr(event, 'content') and hasattr(event, 'wait_for_response') and event.wait_for_response else print(f"\n👤 USER: {event.content}") if hasattr(event, 'action') and event.action.value == 'message' and hasattr(event, 'content') else print(f"\n💻 COMMAND: {event.command.strip()}") if hasattr(event, 'action') and event.action.value == 'run' and hasattr(event, 'command') else print(f"📤 OUTPUT: {('\\n'.join(event.content.strip().split('\\n')[:5]) + f'\\n... (truncated {len(event.content.strip().split(chr(10)))-5} more lines)') if len(event.content.strip().split('\\n')) > 5 else event.content.strip()}") if hasattr(event, 'observation') and event.observation.value == 'run' and hasattr(event, 'content') else print(f"\\n✅ AGENT COMPLETED TASK:\\n   Task Completed: {event.task_completed}\\n   Final Thought: {event.final_thought}") if hasattr(event, 'action') and event.action.value == 'finish' else print(f"\\n📖 READ FILE: {event.path}") if hasattr(event, 'action') and event.action.value == 'read' and hasattr(event, 'path') else print(f"📄 FILE CONTENT: {('\\n'.join(event.content.split('\\n')[:8]) + f'\\n... (truncated {len(event.content.split(chr(10)))-8} more lines)') if len(event.content.split('\\n')) > 8 else event.content}") if hasattr(event, 'observation') and event.observation.value == 'read' and hasattr(event, 'content') else None for event in state.history]; print("\\n" + "=" * 80, "FINAL STATE", "=" * 80, f"Session ID: {state.session_id}", f"Agent State: {state.agent_state}", f"Iterations: {state.iteration_flag.current_value}/{state.iteration_flag.max_value}", f"Total Cost: ${state.metrics.accumulated_cost}", f"Total Tokens: {state.metrics.accumulated_token_usage}", sep="\\n")

# Block 6: Execute the session (simplified)
try:
    state = asyncio.run(run_session())
    print_conversation(state)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

#### Option B: Using run_controller (Original Approach with Bug Fix)

```python
# Alternative approach using core.main with manual SHTTP server fix
from openhands.core.main import run_controller
from openhands.core.config.mcp_config import OpenHandsMCPConfigImpl

# Same config as Option A, then:
async def run_session_with_controller(): 
    runtime = create_runtime(config, sid=session_name, headless_mode=True)

    # Fix the SHTTP server discarding bug manually
    shttp_server, _ = OpenHandsMCPConfigImpl.create_default_mcp_server_config(config.mcp_host, config, None)
    if shttp_server:
        shttp_server.url = shttp_server.url.replace('http://', 'https://')
        runtime.config.mcp.shttp_servers.append(shttp_server)
        print(f"Added SHTTP server: {shttp_server.url}")

    await runtime.connect()
    repo_directory = initialize_repository_for_runtime(runtime, selected_repository=config.sandbox.selected_repo)
    
    initial_action = MessageAction(content="Your task here...")
    
    state = await run_controller(
        config=config, 
        initial_user_action=initial_action, 
        runtime=runtime, 
        sid=session_name, 
        headless_mode=True, 
        fake_user_response_fn=lambda state: "continue"
    )
    return state

# Execute
try:
    state = asyncio.run(run_session_with_controller())
    print_conversation(state)
except Exception as e:
    print(f"Error: {e}")
```

## 🎉 Success! Both approaches now connect to your dedicated MCP server!

### What this configuration does:

#### Option A: AgentSession Approach (Recommended)
1. **Uses dedicated MCP server**: Connects to your deployed `openhands-mcp-server-default.apps.dev.rhoai.rh-aiservices-bu.com`
2. **Direct Git tool access**: Uses the original OpenHands MCP tools without UI dependencies
3. **Clean architecture**: Separates MCP tools from the main OpenHands runtime
4. **Better reliability**: Isolated MCP server won't be affected by runtime container restarts

#### Option B: Fixed run_controller Approach  
1. **Manual SHTTP server fix**: Manually adds your dedicated MCP server that `core.main` discards
2. **HTTPS protocol fix**: Converts HTTP to HTTPS for external server access
3. **Same core.main flow**: Uses existing headless infrastructure with your MCP server

### Available Tools (from your MCP server):
- **create_pr**: GitHub pull request creation using your GitHub token
- **create_mr**: GitLab merge request creation (when GitLab token is configured)
- **create_bitbucket_pr**: Bitbucket pull request creation (when Bitbucket token is configured)
- **Plus all microagent tools**: fetch, etc. from runtime containers

### Your MCP Server Architecture:
1. **Dedicated deployment**: Runs independently in `openhands-pipeline` namespace
2. **Original MCP tools**: Uses the actual OpenHands MCP functions with proper authentication
3. **Environment-based auth**: Uses your `GITHUB_TOKEN` from the OpenShift secret
4. **HTTP wrapper**: Provides REST API and MCP-compatible endpoints
5. **Route access**: Accessible via OpenShift route at `https://openhands-mcp-server-default.apps.dev.rhoai.rh-aiservices-bu.com`

### Authentication:
- **Your MCP server**: Uses `GITHUB_TOKEN` from `openhands-secrets` in your OpenShift namespace
- **Runtime containers**: Use environment variables for other integrations

You now have **two working approaches** to access Git tools from your dedicated MCP server in headless mode! 🚀

### 3. Docker Runtime Commands

```bash
# Create Docker container session with GitHub repo
docker run -it \
  -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.49-nikolaik \
  -e GITHUB_TOKEN=your-github-token \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands:/.openhands \
  docker.all-hands.dev/all-hands-ai/openhands:0.49 \
  openhands \
    --selected-repo "owner/repository" \
    --task "Your development task" \
    --runtime docker \
    --max-iterations 50
```

### 4. Kubernetes Pod Commands

```bash
# Using Kubernetes runtime (creates pods automatically)
export GITHUB_TOKEN="your-github-token"
openhands \
  --runtime kubernetes \
  --sandbox.selected_repo "owner/repository" \
  --task "Deploy and test the application" \
  --max-iterations 100 \
  --config-file k8s-config.toml
```

**k8s-config.toml example:**
```toml
[runtime]
runtime = "kubernetes"
kubernetes_namespace = "openhands"
pod_name_prefix = "openhands-runtime-"

[git]
github_token = "your-github-token"
```

### 5. Issue Resolution Workflow

```bash
# Automatically resolve GitHub issues (creates session + clones repo)
export GITHUB_TOKEN="your-github-token"
python -m openhands.resolver.resolve_issue \
  --selected-repo "owner/repository" \
  --issue-number 123 \
  --max-iterations 50 \
  --runtime docker
```

### 6. Server Mode for API Access

```bash
# Start OpenHands server for API-based session creation
python -m openhands.server --host 0.0.0.0 --port 3000

# Then use API to create sessions
curl -X POST http://localhost:3000/api/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "sandbox": {
      "selected_repo": "owner/repo"
    },
    "initial_message": "Fix the failing tests"
  }'
```

## Core Implementation Details

### Session Creation Flow
1. **AgentSession.start()** - Initializes agent session (`openhands/server/session/agent_session.py:200`)
2. **Runtime.connect()** - Creates Docker container or Kubernetes pod (`openhands/runtime/base.py:883`)
3. **Runtime.clone_or_init_repo()** - Clones GitHub repository (`openhands/runtime/base.py:362`)
4. **Runtime.maybe_run_setup_script()** - Executes `.openhands/setup.sh` if present (`openhands/runtime/base.py:424`)

### Key Files
- `openhands/core/main.py` - Main headless entry point
- `openhands/cli/main.py` - CLI interface
- `openhands/runtime/base.py:362` - Repository cloning logic
- `openhands/server/session/agent_session.py` - Session management
- `openhands/runtime/impl/docker/docker_runtime.py` - Docker container creation
- `openhands/runtime/impl/kubernetes/kubernetes_runtime.py` - Kubernetes pod creation

## Environment Variables

```bash
export GITHUB_TOKEN="your-github-token"
export LLM_MODEL="gpt-4"
export LLM_API_KEY="your-openai-key"
export RUNTIME="docker"  # or "kubernetes"
export LOG_LEVEL="INFO"
export WORKSPACE_BASE="/workspace"
```

## Repository Integration Features

- **Automatic cloning** of GitHub repositories into `/workspace/repo-name`
- **Branch switching** to specified branch or creates workspace branch
- **Microagent loading** from `.openhands/microagents/` directory
- **Setup script execution** from `.openhands/setup.sh`
- **Git hooks setup** from `.openhands/pre-commit.sh`
- **Organization-level microagents** from `org/.openhands` repositories

## Best Practices

1. **Use Docker runtime** for consistent, isolated environments
2. **Set appropriate resource limits** (`max_iterations`, `max_budget_per_task`)
3. **Configure proper authentication** for private repositories
4. **Implement error handling** for network issues and API limits
5. **Use configuration files** for complex setups
6. **Monitor resource usage** when running multiple sessions

## Troubleshooting

- **Authentication errors**: Ensure GitHub token has proper permissions
- **Docker issues**: Check Docker daemon is running and accessible
- **Kubernetes errors**: Verify cluster access and namespace permissions
- **Repository access**: Confirm repository exists and is accessible with provided credentials
- **Resource limits**: Increase max_iterations for complex tasks

This document provides the essential commands and patterns to replicate OpenHands' UI workflow in headless mode, enabling automated session creation, repository cloning, and task execution.