from Dimension2Network.graph_elements import Graph, Node, Link

class GraphTheoryRule:
    def __init__(self, graph):
        print(1)

class RuleManager:
    """Manages rules for nodes and links in the network."""
    #The input dimensions of each function is the dimension of high-dimensional network

    def __init__(self):
        self.node_rules = {}  # {rule_id: (dimensions, rule_function)}
        self.link_rules = {}  # {rule_id: (dimensions, rule_function)}

    def add_node_rule(self, rule_id, dimensions, rule_function):
        """Add a node rule."""
        self.node_rules[rule_id] = (dimensions, rule_function)

    def add_link_rule(self, rule_id, dimensions, rule_function):
        """Add a link rule."""
        self.link_rules[rule_id] = (dimensions, rule_function)

    def validate_node(self, dimensions, coordinates):
        """Validate a node against all node rules."""
        for rule_id, (rule_dims, rule_func) in self.node_rules.items():
            if not all(dim in dimensions for dim in rule_dims):
                continue
            indices = [dimensions.index(dim) for dim in rule_dims]
            values = [coordinates[idx] for idx in indices]
            if not rule_func(*values):
                return False
        return True

    def validate_link(self, dimensions, coords1, coords2):
        """Validate a link against all link rules."""
        for rule_id, (rule_dims, rule_func) in self.link_rules.items():
            if not all(dim in dimensions for dim in rule_dims):
                continue
            indices = [dimensions.index(dim) for dim in rule_dims]
            values1 = [coords1[idx] for idx in indices]
            values2 = [coords2[idx] for idx in indices]

            # Flatten lists if there's only one dimension
            if len(values1) == 1 and len(values2) == 1:
                values1 = values1[0]
                values2 = values2[0]

            if not rule_func(values1, values2):
                return False
        return True


