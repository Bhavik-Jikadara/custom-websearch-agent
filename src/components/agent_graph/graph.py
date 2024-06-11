import json
import ast
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from src.components.models.openai_models import get_open_ai_json
from langgraph.checkpoint.sqlite import SqliteSaver
from src.components.agents.agents import (
    planner_agent, 
    researcher_agent, 
    reporter_agent, 
    reviewer_agent, 
    final_report, 
    end_node
    )
from src.components.prompts.prompts import (
    reviewer_prompt_template, 
    planner_prompt_template, 
    researcher_prompt_template, 
    reporter_prompt_template,
    reviewer_guided_json,
    researcher_guided_json,
    planner_guided_json
    )
from src.components.tools.google_serper import get_google_serper
from src.components.tools.basic_scraper import scrape_website
from src.components.states.state import AgentGraphState, get_agent_graph_state


def create_graph(server=None, model=None, stop=None, model_endpoint=None):
    graph = StateGraph(AgentGraphState)

    graph.add_node(
        "planner", 
        lambda state: planner_agent(
            state=state,
            research_question=state["research_question"],  
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
            previous_plans=lambda: get_agent_graph_state(state=state, state_key="planner_all"),
            model=model,
            server=server,
            guided_json=planner_guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )
    )

    graph.add_node(
        "researcher",
        lambda state: researcher_agent(
            state=state,
            research_question=state["research_question"], 
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
            previous_selections=lambda: get_agent_graph_state(state=state, state_key="researcher_all"), 
            serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
            model=model,
            server=server,
            guided_json=researcher_guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )
    )

    graph.add_node(
        "reporter", 
        lambda state: reporter_agent(
            state=state,
            research_question=state["research_question"], 
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
            previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_all"), 
            research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest"),
            model=model,
            server=server,
            stop=stop,
            model_endpoint=model_endpoint
        )
    )

    graph.add_node(
        "reviewer", 
        lambda state: reviewer_agent(
            state=state,
            research_question=state["research_question"], 
            feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"), 
            planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"), 
            researcher=lambda: get_agent_graph_state(state=state, state_key="researcher_latest"), 
            reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
            planner_agent=planner_prompt_template,
            researcher_agent=researcher_prompt_template,
            reporter_agent=reporter_prompt_template,
            serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest"),
            model=model,
            server=server,
            guided_json=reviewer_guided_json,
            stop=stop,
            model_endpoint=model_endpoint
        )
    )

    graph.add_node(
        "serper_tool",
        lambda state: get_google_serper(
            state=state,
            plan=lambda: get_agent_graph_state(state=state, state_key="planner_latest")
        )
    )

    graph.add_node(
        "scraper_tool",
        lambda state: scrape_website(
            state=state,
            research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest")
        )
    )

    graph.add_node(
        "final_report", 
        lambda state: final_report(
            state=state,
            final_response=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
            )
    )

    graph.add_node("end", lambda state: end_node(state=state))

    # Define the edges in the agent graph
    def pass_review(state: AgentGraphState, model=None):
        review_list = state["reviewer_response"]
        if review_list:
            review = review_list[-1]
        else:
            review = "No review"

        if review != "No review":
            if isinstance(review, HumanMessage):
                review_content = review.content
            else:
                review_content = review
            
            # review_data = ast.literal_eval(review_content)
            # review_data = json.loads(review_content)
            review_data = json.loads(review_content)
            next_agent = review_data["suggest_next_agent"]
        else:
            next_agent = "end"

        return next_agent

    # Add edges to the graph
    graph.set_entry_point("planner")
    graph.set_finish_point("end")
    graph.add_edge("planner", "serper_tool")
    graph.add_edge("serper_tool", "researcher")
    graph.add_edge("researcher", "scraper_tool")
    graph.add_edge("scraper_tool", "reporter")
    graph.add_edge("reporter", "reviewer")

    graph.add_conditional_edges(
        "reviewer",
        lambda state: pass_review(state=state, model=model),
    )

    graph.add_edge("final_report", "end")

    return graph

def compile_workflow(graph):
    # memory = SqliteSaver.from_conn_string(":memory:")  # Here we only save in-memory
    # workflow = graph.compile(checkpointer=memory, interrupt_before=["end"])
    workflow = graph.compile()
    return workflow