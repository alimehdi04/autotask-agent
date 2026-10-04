import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from tools import llm_with_tools, fetch_invoices, submit_to_internal_system, verify_system_state
import argparse

class AgentState(TypedDict):
    messages: Annotated[List, operator.add]

# System prompt updated to mention human approval
SYSTEM_PROMPT = """You are an autonomous AI task worker.
Your goal is to complete the user's task using the tools provided.

CRITICAL INSTRUCTIONS:
1. Break the task down into logical steps.
2. If a tool action fails (e.g., a 500 error from the internal system or a browser input error), you MUST read the error observation, fix the issue, and retry the action at least once before giving up.
3. After successfully submitting data, you MUST call verify_system_state to actually check that the task was completed correctly and the data matches what you submitted.
4. When reporting back, provide a concise summary and evidence of completion based on the verification step.
"""

def agent_node(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    last_message = state["messages"][-1]
    tool_outputs = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # HUMAN-IN-THE-LOOP INTERCEPT
        if tool_name == "submit_to_internal_system":
            print(f"\n🛑 HUMAN APPROVAL REQUIRED 🛑")
            print(f"The agent is attempting to submit the following data to the internal system:")
            print(f"Payload: {tool_args}")
            approval = input("Do you approve this submission? (y/n): ")
            
            if approval.lower() != 'y':
                print("[Action Cancelled by User]")
                result = "Human denied the submission. Stop the task and ask the human for clarification."
                tool_outputs.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
                continue
                
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
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "end"
    return "continue"

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
workflow.add_edge("tools", "agent")

app = workflow.compile()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CentrAlign Autonomous Task Worker")
    parser.add_argument(
        "--task", 
        type=str, 
        default="Find the latest invoice from Company X, extract the amount and due date, enter it into our internal system, and tell me once it is done.",
        help="The natural language task for the agent to execute."
    )
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print("🤖 AutoTask Agent Initialized")
    print("="*50)
    print(f"Goal: {args.task}\n")
    
    inputs = {"messages": [HumanMessage(content=args.task)]}
    
    for output in app.stream(inputs, stream_mode="updates"):
        for node_name, state_update in output.items():
            if node_name == "agent":
                agent_msg = state_update["messages"][0]
                if agent_msg.content:
                    print(f"\n[Agent Final Report]:\n{agent_msg.content}\n")