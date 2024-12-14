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


class GraphDrawer:
    def __init__(self, dimension_list, graph):
        """
        Initialize the GraphDrawer with a graph object and dimensions.
        :param dimension_list: A list of Dimension objects.
        :param graph: A graph object containing nodes and links.
        """
        self.dimension_list = {dim.dim_id: dim for dim in dimension_list}  # Store dimensions as a dictionary
        self.graph = graph

    def plot_projection(self, dimension_id_list, save_path=None):
        """
        Plot a projection of the graph onto specified dimensions using Dimension values as axis ticks.
        :param dimension_id_list: List of dimension IDs to project onto (e.g., ["X", "Y"]).
        :param save_path: Optional path to save the plot as an image.
        """
        # Validate input dimensions
        if not all(dim in self.graph.dimension_id_list for dim in dimension_id_list):
            raise ValueError(f"Some dimensions in {dimension_id_list} are not part of the graph's dimensions.")

        # Use `project_to_dimensions` to get projected data
        projection = self.graph.project_to_dimensions(dimension_id_list)
        projected_nodes = projection["nodes"]
        projected_links = projection["links"]

        # Debugging output
        print("Projected Nodes:", projected_nodes)
        print("Projected Links:", projected_links)

        # Get Dimension objects for axis
        dimensions = [self.dimension_list[dim] for dim in dimension_id_list]
        dim_x, dim_y = dimensions

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot nodes
        for node in projected_nodes:
            coords = node["coordinates"]
            ax.scatter(
                coords[dim_x.dim_id], coords[dim_y.dim_id],
                s=100, color='blue', edgecolor='black', label=f"Node {node['node_id']}"
            )
            ax.text(
                coords[dim_x.dim_id], coords[dim_y.dim_id], f"{node['node_id']}",
                fontsize=10, ha='center', va='center', color='red'
            )

        # Plot links
        for link in projected_links:
            source_coords = link["source"]["coordinates"]
            target_coords = link["target"]["coordinates"]
            ax.plot(
                [source_coords[dim_x.dim_id], target_coords[dim_x.dim_id]],
                [source_coords[dim_y.dim_id], target_coords[dim_y.dim_id]],
                color='gray', linestyle='-', linewidth=1, alpha=0.7
            )

        # Set axis labels
        ax.set_xlabel(f"Dimension {dim_x.dim_id}", fontsize=12)
        ax.set_ylabel(f"Dimension {dim_y.dim_id}", fontsize=12)
        ax.set_title(f"Projection on Dimensions {dim_x.dim_id} vs {dim_y.dim_id}", fontsize=16)

        # Use values as axis ticks
        ax.set_xticks([dim_x.coordinates[value] for value in dim_x.values])  # Map coordinate ticks for X
        ax.set_xticklabels(dim_x.values, fontsize=10)  # Use value labels for X-axis
        ax.set_yticks([dim_y.coordinates[value] for value in dim_y.values])  # Map coordinate ticks for Y
        ax.set_yticklabels(dim_y.values, fontsize=10)  # Use value labels for Y-axis

        # Add grid
        ax.grid(True)

        # Save or show the plot
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Projection saved to {save_path}")
        else:
            plt.show()