# Adjustable settings for figure size and resolution
FIGURE_SIZE = (12, 6)  # Default figure size (width, height) for each subplot
FIGURE_DPI = 150       # Default resolution (dots per inch)
NODE_SIZE = 50         # Default node size in the scatter plot
NODE_COLOR = 'blue'    # Default node color
NODE_EDGECOLOR = 'black'  # Default edge color of the nodes
NODE_LINEWIDTH = 0.5   # Default linewidth for the node edge
TEXT_FONTSIZE = 8      # Default font size for node labels
EDGE_COLOR = 'gray'    # Default color of edges
EDGE_LINEWIDTH = 1     # Default linewidth for edges
EDGE_ALPHA = 0.7       # Default transparency for edges
AXIS_LABEL_FONTSIZE = 12  # Default font size for axis labels
TITLE_FONTSIZE = 14    # Default font size for subplot titles
GRID_STYLE = '--'      # Grid line style
GRID_ALPHA = 0.6       # Grid transparency

import matplotlib.pyplot as plt
from itertools import combinations

class GraphDrawer:
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

    def plot_with_matplotlib(self, save_path=None):
        """
        Generate pairwise dimensional combination plots using Matplotlib.
        :param save_path: Optional path to save the plot as an image.
        """
        # Prepare data
        node_positions, dimension_pairs, edges = self._prepare_plot_data()
        num_pairs = len(dimension_pairs)

        # Create subplots with increased figure size and resolution
        fig, axes = plt.subplots(num_pairs, 1, figsize=(FIGURE_SIZE[0], FIGURE_SIZE[1] * num_pairs), dpi=FIGURE_DPI)
        if num_pairs == 1:
            axes = [axes]  # Ensure axes is iterable if there's only one subplot

        for ax, (dim_x, dim_y) in zip(axes, dimension_pairs):
            # Plot nodes
            for node_id, coords in node_positions.items():
                ax.scatter(
                    coords[dim_x], coords[dim_y], label=f"Node {node_id}",
                    s=NODE_SIZE, color=NODE_COLOR, edgecolor=NODE_EDGECOLOR, linewidth=NODE_LINEWIDTH
                )
                # ax.text(
                #     coords[dim_x], coords[dim_y], f"{node_id}",
                #     fontsize=TEXT_FONTSIZE, color='red', ha='center', va='center'
                # )

            # Plot edges
            for source_coords, target_coords in edges:
                ax.plot(
                    [source_coords[dim_x], target_coords[dim_x]],
                    [source_coords[dim_y], target_coords[dim_y]],
                    color=EDGE_COLOR, linewidth=EDGE_LINEWIDTH, alpha=EDGE_ALPHA
                )

            # Set axis labels and titles with dimension IDs
            ax.set_xlabel(f"Dimension {dim_x}", fontsize=AXIS_LABEL_FONTSIZE)
            ax.set_ylabel(f"Dimension {dim_y}", fontsize=AXIS_LABEL_FONTSIZE)
            ax.set_title(f"Dimension {dim_x} vs Dimension {dim_y}", fontsize=TITLE_FONTSIZE)

            # Enhance grid and layout
            ax.grid(True, linestyle=GRID_STYLE, alpha=GRID_ALPHA)

        # Adjust layout
        plt.tight_layout()

        # Save or show the plot
        if save_path:
            plt.savefig(save_path, dpi=300)  # High resolution for saved images
            print(f"Plot saved to {save_path}")
        else:
            plt.show()