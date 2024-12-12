import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

class GraphVisualizer:
    def __init__(self, graph):
        """
        Initialize the visualizer with a graph.
        :param graph: An instance of the Graph class.
        """
        self.graph = graph

    def _prepare_plot_data(self):
        """
        Prepare data for Plotly visualization. Projects higher-dimensional nodes to 2D.
        """
        node_x = []
        node_y = []
        node_ids = []
        node_colors = []
        edge_x = []
        edge_y = []

        # Generate node positions
        for node in self.graph.nodes.values():
            # Project higher-dimensional coordinates to 2D (take the first two dimensions)
            x, y = node.coordinates[:2] if len(node.coordinates) >= 2 else (node.coordinates[0], 0)
            node_x.append(x)
            node_y.append(y)
            node_ids.append(node.node_id)
            node_colors.append(node.attributes.get("color", "blue"))

        # Generate edges
        for link in self.graph.links:
            source_node = self.graph.nodes[link.source]
            target_node = self.graph.nodes[link.target]
            source_x, source_y = source_node.coordinates[:2] if len(source_node.coordinates) >= 2 else (
            source_node.coordinates[0], 0)
            target_x, target_y = target_node.coordinates[:2] if len(target_node.coordinates) >= 2 else (
            target_node.coordinates[0], 0)
            edge_x += [source_x, target_x, None]
            edge_y += [source_y, target_y, None]

        return node_x, node_y, node_ids, node_colors, edge_x, edge_y

    def create_dash_app(self):
        """
        Create a Dash app for graph visualization.
        """
        app = dash.Dash(__name__)

        # Prepare data for visualization
        node_x, node_y, node_ids, node_colors, edge_x, edge_y = self._prepare_plot_data()

        # Initial Plotly figure
        fig = go.Figure()

        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            mode='lines'
        ))

        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                size=10,
                color=node_colors,
                line_width=2
            ),
            text=node_ids,
            hoverinfo='text'
        ))

        # Set layout
        fig.update_layout(
            title=f"Graph: {self.graph.network_id}",
            showlegend=False,
            margin=dict(l=0, r=0, t=40, b=0),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
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

        # Callbacks for interactivity
        @app.callback(
            Output('node-info', 'children'),
            [Input('graph-visualization', 'clickData')]
        )
        def display_node_info(click_data):
            if click_data is None:
                return "Click on a node to see details."
            node_id = click_data['points'][0]['text']
            node = self.graph.nodes[node_id]
            return f"Node ID: {node.node_id}, Coordinates: {node.coordinates}, Attributes: {node.attributes}"

        return app