import streamlit as st
import yaml
from scipy.special import comb
import numpy as np
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import networkx as nx
from pyvis.network import Network


def bernstein_poly(i, n, t):
    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i

def bezier_curve(in_points, num=200):

    points = []
    for i in range(len(in_points)):
        x = i/(len(in_points)-1)
        y = in_points[i]
        points.append((x, y))
    
    points = np.array(points)
    N = len(points)
    t = np.linspace(0, 1, num=num)
    curve = np.zeros((num, 2))
    for i in range(N):
        curve += np.outer(bernstein_poly(i, N - 1, t), points[i])

    fig, ax = plt.subplots()
    ax.plot(points[:,0], points[:,1], 'ro-', label='Control Points')
    ax.plot(curve[:,0], curve[:,1], 'b-', label='Spline')
    ax.legend()
    ax.grid(True)
    ax.set_title(f'Spline with {len(in_points)} Control Points')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    st.pyplot(fig)

def create_graph(net):

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = '/tmp'
        net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Save and read graph as HTML file (locally)
    except:
        net.show('pyvis_graph.html')
        HtmlFile = open('pyvis_graph.html', 'r', encoding='utf-8')

    # Read the HTML file
    source_code = HtmlFile.read()

    return components.html(source_code, height=400)

def config_generator():
    st.header("Configuration")

    supernode_graph = Network(
                height='400px',
                width='100%',
                bgcolor='white',
                font_color='black',
                directed=True,
                neighborhood_highlight=True,
            )
    
    subnode_graph = Network(
                height='400px',
                width='100%',
                bgcolor='white',
                font_color='black',
                directed=True,
                neighborhood_highlight=True,
            )

    combined_graph = Network(
                height='400px',
                width='100%',
                bgcolor='white',
                font_color='black',
                directed=True,
                neighborhood_highlight=True,
            )

    super_nodes_data = {}

    super_nodes_data['n_supernodes'] = st.number_input("Number of super nodes", 1, step=1)

    super_nodes_data['n_cycles'] = st.number_input("Number of cycles", 100, step=100)

    super_nodes_data['supernodes'] = {}
 

    for i in range(super_nodes_data['n_supernodes']):

        st.subheader(f"Super Node {i+1}")

        supernode_graph.add_node(f"{i}", label=f"Super Node {i+1}", group=i)
        combined_graph.add_node(f"{i}", label=f"Super Node {i+1}", group=i, borderWidth=5, size=40)

        n_nodes = st.number_input(f"Number of SUB NODES for SUPER NODE {i+1}", 1, step=1, key=f"n_nodes_{i}")

        control_points = []

        control_points_in = st.text_input(f"Comma separated control points (between 0 and 1) for Super Node {i+1}", key=f"control_points_{i}")

        if control_points_in:
            control_points = [float(x) for x in control_points_in.split(',')]
            bezier_curve(control_points, super_nodes_data['n_cycles'])

        boundaries = []
        for j in range(n_nodes):

            subnode_graph.add_node(f"{i}_{j}", label=f"Sub Node {j+1}", group=i)
            combined_graph.add_node(f"{i}_{j}", label=f"Sub Node {j+1}", group=i)
            combined_graph.add_edge(f"{i}", f"{i}_{j}")


            bounds = st.text_input(f"Comma separated bounds <lower,upper> for Sub Node {j+1} for Super Node {i+1}")

            if bounds:
                bounds = [float(x) for x in bounds.split(',')]
            else:
                bounds = [0,1]

            boundaries.append(bounds)

        node_type = st.selectbox(f"Type for Super Node {i+1}", ['independent', 'dependent'])

        
        if node_type == 'dependent':
            n_incoming_nodes = st.number_input(f"Number of incoming nodes for Super Node {i+1}", 1, step=1, key=f"n_incoming_nodes_{i}")

            inputs = []

            for j in range(n_incoming_nodes):
                
                st.subheader(f"Incomming Super Node {j+1} for Super Node {i+1}")

                input_supernode = st.selectbox(f"Incomming Super Node", list(super_nodes_data['supernodes'].keys()), key=f"input_supernode_{i}_{j}")

                if input_supernode is not None:

                    supernode_graph.add_edge(f"{input_supernode}", f"{i}")
                    combined_graph.add_edge(f"{input_supernode}", f"{i}", width=200)

                    correlation = st.number_input(f"Correlation for Incomming Node {j+1} for Super Node {i+1}", -1.0, 1.0, 0.0, key=f"correlation_{i}_{j}")
                    weight = st.number_input(f"Weight for Incomming Node {j+1} for Super Node {i+1}", 0.0, 1.0, 0.0, key=f"weight_{i}_{j}")
                    
                    connections_main = []
                    connection_graph = []
                    for k in range(n_nodes):
                        connection = st.text_input(f"Comma separated connections (binary list of size N(subnodes of incoming supernode)) for Sub Node {k+1}", key=f"connection_{i}_{j}_{k}")

                        connections = list(int(x) for x in connection.split(',')) if connection else []

                        if connections:
                            for ind in range(len(connections)):

                                if connections[ind] == 1:
                                    
                                    # check if nodes exist
                                    if f"{input_supernode}_{ind}" not in subnode_graph.nodes:
                                        subnode_graph.add_node(f"{input_supernode}_{ind}", label=f"Sub Node {ind+1}", group=input_supernode)

                                    if f"{i}_{k}" not in subnode_graph.nodes:
                                        subnode_graph.add_node(f"{i}_{k}", label=f"Sub Node {k+1}", group=i)

                                    # check if edge exists has_edge does not work
                                    
                                    if (f"{input_supernode}_{ind}", f"{i}_{k}") not in connection_graph:
                                        subnode_graph.add_edge(f"{input_supernode}_{ind}", f"{i}_{k}")
                                        combined_graph.add_edge(f"{input_supernode}_{ind}", f"{i}_{k}")
                                        connection_graph.append((f"{input_supernode}_{ind}", f"{i}_{k}"))

                        connections_main.append(connections)
                    st.write(connections_main)

                    # expected_lower_bound = st.number_input(f"Enter expected lower bound for Incomming node {j+1} for Super Node {i+1}")
                    # expected_upper_bound = st.number_input(f"Enter expected upper bound for Incomming node {j+1} for Super Node {i+1}")
                    # expected_mean = st.number_input(f"Enter expected mean for Incomming node {j+1} for Super Node {i+1}")

                    inputs.append({
                        'input_supernode': input_supernode,
                        'correlation': correlation,
                        'weight': weight,
                        'connections': connections,
                        # 'expected_lower_bound': expected_lower_bound,
                        # 'expected_upper_bound': expected_upper_bound,
                        # 'expected_mean': expected_mean
                    })
        else:
            n_incoming_nodes = 0
            inputs = []
        
        

        super_nodes_data['supernodes'][i] = {
            'node_type': node_type,
            'n_subnodes': n_nodes,
            'boundaries': boundaries,
            'control_points': control_points,
            'n_incomming_nodes': n_incoming_nodes,
            'inputs': inputs
        }

    st.subheader("Super Node Graph")

    supernode_vis_check = st.toggle("Visualize Super Node Graph")

    if supernode_vis_check:
        supernode_graph.save_graph('./pages/supernode_graph.html')
        source_code = open('./pages/supernode_graph.html', 'r', encoding='utf-8').read()
        components.html(source_code, height=400)

    st.subheader("Sub Node Graph")

    subnode_graph_check = st.toggle("Visualize Sub Node Graph")

    if subnode_graph_check:
        subnode_graph.save_graph('./pages/subnode_graph.html')
        source_code = open('./pages/subnode_graph.html', 'r', encoding='utf-8').read()
        components.html(source_code, height=400)

    # st.subheader("Combined Node Graph")

    # combined_graph_check = st.toggle("Visualize Combined Graph")

    # if combined_graph_check:
    #     combined_graph.save_graph('./pages/combined_graph.html')
    #     source_code = open('./pages/combined_graph.html', 'r', encoding='utf-8').read()
    #     components.html(source_code, height=400)
        
    is_generate = st.button("Generate Config")
    
    if is_generate:
        # Convert the dictionary into a YAML formatted string
        yaml_config = yaml.dump(super_nodes_data)

        # Create a download button for the YAML configuration file
        st.download_button(
            label="Download YAML Configuration File",
            data=yaml_config,
            file_name='config.yaml',
            mime='application/x-yaml'
        )

    return super_nodes_data

if __name__ == "__main__":
    config_generator()