from Dimension2Network.Dimension2Network import HighDimNetwork, NetworkRuleManager, NetworkRule, Rule, Dimension
from visulizations.graph_output import GraphDrawer
from visulizations.graph_visualizer import GraphVisualizer
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")


if __name__ == "__main__":
    # Step 1: Define dimensions for XY network
    dimension_x = Dimension(
        dim_id="X",
        values=["A", "B", "C"],
        attributes={
            "A": {"type": "start"},
            "B": {"type": "intermediate"},
            "C": {"type": "end"}
        },
        start=0,
        step=1
    )

    dimension_y = Dimension(
        dim_id="Y",
        values=[0.1, 0.2, 0.3],
        attributes={
            0.1: {"category": "low"},
            0.2: {"category": "medium"},
            0.3: {"category": "high"}
        },
        start=0.1,
        step=0.10
    )

    # Step 2: Set up a rule manager and define rules for the XY network
    rule_manager_xy = NetworkRuleManager("rule_xy")
    link_rule_xy = NetworkRule("rule_link_xy", ["Y"])
    link_rule_xy.add_subrule(Rule(["Y"], lambda y1, y2: (y1 - y2) < 0.05))
    rule_manager_xy.add_link_rule(link_rule_xy)

    # Step 3: Create the XY network
    network_xy = HighDimNetwork(
        network_id="XY_Network",
        dimension_list=[dimension_x, dimension_y],
        rule_manager=rule_manager_xy
    )
    network_xy.construct_network()

    # Step 4: Define dimensions for YZ network
    dimension_z = Dimension(
        dim_id="Z",
        values=["001", "010", "100", "110", "101", "011", "111", "000"],
        attributes={
            "001": {"category": "low"},
            "010": {"category": "medium"},
            "100": {"category": "high"},
            "110": {"category": "medium-high"},
            "101": {"category": "medium-low"},
            "011": {"category": "balanced"},
            "111": {"category": "very high"},
            "000": {"category": "very low"}
        },
        start=0.1,
        step=0.1
    )

    # Set up a rule manager and define rules for the YZ network
    rule_manager_yz = NetworkRuleManager("rule_yz")
    link_rule_yz = NetworkRule("rule_link_yz", ["Y", "Z"])
    link_rule_yz.add_subrule(Rule(["Y", "Z"], lambda y1, z1, y2, z2: (y1 - y2) < 0.15 and z1 != z2))
    rule_manager_yz.add_link_rule(link_rule_yz)

    # Create the YZ network
    network_yz = HighDimNetwork(
        network_id="YZ_Network",
        dimension_list=[dimension_y, dimension_z],
        rule_manager=rule_manager_yz
    )
    network_yz.construct_network()

    # Step 5: Merge the XY and YZ networks
    merged_network = network_xy.merge_networks(network_yz, merge_dimensions=["Y"])

    # Output results for merged network
    merged_network.print_graph_summary()

    # Print all nodes in the merged network
    print("\nMerged Network Nodes:")
    for node_id, node in merged_network.graph.nodes.items():
        print(f"  Node ID: {node_id}, Dim Values: {node.dim_values_dic}, Coordinates: {node.coordinates_dic}")

    # Print all links in the merged network
    print("\nMerged Network Links:")
    for link_id, link in merged_network.graph.links.items():
        print(f"  Link ID: {link_id}, Source: {link.source}, Target: {link.target}")

    # Visualize the merged network
    visualizer = GraphDrawer(merged_network.dimension_list,merged_network.graph)
    visualizer.plot_projection(["X", "Y"])
    visualizer.plot_projection(["X", "Z"])
    visualizer.plot_projection(["Y", "Z"])
    if None:
        visualizer = GraphVisualizer(merged_network.graph)
        app = visualizer.create_dash_app()
        # Run the Dash app
        print("Initializing the Dash server...")
        try:
            Timer(1, open_browser).start()
            app.run_server(debug=True, port=8050)
        except Exception as e:
            print(f"Error starting Dash server: {e}")