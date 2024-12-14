from typing import Dict, List
try:
    import networkx as nx
except ImportError:
    nx = None

try:
    from dgl import DGLGraph
except ImportError:
    DGLGraph = None

try:
    import cudf
    from cugraph.structure.graph import Graph as CuGraph
except ImportError:
    cudf = None
    CuGraph = None

try:
    from pyomo.environ import ConcreteModel, Var, Objective, Constraint
except ImportError:
    ConcreteModel = None
    Var = None
    Objective = None
    Constraint = None

class Node:
    def __init__(self, node_id, dim_list, dim_values_dic, coordinates_dic, attributes=None):
        """
        Initialize a Node.
        :param node_id: Unique identifier for the node.
        :param dim_list: List[str], names of dimensions (e.g., ["X", "Y", "Z"]).
        :param dim_values_dic: Dict[str, Any], mapping of dimension names to their values (e.g., {"X": 1, "Y": 2}).
        :param coordinates_dic: Dict[str, float], mapping of dimension names to their coordinates (e.g., {"X": 0.1, "Y": 0.2}).
        :param attributes: Optional[Dict[str, Any]], additional attributes for the node.
        """
        self.node_id = node_id
        self.dim_list = dim_list
        self.dim_values_dic = dim_values_dic
        self.coordinates_dic = coordinates_dic
        self.attributes = attributes or {}

        # Ensure the dimensions match
        if set(self.dim_list) != set(self.dim_values_dic.keys()):
            raise ValueError("Dimension names in dim_list must match keys in dim_values_dic.")
        if set(self.dim_list) != set(self.coordinates_dic.keys()):
            raise ValueError("Dimension names in dim_list must match keys in coordinates_dic.")

        # Generate tuples for dim_values and coordinates
        self.dim_values = tuple(self.dim_values_dic[dim] for dim in self.dim_list)
        self.coordinates = tuple(self.coordinates_dic[dim] for dim in self.dim_list)

    def get_coords_value(self, dimension: str):
        """
        Get the value of a specific dimension for this node.
        """
        return self.coordinates_dic.get(dimension, None)
    def to_dict(self):
        """
        Convert the node to a dictionary representation.
        :return: A dictionary containing node details.
        """
        return {
            "id": self.node_id,
            "dim_list": self.dim_list,
            "dim_values_dic": self.dim_values_dic,
            "coordinates_dic": self.coordinates_dic,
            "dim_values": self.dim_values,
            "coordinates": self.coordinates,
            "attributes": self.attributes,
        }

    def get_dim_values_tuple(self):
        """
        Get the tuple representation of the dimension values.
        :return: Tuple of dimension values.
        """
        return self.dim_values

    def get_coordinates_tuple(self):
        """
        Get the tuple representation of the coordinates.
        :return: Tuple of coordinates.
        """
        return self.coordinates

    def __repr__(self):
        """
        Return a string representation of the Node.
        """
        return (f"Node(id={self.node_id}, dim_list={self.dim_list}, dim_values={self.dim_values}, "
                f"coordinates={self.coordinates}, attributes={self.attributes})")


    def __repr__(self):
        return f"Node(id={self.node_id}, dim_values_dic={self.dim_values_dic} coordinates={self.coordinates}, attributes={self.attributes})"


class Link:
    def __init__(self, link_id, source, target, attributes=None):
        """
        :param link_id: Unique identifier for the link.
        :param source: Source node ID.
        :param target: Target node ID.
        :param attributes: Dictionary of attributes for the link.
        """
        self.link_id = link_id
        self.source = source
        self.target = target
        self.attributes = attributes or {}

    def to_dict(self):
        """Convert the link to a dictionary representation."""
        return {
            "id": self.link_id,
            "source": self.source,
            "target": self.target,
            "attributes": self.attributes,
        }

    def __repr__(self):
        return (f"Link(id={self.link_id}, source={self.source}, target={self.target}, "
                f"attributes={self.attributes})")


