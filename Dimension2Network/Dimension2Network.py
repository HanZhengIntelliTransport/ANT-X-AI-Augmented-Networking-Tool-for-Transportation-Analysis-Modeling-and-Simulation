from Dimension2Network.graph_elements import Graph, Node, Link
import inspect
from typing import Dict, List

class Dimension:
    """Represents a single dimension with logical values, corresponding coordinates, and attributes."""

    def __init__(self, dim_id, values, attributes=None, start=0, step=1):
        """
        Initialize a Dimension.
        :param dim_id: str, id of the dimension (e.g., "state").
        :param values: List[str], list of logical values this dimension can take (e.g., ["A", "B", "C"]).
        :param attributes: Optional[Dict[str, Dict[str, Any]]], a dictionary mapping each value in `values`
                           to another dictionary of attributes.
                           - Key: str, a value in `values`.
                           - Value: Dict[str, Any], a dictionary where:
                               - Key: Attribute name (e.g., "color", "weight").
                               - Value: Attribute value (e.g., "red", 1.5).
                           Example:
                               attributes={
                                   "A": {"color": "red", "weight": 1.0},
                                   "B": {"color": "blue", "weight": 1.5},
                                   "C": {"color": "green", "weight": 2.0},
                               }
        :param start: int or float, the starting coordinate for visualization.
        :param step: int or float, the step size for generating coordinates between consecutive values.
        """
        self.dim_id = dim_id
        self.values = values
        self.attributes = attributes or {value: {} for value in values}  # Default attributes as empty dicts
        self.coordinates = self._generate_coordinates(start, step)

        # Ensure attributes match values
        if set(self.values) != set(self.attributes.keys()):
            raise ValueError("Attributes keys must match the dimension values.")

    def _generate_coordinates(self, start, step):
        """
        Generate a mapping of each value to a unique coordinate based on its position in `values`.
        :param start: Starting coordinate for the first value.
        :param step: Step size between consecutive coordinates.
        :return: Dict[str, float], a dictionary mapping each value in `values` to a coordinate.
        """
        return {value: start + i * step for i, value in enumerate(self.values)}

    def validate_value(self, value):
        """
        Validate if a given value is valid for this dimension.
        :param value: str, the value to validate.
        :return: bool, True if the value is valid, otherwise False.
        """
        return value in self.values

    def get_coordinate(self, value):
        """
        Retrieve the coordinate corresponding to a logical value.
        :param value: str, a value in `values`.
        :return: float, the coordinate associated with the given value.
        :raises ValueError: If the value is not valid for this dimension.
        """
        if value not in self.coordinates:
            raise ValueError(f"Value '{value}' not valid for dimension '{self.dim_id}'.")
        return self.coordinates[value]

    def get_attribute(self, value, attribute_name):
        """
        Retrieve a specific attribute for a given value in this dimension.
        :param value: str, the value for which to retrieve the attribute.
        :param attribute_name: str, the name of the attribute to retrieve.
        :return: Any, the value of the requested attribute.
        :raises ValueError: If the value is not valid for this dimension.
        :raises KeyError: If the attribute does not exist for the given value.
        """
        if value not in self.attributes:
            raise ValueError(f"Value '{value}' not valid for dimension '{self.dim_id}'.")
        if attribute_name not in self.attributes[value]:
            raise KeyError(f"Attribute '{attribute_name}' not found for value '{value}'.")
        return self.attributes[value][attribute_name]

    def set_attribute(self, value, attribute_name, attribute_value):
        """
        Set or update a specific attribute for a given value in this dimension.
        :param value: str, the value for which to set or update the attribute.
        :param attribute_name: str, the name of the attribute to set or update.
        :param attribute_value: Any, the value to assign to the attribute.
        :raises ValueError: If the value is not valid for this dimension.
        """
        if value not in self.attributes:
            raise ValueError(f"Value '{value}' not valid for dimension '{self.dim_id}'.")
        self.attributes[value][attribute_name] = attribute_value

    def __repr__(self):
        """
        Return a string representation of the Dimension, including its name, values,
        coordinates, and attributes for debugging or display purposes.
        """
        return (f"Dimension(name={self.dim_id}, values={self.values}, "
                f"coordinates={self.coordinates}, attributes={self.attributes})")