class HighDimNetwork:
    """A network supporting high-dimensional nodes, links, and traceable dimensions."""

    def __init__(self, network_id, dimension, dimension_ids=None, scales=None, ranges=None, steps=None, rule_manager=None):
        self.network_id = network_id
        self.dimension = dimension
        self.graph = Graph(network_id)
        self.node_mapping = {}
        self.link_mapping = {}
        self.rule_manager = rule_manager or RuleManager()

        # Validate and set metadata
        if dimension_ids and len(dimension_ids) != dimension:
            raise ValueError("The number of dimension IDs must match the dimensionality.")
        self.dimension_metadata = dimension_ids or [f"dim_{i}" for i in range(dimension)]
        self.scales = scales or [None] * dimension
        self.ranges = ranges or [(None, None)] * dimension
        self.steps = steps or [0.1] * dimension

        if len(self.scales) != dimension or len(self.ranges) != dimension or len(self.steps) != dimension:
            raise ValueError("Scales, ranges, and steps must match the dimensionality.")

    def construct_nodes(self):
        """Construct nodes based on ranges, steps, and rules."""
        import itertools

        # Generate combinations of dimension values
        value_ranges = [
            [round(i, 10) for i in self._frange(rng[0], rng[1], step)] if rng[0] is not None and rng[1] is not None else []
            for rng, step in zip(self.ranges, self.steps)
        ]
        for coordinates in itertools.product(*value_ranges):
            node_id = "_".join(map(str, coordinates))
            if self.rule_manager.validate_node(self.dimension_metadata, coordinates):
                self.add_node(node_id, coordinates)

    def construct_links(self):
        """Construct links between nodes based on link rules."""
        node_ids = list(self.graph.nodes.keys())
        for i, source_id in enumerate(node_ids):
            for target_id in node_ids[i + 1:]:
                coords1 = self.graph.nodes[source_id].coordinates
                coords2 = self.graph.nodes[target_id].coordinates
                if self.rule_manager.validate_link(self.dimension_metadata, coords1, coords2):
                    self.add_link(source_id, target_id)

    def _frange(self, start, stop, step):
        """Helper function for generating floating-point ranges."""
        while start < stop:
            yield round(start, 10)
            start += step

    def add_node(self, node_id, coordinates, attributes=None):
        """Add a node to the graph."""
        self.graph.add_node(Node(node_id, coordinates, attributes))

    def add_link(self, source_id, target_id, link_id=None, attributes=None):
        """Add a link to the graph."""
        link_id = link_id or f"{source_id}_{target_id}"
        self.graph.add_link(Link(link_id, source_id, target_id, attributes))

    def merge_networks(self, other_network, merge_dimensions):
        """
        Merge two networks into a higher-dimensional network.

        :param other_network: The other HighDimNetwork instance to merge with.
        :param merge_dimensions: List of shared dimensions to merge on.
        :return: A new HighDimNetwork instance representing the merged network.
        """
        # Validate shared dimensions
        shared_dims = [
            dim for dim in merge_dimensions
            if dim in self.dimension_metadata and dim in other_network.dimension_metadata
        ]
        if not shared_dims:
            raise ValueError("No shared dimensions found for merging.")

        # Prepare new metadata, scales, and ranges for the merged network
        new_metadata = list(set(self.dimension_metadata + other_network.dimension_metadata))
        combined_scales = [None] * len(new_metadata)
        combined_ranges = [(None, None)] * len(new_metadata)

        # Copy scales and ranges for the first network
        for dim in self.dimension_metadata:
            idx = new_metadata.index(dim)
            combined_scales[idx] = self.scales[self.dimension_metadata.index(dim)]
            combined_ranges[idx] = self.ranges[self.dimension_metadata.index(dim)]

        # Copy scales and ranges for the second network
        for dim in other_network.dimension_metadata:
            idx = new_metadata.index(dim)
            combined_scales[idx] = other_network.scales[other_network.dimension_metadata.index(dim)]
            combined_ranges[idx] = other_network.ranges[other_network.dimension_metadata.index(dim)]

        # Combine rule managers
        combined_rule_manager = RuleManager()
        combined_rule_manager.node_rules.update(self.rule_manager.node_rules)
        combined_rule_manager.node_rules.update(other_network.rule_manager.node_rules)
        combined_rule_manager.link_rules.update(self.rule_manager.link_rules)
        combined_rule_manager.link_rules.update(other_network.rule_manager.link_rules)

        # Initialize the merged network
        combined_network = HighDimNetwork(
            network_id=f"{self.network_id}_{other_network.network_id}",
            dimension=len(new_metadata),
            dimension_ids=new_metadata,
            scales=combined_scales,
            ranges=combined_ranges,
            rule_manager=combined_rule_manager,
        )

        # Merge nodes
        for node1_id, data1 in self.graph.nodes.items():
            for node2_id, data2 in other_network.graph.nodes.items():
                combined_coords = [
                    data1.coordinates[self.dimension_metadata.index(dim)] if dim in self.dimension_metadata else
                    data2.coordinates[other_network.dimension_metadata.index(dim)]
                    for dim in new_metadata
                ]
                combined_id = f"{node1_id}_{node2_id}"
                combined_network.add_node(combined_id, tuple(combined_coords))
                combined_network.node_mapping[combined_id] = {
                    self.network_id: node1_id,
                    other_network.network_id: node2_id,
                }
                print(f"Node Mapping Added: {combined_id} -> {combined_network.node_mapping[combined_id]}")  # Debug

        # Merge links
        for link1 in self.graph.links:
            for link2 in other_network.graph.links:
                combined_source = f"{link1.source}_{link2.source}"
                combined_target = f"{link1.target}_{link2.target}"
                combined_id = f"{link1.link_id}_{link2.link_id}"
                combined_network.add_link(combined_source, combined_target)
                combined_network.link_mapping[combined_id] = {
                    self.network_id: (link1.source, link1.target),
                    other_network.network_id: (link2.source, link2.target),
                }
                print(f"Link Mapping Added: {combined_id} -> {combined_network.link_mapping[combined_id]}")  # Debug

        return combined_network
    def remove_node(self, node_id):
        """Remove a node and its associated links from the graph."""
        if node_id not in self.graph.nodes:
            raise ValueError(f"Node {node_id} does not exist in the graph.")

        # Remove associated links
        associated_links = [
            link_id for link_id, link in self.graph.links.items()
            if link.source == node_id or link.target == node_id
        ]
        for link_id in associated_links:
            self.remove_link(link_id)

        # Remove node from the graph and update mappings
        del self.graph.nodes[node_id]
        if node_id in self.node_mapping:
            del self.node_mapping[node_id]

        print(f"Node {node_id} and its associated links have been removed.")  # Debug

    def remove_link(self, link_id):
        """Remove a link from the graph."""
        if link_id not in self.graph.links:
            raise ValueError(f"Link {link_id} does not exist in the graph.")

        # Remove link from the graph and update mappings
        del self.graph.links[link_id]
        if link_id in self.link_mapping:
            del self.link_mapping[link_id]

        print(f"Link {link_id} has been removed.")  # Debug

    # Add helper functions for debug purposes (optional)
    def print_graph_summary(self):
        """Print a summary of the current graph state."""
        print(f"Graph {self.network_id}:")
        print(f"  Nodes: {len(self.graph.nodes)}")
        print(f"  Links: {len(self.graph.links)}")
    def __repr__(self):
        return f"HighDimNetwork(network_id={self.network_id}, nodes={len(self.graph.nodes)}, links={len(self.graph.links)})"