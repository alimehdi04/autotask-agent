import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from tools import llm_with_tools, fetch_invoices, submit_to_internal_system, verify_system_state

# Define the state graph schema
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]

# System instructions forcing explicit verification and retry behavior
SYSTEM_PROMPT = """You are an autonomous AI task worker.
Your goal is to complete the user's task using the tools provided.

CRITICAL INSTRUCTIONS:
1. Break the task down into logical steps.
2. If a tool action fails (e.g., a 500 error from the internal system), you MUST read the error observation and retry the action at least once before giving up.
3. After successfully submitting data, you MUST call verify_system_state to actually check that the task was completed correctly and the data matches what you submitted. Do not just assume it worked.
4. When reporting back, provide a concise summary and evidence of completion based on the verification step.
"""

def agent_node(state: AgentState):
    """Invokes the LLM to decide the next action based on the state history."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    """Executes the tool calls requested by the agent and returns the observations."""
    last_message = state["messages"][-1]
    tool_outputs = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        print(f"\n[Executing Tool]: {tool_name} with args: {tool_args}")
        
        if tool_name == "fetch_invoices":
            result = fetch_invoices.invoke(tool_args)
        elif tool_name == "submit_to_internal_system":
            result = submit_to_internal_system.invoke(tool_args)
        elif tool_name == "verify_system_state":
            result = verify_system_state.invoke(tool_args)
        else:
            result = "Error: Unknown tool."
            
        print(f"[Tool Observation]: {result}")
        tool_outputs.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        
    return {"messages": tool_outputs}

def should_continue(state: AgentState):
    """Determines whether the agent needs to use more tools or is finished."""
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "end"
    return "continue"

# Build the LangGraph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
workflow.add_edge("tools", "agent")

app = workflow.compile()

if __name__ == "__main__":
    # The exact natural language instruction from the prompt
    task = "Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done."
    
    print("--- Starting Autonomous AI Task Worker ---")
    print(f"Goal: {task}\n")
    
    inputs = {"messages": [HumanMessage(content=task)]}
    
    # Stream the execution to observe the loop
    for output in app.stream(inputs, stream_mode="updates"):
        for node_name, state_update in output.items():
            if node_name == "agent":
                agent_msg = state_update["messages"][0]
                if agent_msg.content:
                    print(f"\n[Agent Final Report]:\n{agent_msg.content}")