class Rule:
    """Represents a single subrule with specific dimensions and a validation function."""

    def __init__(self, dimensions, rule_function):
        """
        Initialize a SubRule.
        :param dimensions: Dimensions the subrule applies to.
        :param rule_function: Validation function for the subrule.
        """
        self.dimensions = dimensions
        self.rule_function = rule_function

    def validate(self, dimensions_id_list, dim_values_Dic_1, dim_values_Dic_2):
        """
        Validate this subrule.
        :param dimensions_id_list: List of all dimension IDs in the current context.
        :param dim_values_Dic_1: Dictionary of dimension values for the source node.
        :param dim_values_Dic_2: Dictionary of dimension values for the target node.
        :return: True if the subrule passes, False otherwise.
        """
        # Ensure all dimensions required by this rule are present in dimensions_id_list
        if not all(dim in dimensions_id_list for dim in self.dimensions):
            return False

        # Extract the values of the relevant dimensions (e.g., "Y") from both source and target nodes
        relevant_source_values = [dim_values_Dic_1[dim] for dim in self.dimensions]
        relevant_target_values = [dim_values_Dic_2[dim] for dim in self.dimensions]

        # Pass the extracted values to the rule function
        return self.rule_function(*relevant_source_values, *relevant_target_values)

    def __str__(self):
        """Return a string representation of the SubRule."""
        try:
            # Get the source code of the rule_function if available
            func_code = inspect.getsource(self.rule_function).strip()
        except (TypeError, OSError):
            # Fallback to function name and memory location if source code is unavailable
            func_code = f"{self.rule_function.__name__} at {hex(id(self.rule_function))}"

        return f"SubRule(Dimensions: {self.dimensions}, Function: {func_code})"


class NetworkRule:
    """Represents a composite rule consisting of multiple subrules."""

    def __init__(self, rule_id, dimensions):
        """
        Initialize a Rule.
        :param rule_id: Unique identifier for the rule.
        :param dimensions: Dimensions applicable to this rule.
        """
        self.rule_id = rule_id
        self.dimensions = dimensions  # List of dimensions this rule applies to
        self.rules:List[Rule] = []  # List of SubRule instances

    def add_subrule(self, rule):
        """
        Add a subrule to this rule.
        :param rule: An instance of SubRule.
        :raises ValueError: If the SubRule's dimensions are not a subset of the Rule's dimensions.
        """
        # Check if all dimensions of the SubRule are within the Rule's dimensions
        if not all(dim in self.dimensions for dim in rule.dimensions):
            raise ValueError(
                f"SubRule dimensions {rule.dimensions} are not a subset of Rule dimensions {self.dimensions}."
            )
        self.rules.append(rule)

    def validate(self, dimensions_id_list, dim_values_Dic_1, dim_values_Dic_2):
        """
        Validate this rule by evaluating all its subrules.
        :param dimensions_id_list: List of all dimension ids in the current context.
        :param values: List of corresponding coordinate values.
        :return: True if any subrule passes, False otherwise (OR relationship).
        """
        return any(rule.validate(dimensions_id_list, dim_values_Dic_1, dim_values_Dic_2) for rule in self.rules)


class NetworkRuleManager:
    """Manages multiple rules for nodes and links."""

    def __init__(self, manager_id):
        """
        Initialize the RuleManager.
        :param manager_id: Unique identifier for this manager.
        """
        self.manager_id = manager_id
        self.link_rules: Dict[str, NetworkRule] = {}  # {rule_id: Rule instance}


    def add_link_rule(self, rule:NetworkRule):
        """
        Add a link rule.
        :param rule: An instance of Rule.
        """
        if rule.rule_id in self.link_rules:
            raise ValueError(f"Link rule with ID '{rule.rule_id}' already exists.")
        self.link_rules[rule.rule_id] = rule

    def validate_link(self, dimensions_id_list, dim_values_Dic_1, dim_values_Dic_2):
        """
        Validate a link by evaluating all link rules.
        :return: True if all rule passes, False otherwise (and relationship).
        """
        return all(rule.validate(dimensions_id_list, dim_values_Dic_1 , dim_values_Dic_2) for rule in self.link_rules.values())

    def list_rules(self):
        """
        List all rules managed by this manager with detailed subrule information.
        """
        print(f"Rules for RuleManager '{self.manager_id}':")

        for rule_id, rule in self.link_rules.items():
            print(f"  {rule_id}: {len(rule.rules)} subrule(s)")
            for idx, subrule in enumerate(rule.rules, start=1):
                print(f"    SubRule {idx}: {str(subrule)}")