class Graph:
    def __init__(self, network_id: str, dimension_id_list: List[str]):
        """
        Initialize the Graph with a network ID and a list of dimensions.
        :param network_id: Unique identifier for the graph.
        :param dimension_id_list: List of dimension IDs associated with this graph.
        """
        self.network_id = network_id
        self.dimension_id_list = dimension_id_list
        self.nodes: Dict[str, Node] = {}  # Stores nodes by their ID
        self.links: Dict[str, Link] = {}  # Stores links by their ID

    def add_node(self, node):
        """
        Add a Node to the Graph.
        """
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists.")
        self.nodes[node.node_id] = node

    def add_link(self, link):
        """
        Add a Link to the Graph.
        """
        if not (link.source in self.nodes and link.target in self.nodes):
            raise ValueError("Both source and target nodes must exist in the graph.")
        self.links[link.link_id] = link

    def project_to_dimensions(self, dimension_list: List[str]) -> Dict[str, List[Dict]]:
        """
        Project the Graph onto a given dimensional plane.
        :param dimension_list: List of dimensions to project onto.
        :return: Dictionary containing nodes and links in the projection.
        """
        if not all(dim in self.dimension_id_list for dim in dimension_list):
            raise ValueError("Some dimensions in the input list are not part of the graph's dimensions.")

        # Project nodes
        projected_nodes = []
        for node_id, node in self.nodes.items():
            # Extract relevant dimension values for the projection
            projected_coordinates = {dim: node.get_coords_value(dim) for dim in dimension_list if dim in node.dim_list}
            if len(projected_coordinates) == len(dimension_list):  # Ensure all dimensions exist for this node
                projected_nodes.append({"node_id": node.node_id, "coordinates": projected_coordinates})

        # Project links
        projected_links = []
        for link in self.links.values():
            source_node = self.nodes[link.source]
            target_node = self.nodes[link.target]

            # Extract relevant dimension values for source and target
            source_projection = {dim: source_node.get_coords_value(dim) for dim in dimension_list if dim in source_node.dim_list}
            target_projection = {dim: target_node.get_coords_value(dim) for dim in dimension_list if dim in target_node.dim_list}

            if len(source_projection) == len(dimension_list) and len(target_projection) == len(dimension_list):
                projected_links.append({
                    "link_id": link.link_id,
                    "source": {"node_id": link.source, "coordinates": source_projection},
                    "target": {"node_id": link.target, "coordinates": target_projection}
                })

        return {
            "nodes": projected_nodes,
            "links": projected_links
        }

    def to_networkx(self):
        if nx is None:
            raise ImportError("NetworkX is not installed. Please install it using `pip install networkx`.")
        nx_graph = nx.DiGraph()
        for node in self.nodes.values():
            nx_graph.add_node(node.node_id, **node.to_dict())
        for link in self.links:
            nx_graph.add_edge(link.source, link.target, **link.to_dict())
        return nx_graph

    def to_dgl(self):
        if DGLGraph is None:
            raise ImportError("DGL is not installed. Please install it using `pip install dgl`.")
        dgl_graph = DGLGraph()
        node_ids = list(self.nodes.keys())
        node_index_map = {node_id: idx for idx, node_id in enumerate(node_ids)}
        dgl_graph.add_nodes(len(node_ids))
        for link in self.links:
            dgl_graph.add_edges(
                node_index_map[link.source],
                node_index_map[link.target],
                data={key: [value] for key, value in link.to_dict().items()},
            )
        return dgl_graph

    def to_cugraph(self):
        if cudf is None or CuGraph is None:
            raise ImportError(
                "cuGraph is not installed or the necessary dependencies are missing. "
                "Please install cuGraph using the NVIDIA RAPIDS installation guide."
            )
        source = []
        target = []
        attributes = {}
        for link in self.links:
            source.append(link.source)
            target.append(link.target)
            for key, value in link.to_dict()["attributes"].items():
                if key not in attributes:
                    attributes[key] = []
                attributes[key].append(value)
        gdf = cudf.DataFrame({"source": source, "target": target, **attributes})
        cu_graph = CuGraph()
        cu_graph.from_cudf_edgelist(gdf, source="source", destination="target")
        return cu_graph

    def to_pyomo(self):
        if ConcreteModel is None:
            raise ImportError(
                "Pyomo is not installed. Please install it using `pip install pyomo`."
            )
        model = ConcreteModel()
        model.nodes = list(self.nodes.keys())
        model.links = [(link.source, link.target) for link in self.links]
        model.link_cost = Var(model.links, domain=Var().domain, initialize=1)
        model.objective = Objective(expr=sum(model.link_cost[link] for link in model.links))
        model.constraints = Constraint(expr=model.objective >= 0)
        return model

    def __repr__(self):
        return f"Graph(id={self.network_id}, nodes={len(self.nodes)}, links={len(self.links)})"


class Path:
    def __init__(self, nodes):
        self.nodes = nodes

    def length(self):
        return len(self.nodes)

    def __repr__(self):
        return f"Path(nodes={self.nodes})"