import streamlit as st
from scipy.interpolate import interp1d
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 

def create_series(control_points, y_range, cycles, noise=0.05 ):

    # Sort control points by x value
    # Sort control points by y value
    control_points.sort()

    # Generate x values for each control point
    ys = control_points
    xs = np.linspace(0, 1, len(ys))

    # Create spline
    spline = interp1d(xs, ys, kind='quadratic')

    # Generate x values for each day in the date range
    x = np.linspace(0, 1, num=cycles, endpoint=True)

    # Generate y values (spline)
    y = spline(x)

    y += np.random.normal(0, noise, size=y.shape)

    # Apply Min-Max scaling to y values
    y_min, y_max = np.min(y), np.max(y)
    y = (y - y_min) / (y_max - y_min)  # Min-Max scaling

    # Scale y values to provided y range
    y = y * (y_range[1] - y_range[0]) + y_range[0]

    # Create a pandas Series with dates as the index
    spline_series = pd.Series(y)

    return spline_series

def generate_independent_subnodes(config, super_node_id, cycles):
    n_subnodes = config['n_subnodes']
    boundaries = config['boundaries']
    control_points = config['control_points']

    subnodes = {}

    for i in range(n_subnodes):
        base = create_series(control_points, boundaries[i], cycles)
        subnodes[i] = base
        
        base_temp = {}

        base_temp['base'] = base

        st.download_button(
            label=f'Download for Sub Node {i}',
            data=pd.DataFrame(base_temp).to_csv(),
            file_name=f'subnode_{super_node_id}_{i}.csv',
            mime='text/csv'
        )

        show_preview = st.toggle("Show Preview", value=False, key=f"subnode_{super_node_id}_{i}")

        if show_preview:
            st.table(subnodes[i])


    fig = px.line(pd.DataFrame(subnodes))
    st.plotly_chart(fig)

    return subnodes

def generate_dependent_subnodes(config, super_node_id, cycles, generated_series):
    n_subnodes = config['n_subnodes']
    boundaries = config['boundaries']
    control_points = config['control_points']

    subnodes = {}

    for i in range(n_subnodes):
        
        base = create_series(control_points, boundaries[i], cycles)

        for j in range(config['n_incomming_nodes']):

            value = config['inputs'][j]

            temp = {}


            for k in range(len(value['connections'])):
                input_series = pd.Series(generated_series[value['input_supernode']][value['connections'][k]])
                temp[k] = input_series

                base += input_series * value['weight'] * value['correlation']
        
        temp['base'] = base
        subnodes[i] = base

        st.download_button(
            label=f'Download for Sub Node {i}',
            data=pd.DataFrame(temp).to_csv(),
            file_name=f'subnode_{super_node_id}_{i}.csv',
            mime='text/csv'
        )

        show_preview = st.toggle("Show Preview", value=False, key=f"subnode_{super_node_id}_{i}")

        if show_preview:
            st.table(subnodes[i])

    # st.table(subnodes)
    fig = px.line(pd.DataFrame(subnodes))
    st.plotly_chart(fig) 

    return subnodes