class HighDimNetwork:
    """A network supporting high-dimensional nodes, links, and traceable dimensions."""

    def __init__(self, network_id, dimension_list:[], rule_manager=None):
        self.network_id = network_id
        self.dimension_list = dimension_list
        self.node_mapping = {}
        self.link_mapping = {}
        self.rule_manager = rule_manager or NetworkRuleManager()
        self.dimension_id_list = [i.dim_id for i in dimension_list]
        self.graph = Graph(network_id,self.dimension_id_list)

    def construct_nodes(self):
        """
        Construct nodes by enumerating all possible combinations of dimension values.
        Each dimension in `dimension_list` contributes its values to the Cartesian product.
        """
        import itertools

        # Ensure that dimensions have unique IDs
        dim_list = [dim.dim_id for dim in self.dimension_list]

        # Generate all possible combinations of dimension values
        value_ranges = [dim.values for dim in self.dimension_list]
        for combination in itertools.product(*value_ranges):
            # Create a dictionary for dim_values_dic with dimension_id as key and value from combination
            dim_values_dic = {dim_id: value for dim_id, value in zip(dim_list, combination)}

            # Create a dictionary for coordinates_dic with dimension_id as key and coordinate value
            coordinates_dic = {dim.dim_id: dim.get_coordinate(value) for dim, value in
                               zip(self.dimension_list, combination)}

            # Generate a unique node ID by joining dimension values (for human-readable purposes)
            node_id = "_".join(map(str, combination))

            # Create an optional attributes dictionary (if needed, extend this with relevant attributes)
            attributes = {
                "node_type": "default",  # Example attribute, can be replaced or extended
                "dimension_count": len(dim_list),  # Number of dimensions for this node
            }

            # Add the node to the graph using the new Node structure
            self.add_node(node_id, dim_list, dim_values_dic, coordinates_dic, attributes)

        print(f"Constructed {len(self.graph.nodes)} nodes.")  # Debug: number of nodes constructed

    def construct_links(self):# node loop for a pair of nodes for default
        """Construct links between nodes based on link rules."""
        node_ids = list(self.graph.nodes.keys())
        node_id_range=enumerate(node_ids)
        for i, source_id in node_id_range:
            for target_id in node_ids[i + 1:]:
                if source_id == target_id:
                    continue
                dim_values_dic_1 = self.graph.nodes[source_id].dim_values_dic
                dim_values_dic_2 = self.graph.nodes[target_id].dim_values_dic
                if self.rule_manager.validate_link(self.dimension_id_list, dim_values_dic_1, dim_values_dic_2):
                    self.add_link(source_id, target_id)

    def construct_network(self):
        """Construct network."""
        self.construct_nodes()
        self.construct_links()

    # def _frange(self, start, stop, step):
    #     """Helper function for generating floating-point ranges."""
    #     while start < stop:
    #         yield round(start, 10)
    #         start += step

    def add_node(self, node_id, dim_list, dim_values_dic, coordinates_dic, attributes=None):
        """Add a node to the graph."""
        self.graph.add_node(Node(node_id, dim_list, dim_values_dic, coordinates_dic, attributes))

    def add_link(self, source_id, target_id, link_id=None, attributes=None):
        """Add a link to the graph."""
        link_id = link_id or f"{source_id}_{target_id}"
        self.graph.add_link(Link(link_id, source_id, target_id, attributes))

    def merge_networks(self, other_network, merge_dimensions):
        """
        Merge dimensions and link rules from two networks, then regenerate the merged network.
        :param other_network: The other HighDimNetwork instance to merge with.
        :param merge_dimensions: List of shared dimensions to merge on.
        :return: A new HighDimNetwork instance representing the merged network.
        """
        # Validate shared dimensions
        shared_dims = [
            dim for dim in merge_dimensions
            if dim in self.dimension_id_list and dim in other_network.dimension_id_list
        ]
        if not shared_dims:
            raise ValueError("No shared dimensions found for merging.")

        # Combine dimensions from both networks
        merged_dimension_list = list({
                                         dim.dim_id: dim for dim in (self.dimension_list + other_network.dimension_list)
                                     }.values())

        # Merge link rules from both networks
        combined_rule_manager = NetworkRuleManager(f"{self.network_id}_{other_network.network_id}_rules")
        for rule_id, rule in self.rule_manager.link_rules.items():
            if rule_id not in combined_rule_manager.link_rules:
                combined_rule_manager.add_link_rule(rule)
        for rule_id, rule in other_network.rule_manager.link_rules.items():
            if rule_id not in combined_rule_manager.link_rules:
                combined_rule_manager.add_link_rule(rule)

        # Initialize the merged network with combined dimensions and rules
        combined_network = HighDimNetwork(
            network_id=f"{self.network_id}_{other_network.network_id}",
            dimension_list=merged_dimension_list,
            rule_manager=combined_rule_manager
        )

        # Regenerate nodes and links for the merged network
        combined_network.construct_network()

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