import streamlit as st
from streamlit_plotly_events import plotly_events
from dashboard.api.client import APIClient
from dashboard.api.endpoints import get_version_flow_endpoint
from dashboard.visualizations.flow_chart import FlowChart

def get_path_to_node(flow_data: dict, target_node_id: str) -> list:
    """Calculate path to node using previous_node_id"""
    nodes_map = {step["id"]: step for step in flow_data["steps"]}
    path = []
    current_node_id = target_node_id
    while current_node_id:
        current_node = nodes_map.get(current_node_id)
        if current_node:
            path.append(current_node["name"])
            current_node_id = current_node.get("previous_node_id")
        else:
            break
    return list(reversed(path))

def flow_page():
    if 'current_project' not in st.session_state or 'current_version' not in st.session_state:
        st.switch_page("main.py")
        return
        
    if 'switch_to_recordings' not in st.session_state:
        st.session_state.switch_to_recordings = False
        
    if st.session_state.switch_to_recordings:
        st.session_state.switch_to_recordings = False
        st.switch_page("pages/2_recordings.py")
        
    st.title(f"Version: {st.session_state.current_version}")
    
    # Initialize API client
    api_client = APIClient()
    
    flow_data = api_client.fetch_data(
        get_version_flow_endpoint(
            st.session_state.current_project,
            st.session_state.current_version
        )
    )
    
    if flow_data.get("steps"):
        st.subheader("Call Flow Visualization")
        
        # Create a list of node IDs in order
        node_list = [step["id"] for step in flow_data["steps"]]
        
        flow_chart = FlowChart(flow_data)
        fig = flow_chart.create_figure()
        
        # Handle click events using plotly_events
        clicked = plotly_events(
            fig,
            click_event=True,
            override_height=600,
            key="flow_chart"
        )
        
        # Debug container
        debug_container = st.empty()
        info_container = st.empty()
        
        if clicked:
            with debug_container:
                if len(clicked) > 0:
                    point_data = clicked[0]
                    point_index = point_data.get("pointIndex")
                    
                    if point_index is not None and 0 <= point_index < len(node_list):
                        node_id = node_list[point_index]
                        path = get_path_to_node(flow_data, node_id)
                        print("Flow data:", flow_data)
                        print("Node ID:", node_id)
                        print("Path:", path)

                        
                        # Update session state
                        st.session_state.selected_node_id = node_id
                        st.session_state.selected_path = " -> ".join(path)
                        
                        with info_container:
                            # Show selection info
                            st.success(f"Selected path: {st.session_state.selected_path}")
                            
                            # Get step details
                            step_data = next((s for s in flow_data["steps"] if s["id"] == node_id), None)
                            if step_data:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Calls", step_data["number_of_calls"])
                                with col2:
                                    st.metric("Successful", step_data["number_of_successful_calls"])
                                with col3:
                                    success_rate = (step_data["number_of_successful_calls"] / 
                                                  step_data["number_of_calls"] * 100 
                                                  if step_data["number_of_calls"] > 0 else 0)
                                    st.metric("Success Rate", f"{success_rate:.1f}%")
                            
                            if st.button("View Recordings for this Path", type="primary"):
                                st.session_state.switch_to_recordings = True
                                st.rerun()

if __name__ == "__main__":
    flow_page()