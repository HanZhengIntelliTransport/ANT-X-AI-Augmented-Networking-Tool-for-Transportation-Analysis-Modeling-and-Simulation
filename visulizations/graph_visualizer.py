from itertools import combinations
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

class GraphVisualizer:
    def __init__(self, graph):
        """
        Initialize the GraphVisualizer with a graph object.
        :param graph: A graph object containing nodes and links.
        """
        self.graph = graph

    def _prepare_plot_data(self):
        """
        Prepare data for visualization, extracting all pairwise dimension combinations.
        """
        node_positions = {node.node_id: node.coordinates for node in self.graph.nodes.values()}
        dimensions = len(next(iter(node_positions.values())))  # Get the number of dimensions
        dimension_pairs = list(combinations(range(dimensions), 2))  # Generate all pairwise combinations
        edges = [
            (self.graph.nodes[link.source].coordinates, self.graph.nodes[link.target].coordinates)
            for link in self.graph.links
        ]
        return node_positions, dimension_pairs, edges

    def create_dash_app(self):
        """
        Create a Dash app to visualize all pairwise dimension combinations.
        """
        app = dash.Dash(__name__)

        # Prepare the data
        node_positions, dimension_pairs, edges = self._prepare_plot_data()

        # Create a subplot for each pair of dimensions
        fig = make_subplots(
            rows=len(dimension_pairs),
            cols=1,
            subplot_titles=[
                f"Dimension {pair[0]} vs Dimension {pair[1]}" for pair in dimension_pairs
            ],
            vertical_spacing=0.1
        )

        # Add traces for each dimension pair
        for i, (dim_x, dim_y) in enumerate(dimension_pairs, start=1):
            # Nodes
            fig.add_trace(
                go.Scatter(
                    x=[node[dim_x] for node in node_positions.values()],
                    y=[node[dim_y] for node in node_positions.values()],
                    mode='markers',
                    marker=dict(size=10, color='blue'),
                    text=[f"Node {node_id}" for node_id in node_positions.keys()],
                    hoverinfo='text',
                    name=f"Nodes (Dim {dim_x}, Dim {dim_y})"
                ),
                row=i,
                col=1
            )

            # Edges
            for source_coords, target_coords in edges:
                fig.add_trace(
                    go.Scatter(
                        x=[source_coords[dim_x], target_coords[dim_x], None],
                        y=[source_coords[dim_y], target_coords[dim_y], None],
                        mode='lines',
                        line=dict(color='gray', width=1),
                        hoverinfo='none',
                        name=f"Edges (Dim {dim_x}, Dim {dim_y})"
                    ),
                    row=i,
                    col=1
                )

            # Update subplot axis titles for clarity
            fig.update_xaxes(title_text=f"Dimension {dim_x}", row=i, col=1)
            fig.update_yaxes(title_text=f"Dimension {dim_y}", row=i, col=1)

        # Update layout
        fig.update_layout(
            title="Graph Visualization Across All Pairwise Dimension Combinations",
            showlegend=False,
            height=300 * len(dimension_pairs),  # Adjust height based on the number of subplots
            margin=dict(l=50, r=50, t=50, b=50)
        )

        # Dash Layout
        app.layout = html.Div([
            dcc.Graph(
                id='graph-visualization',
                figure=fig,
                style={'height': '90vh'}
            ),
            html.Div(id='node-info', style={'padding': '10px', 'font-size': '16px'})
        ])

        # Callback for interactive node info display
        @app.callback(
            Output('node-info', 'children'),
            [Input('graph-visualization', 'clickData')]
        )
        def display_node_info(click_data):
            if click_data is None:
                return "Click on a node to see details."
            node_id = click_data['points'][0]['text'].split(" ")[1]
            node = self.graph.nodes[node_id]
            return f"Node ID: {node.node_id}, Coordinates: {node.coordinates}, Attributes: {node.attributes}"

        return app