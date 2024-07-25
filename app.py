import streamlit as st
import yaml

from config_generator import config_generator
from generate import generate_dependent_subnodes, generate_independent_subnodes


def network_timeseries():
    st.title("Network Time Series Data Generator")

    config = None
    
    input_mechanism = st.selectbox("How do you want to enter the configurations?", ["UI", "YAML File"])

    st.divider()
    
    if input_mechanism == "UI":
        config = config_generator()
        
        config = yaml.dump(config)
        config = yaml.safe_load(config)
        
        
    else:
        uploaded_file = st.file_uploader("Upload YAML Configuration File", type=['yaml', 'yml'])

        if uploaded_file is not None:
            file_contents = uploaded_file.read()
            config = yaml.safe_load(file_contents)
                    
    if config is not None:
        st.subheader("Configuration")
        st.write(config)
        is_generate = st.button("Generate Data")
        st.divider()
        
        
        if is_generate:
            st.header("Generated Data")
            generated_series = {}

            for key, value in config['supernodes'].items():

                if value['node_type'] == 'independent':
                    st.subheader(f"Independent Super Node {key+1}")

                    generated_series[key] = generate_independent_subnodes(value, key, config['n_cycles'])

            for key, value in config['supernodes'].items():
                if value['node_type'] == 'dependent':
                    st.subheader(f"Dependent Super Node {key+1}")

                    generated_series[key] = generate_dependent_subnodes(value, key, config['n_cycles'], generated_series)
        
if __name__ == "__main__":
    network_timeseries()