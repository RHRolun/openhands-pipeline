#!/usr/bin/env python3
"""
OpenHands Headless Session Script
This script creates a headless OpenHands session, clones a GitHub repository,
and runs a task with formatted conversation output.
"""

import asyncio
import os
from openhands.core.config import OpenHandsConfig
from openhands.core.config.sandbox_config import SandboxConfig
from openhands.core.config.llm_config import LLMConfig
from openhands.core.main import run_controller
from openhands.core.setup import initialize_repository_for_runtime, create_runtime
from openhands.events.action import MessageAction

async def create_headless_session():
    """Create and run a headless OpenHands session"""
    # Set environment variables for GitHub token
    os.environ['GITHUB_TOKEN'] = 'YOUR_GITHUB_TOKEN'  # Replace with your actual token
    os.environ['LLM_API_KEY'] = 'YOUR_LLM_API_KEY'  # Replace with your actual API key
    os.environ['LLM_BASE_URL'] = 'https://openrouter.ai/api/v1'
    os.environ['LLM_MODEL'] = 'openai/qwen/qwen3-235b-a22b-07-25:free'
    
    # Define a custom session name/ID
    session_name = "simple"
    
    # Configure OpenHands with LLM settings
    config = OpenHandsConfig(
        runtime='kubernetes',  # or 'docker' for container-based execution
        max_iterations=50,
        workspace_base="/workspace",
        sandbox=SandboxConfig(
            selected_repo='rhoai-genaiops/genaiops-helmcharts',  # Repository to clone
            runtime_container_image='ghcr.io/all-hands-ai/runtime:0.49-nikolaik'  # Current OpenHands runtime
        )
    )
    
    # Configure the LLM explicitly
    llm_config = LLMConfig(
        model='openai/qwen/qwen3-235b-a22b-07-25:free',
        api_key='YOUR_LLM_API_KEY',  # Replace with your actual API key
        base_url='https://openrouter.ai/api/v1'
    )
    config.set_llm_config(llm_config)
    
    # Create runtime with custom session ID and initialize repository
    runtime = create_runtime(config, sid=session_name, headless_mode=True)
    await runtime.connect()
    
    # Clone the repository
    repo_directory = initialize_repository_for_runtime(
        runtime, 
        selected_repository=config.sandbox.selected_repo
    )
    
    # Define the task
    initial_action = MessageAction(
        content="Create me a MIT license file and push it as a PR to the repo"
    )
    
    # Run the controller (this creates pod/session and clones repo)
    state = await run_controller(
        config=config,
        initial_user_action=initial_action,
        runtime=runtime,
        sid=session_name,  # Use the same session ID
        headless_mode=True,
        fake_user_response_fn=lambda state: "continue"  # Auto-continue
    )
    
    return state

def print_conversation(state):
    """Extract and print the conversation from the State object"""
    print("=" * 80)
    print("CONVERSATION SUMMARY")
    print("=" * 80)
    
    for i, event in enumerate(state.history):
        # Print user messages
        if hasattr(event, 'action') and event.action.value == 'message' and hasattr(event, 'content'):
            if hasattr(event, 'wait_for_response') and event.wait_for_response:
                print(f"\n🤖 AGENT: {event.content}")
            else:
                print(f"\n👤 USER: {event.content}")
        
        # Print agent actions and thoughts
        elif hasattr(event, 'action') and event.action.value == 'run' and hasattr(event, 'command'):
            print(f"\n💻 COMMAND: {event.command.strip()}")
        
        elif hasattr(event, 'observation') and event.observation.value == 'run' and hasattr(event, 'content'):
            # Only show first few lines of output to avoid clutter
            output_lines = event.content.strip().split('\n')
            if len(output_lines) > 5:
                output = '\n'.join(output_lines[:5]) + f'\n... (truncated {len(output_lines)-5} more lines)'
            else:
                output = event.content.strip()
            print(f"📤 OUTPUT: {output}")
        
        # Print agent finish actions
        elif hasattr(event, 'action') and event.action.value == 'finish':
            print(f"\n✅ AGENT COMPLETED TASK:")
            print(f"   Task Completed: {event.task_completed}")
            print(f"   Final Thought: {event.final_thought}")
        
        # Print file read actions
        elif hasattr(event, 'action') and event.action.value == 'read' and hasattr(event, 'path'):
            print(f"\n📖 READ FILE: {event.path}")
        
        elif hasattr(event, 'observation') and event.observation.value == 'read' and hasattr(event, 'content'):
            # Show just the first few lines of file content
            content_lines = event.content.split('\n')
            if len(content_lines) > 8:
                content = '\n'.join(content_lines[:8]) + f'\n... (truncated {len(content_lines)-8} more lines)'
            else:
                content = event.content
            print(f"📄 FILE CONTENT: {content}")

    print("\n" + "=" * 80)
    print("FINAL STATE")
    print("=" * 80)
    print(f"Session ID: {state.session_id}")
    print(f"Agent State: {state.agent_state}")
    print(f"Iterations: {state.iteration_flag.current_value}/{state.iteration_flag.max_value}")
    print(f"Total Cost: ${state.metrics.accumulated_cost}")
    print(f"Total Tokens: {state.metrics.accumulated_token_usage}")

async def main():
    """Main function to run the session and print results"""
    print("Starting OpenHands headless session...")
    state = await create_headless_session()
    print_conversation(state)
    return state

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())