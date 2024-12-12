from Dimension2Network import HighDimNetwork, RuleManager
from visulizations.graph_visualizer import GraphVisualizer
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

if __name__ == "__main__":
    # Rule definitions
    rule_manager_xy = RuleManager()
    rule_manager_xy.add_node_rule("rule1", ["X", "Y"], lambda x, y: x + y < 0.6)
    rule_manager_xy.add_link_rule("rule1", ["Y"], lambda y1, y2: abs(y1 - y2) < 0.2)

    rule_manager_yz = RuleManager()
    rule_manager_yz.add_node_rule("rule1", ["Y", "Z"], lambda y, z: y + z < 1.0)
    rule_manager_yz.add_link_rule("rule1", ["Y"], lambda y1, y2: abs(y1 - y2) < 0.3)

    # Create two networks
    network_xy = HighDimNetwork("XY", 2, ["X", "Y"], ranges=[(0, 1), (0, 1)], steps=[0.1, 0.1], rule_manager=rule_manager_xy)
    network_yz = HighDimNetwork("YZ", 2, ["Y", "Z"], ranges=[(0, 1), (0, 1)], steps=[0.1, 0.2], rule_manager=rule_manager_yz)

    # Construct nodes and links
    network_xy.construct_nodes()
    network_xy.construct_links()
    network_yz.construct_nodes()
    network_yz.construct_links()

    # Merge networks
    merged_network = network_xy.merge_networks(network_yz, merge_dimensions=["Y"])

    # Output mappings
    print("Node Mapping:")
    for node_id, mapping in merged_network.node_mapping.items():
        print(f"{node_id}: {mapping}")

    print("Link Mapping:")
    for link_id, mapping in merged_network.link_mapping.items():
        print(f"{link_id}: {mapping}")

    # Visualize the network
    visualizer = GraphVisualizer(merged_network.graph)
    app = visualizer.create_dash_app()

    # Run the Dash app
    print("Initializing the Dash server...")
    try:
        Timer(1, open_browser).start()
        app.run_server(debug=True, port=8050)
    except Exception as e:
        print(f"Error starting Dash server: {e}")