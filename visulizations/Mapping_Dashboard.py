import json
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from Network_Factory import get_multi_resolution_network

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# ==================== Helper Functions ====================
def debug_print(message, data=None):
    """Helper function to print debug messages."""
    print(f"[DEBUG] {message}")
    if data:
        print(json.dumps(data, indent=2))


def create_network_figure(layer_data, highlight_node=None, highlight_edge=None):
    """
    Create a Plotly figure for a network layer.

    Args:
        layer_data (dict): Data for the network layer containing nodes and edges.
        highlight_node (str, optional): Node to highlight. Defaults to None.
        highlight_edge (tuple, optional): Edge to highlight. Defaults to None.

    Returns:
        go.Figure: Plotly figure for the layer.
    """
    fig = go.Figure()

    # Add edges
    for edge in layer_data["edges"]:
        x0, y0 = layer_data["nodes"][edge["source"]]["coordinates"]
        x1, y1 = layer_data["nodes"][edge["target"]]["coordinates"]
        is_highlighted = highlight_edge == (edge["source"], edge["target"])

        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode="lines",
            line=dict(width=6 if is_highlighted else 2, color="orange" if is_highlighted else "lightgray"),
            hoverinfo="text",
            text=f"{edge['source']} -> {edge['target']}"
        ))

    # Add nodes
    for node_id, node_data in layer_data["nodes"].items():
        x, y = node_data["coordinates"]
        is_highlighted = node_id == highlight_node

        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=15 if is_highlighted else 10, color="red" if is_highlighted else "blue"),
            text=node_id,
            textposition="top center",
            hoverinfo="text"
        ))

    fig.update_layout(title=layer_data["name"], showlegend=False)
    return fig


# ==================== Retrieve Multi-Resolution Network ====================
multi_resolution_network = get_multi_resolution_network()
serialized_network = multi_resolution_network.serialize_network()
debug_print("Serialized network for visualization", serialized_network)

# ==================== Layout ====================
app.layout = html.Div([
    html.H1("Multi-Resolution Network Visualization"),
    dcc.Store(id="highlight-state"),  # Store highlight state
    dcc.Store(id="serialized-network", data=serialized_network),  # Store serialized network

    # html.Label("Select Layer:"),
    # dcc.Dropdown(
    #     id="layer-dropdown",
    #     options=[{"label": meta["name"], "value": layer_id} for layer_id, meta in serialized_network.items() if layer_id != "mappings"],
    #     placeholder="Select a layer"
    # ),

    html.Div(id="selection-panel", style={"margin-top": "10px"}),  # Placeholder for dynamic selection panel
    html.Button("Highlight", id="highlight-button", n_clicks=0, style={"margin-top": "10px"}),  # Highlight button

    dcc.Graph(id="network-figure"),  # Main network figure

    html.Div(id="debug-output", style={"margin-top": "20px", "font-size": "14px", "color": "green"}),  # Debug output
])


# ==================== Callbacks ====================
@app.callback(
    [Output("network-figure", "figure"), Output("debug-output", "children")],
    [Input("highlight-button", "n_clicks")],
    [State("layer-dropdown", "value"), State("serialized-network", "data")]
)
def update_network_figure(n_clicks, layer_id, network_data):
    """
    Update the network figure based on selected layer and highlight state.

    Args:
        n_clicks (int): Number of clicks on the highlight button.
        layer_id (str): Selected layer ID.
        network_data (dict): Serialized network data.

    Returns:
        Tuple[go.Figure, str]: Updated figure and debug output.
    """
    if not layer_id:
        return go.Figure(), "No layer selected."

    layer_data = network_data.get(layer_id, {})
    if not layer_data:
        return go.Figure(), f"Layer ID '{layer_id}' not found in the network data."

    debug_print(f"Selected Layer: {layer_id}", layer_data)
    return create_network_figure(layer_data), f"Layer '{layer_data['name']}' displayed."


# ==================== Run App ====================
def run_visualization(network):
    global multi_resolution_network
    multi_resolution_network = network
    app.run_server(debug=True, port=8050)