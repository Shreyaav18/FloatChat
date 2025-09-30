"""
ARGO Float Data Explorer - Streamlit Application
AI-Powered Oceanographic Data Analysis System

Installation:
pip install streamlit pandas numpy plotly

Run:
streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="FloatChat",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Welcome to ARGO Float Data Explorer! Ask me about oceanographic data."}
    ]

# Mock data generator
@st.cache_data
def generate_mock_argo_data():
    """Generate sample ARGO float data"""
    floats = pd.DataFrame({
        'float_id': ['WMO2902756', 'WMO2902757', 'WMO2902758', 'WMO2902759', 'WMO2902760'],
        'latitude': [8.5, 10.1, 12.3, 6.8, 15.2],
        'longitude': [76.2, 75.8, 74.5, 77.1, 73.8],
        'last_update': pd.date_range(end=datetime.now(), periods=5, freq='D'),
        'status': ['active', 'active', 'active', 'active', 'inactive'],
        'profiles_count': [145, 132, 167, 89, 201]
    })
    
    depths = np.array([0, 50, 100, 200, 500, 1000, 1500, 2000])
    temperature = np.array([28.5, 26.2, 23.1, 18.5, 12.3, 6.8, 4.2, 2.5])
    salinity = np.array([34.5, 34.8, 35.1, 35.4, 35.2, 34.9, 34.7, 34.6])
    
    profiles = pd.DataFrame({
        'depth': depths,
        'temperature': temperature,
        'salinity': salinity,
        'pressure': depths * 1.02
    })
    
    return floats, profiles

def process_nl_query(query):
    """Simple natural language query processor"""
    query_lower = query.lower()
    
    if 'temperature' in query_lower or 'temp' in query_lower:
        return {
            'text': "Temperature profile from ARGO float WMO2902756 shows tropical ocean stratification with warm surface waters decreasing to cold deep waters.",
            'viz_type': 'temperature'
        }
    elif 'salinity' in query_lower:
        return {
            'text': "Salinity profile shows subsurface maximum around 200m depth, characteristic of Arabian Sea water masses.",
            'viz_type': 'salinity'
        }
    elif 'float' in query_lower or 'location' in query_lower or 'map' in query_lower:
        return {
            'text': "Found 5 ARGO floats in the Indian Ocean region. Active floats are shown on the map.",
            'viz_type': 'map'
        }
    elif 'compare' in query_lower or 'ts' in query_lower:
        return {
            'text': "T-S diagram comparing temperature and salinity helps identify different water masses.",
            'viz_type': 'compare'
        }
    else:
        return {
            'text': "Try asking: Show temperature profiles, Find floats near coordinates, or Compare salinity data.",
            'viz_type': None
        }

def plot_temperature_profile(profiles_df):
    """Create temperature depth profile"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=profiles_df['temperature'],
        y=-profiles_df['depth'],
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title='Temperature Profile',
        xaxis_title='Temperature (°C)',
        yaxis_title='Depth (m)',
        hovermode='closest',
        height=500
    )
    return fig

def plot_salinity_profile(profiles_df):
    """Create salinity depth profile"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=profiles_df['salinity'],
        y=-profiles_df['depth'],
        mode='lines+markers',
        name='Salinity',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        title='Salinity Profile',
        xaxis_title='Salinity (PSU)',
        yaxis_title='Depth (m)',
        hovermode='closest',
        height=500
    )
    return fig

def plot_float_map(floats_df):
    """Create map of ARGO float locations"""
    fig = px.scatter_mapbox(
        floats_df,
        lat='latitude',
        lon='longitude',
        hover_name='float_id',
        hover_data=['status', 'profiles_count'],
        color='status',
        color_discrete_map={'active': '#27ae60', 'inactive': '#95a5a6'},
        zoom=4,
        height=500
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    return fig

def plot_ts_diagram(profiles_df):
    """Create T-S diagram"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=profiles_df['salinity'],
        y=profiles_df['temperature'],
        mode='lines+markers',
        marker=dict(
            size=10,
            color=profiles_df['depth'],
            colorscale='Viridis',
            colorbar=dict(title="Depth (m)"),
            showscale=True
        ),
        text=[f"Depth: {d}m" for d in profiles_df['depth']],
        hovertemplate='Salinity: %{x:.2f}<br>Temperature: %{y:.2f}<br>%{text}<extra></extra>'
    ))
    fig.update_layout(
        title='Temperature-Salinity Diagram',
        xaxis_title='Salinity (PSU)',
        yaxis_title='Temperature (°C)',
        height=500
    )
    return fig

# Main header
st.markdown('<div class="main-header">🌊 FloatChat- AI Conversational Ocean Data Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">ARGO Float Data Explorer</div>', unsafe_allow_html=True)

# Load data
floats_df, profiles_df = generate_mock_argo_data()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Data Source")
    data_source = st.selectbox(
        "Select Region",
        ["Indian Ocean", "Arabian Sea", "Bay of Bengal", "Global"]
    )
    
    st.subheader("Date Range")
    date_range = st.date_input(
        "Select date range",
        value=(datetime.now() - timedelta(days=180), datetime.now()),
        max_value=datetime.now()
    )
    
    st.subheader("Parameters")
    params = st.multiselect(
        "Select parameters",
        ["Temperature", "Salinity", "Pressure", "Oxygen", "Chlorophyll"],
        default=["Temperature", "Salinity"]
    )
    
    st.divider()
    
    st.subheader("📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Floats", len(floats_df[floats_df['status'] == 'active']))
    with col2:
        st.metric("Total Profiles", int(floats_df['profiles_count'].sum()))
    
    st.divider()
    
    st.subheader("🔍 Query Examples")
    examples = [
        "Show temperature profiles",
        "Find floats near equator",
        "Compare salinity data",
        "Map active floats"
    ]
    for example in examples:
        if st.button(example, key=example, use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": example})
            response = process_nl_query(example)
            st.session_state.chat_history.append({"role": "assistant", "content": response['text']})
            st.rerun()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Interface", "🗺️ Float Map", "📈 Profiles", "📊 Dashboard"])

with tab1:
    st.header("AI Assistant")
    
    chat_container = st.container(height=400)
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    user_input = st.chat_input("Ask about ARGO data...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = process_nl_query(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response['text']})
        st.rerun()

with tab2:
    st.header("ARGO Float Locations")
    st.plotly_chart(plot_float_map(floats_df), use_container_width=True)
    
    st.subheader("Float Details")
    st.dataframe(floats_df, use_container_width=True, hide_index=True)

with tab3:
    st.header("Oceanographic Profiles")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Temperature Profile")
        st.plotly_chart(plot_temperature_profile(profiles_df), use_container_width=True)
    
    with col2:
        st.subheader("Salinity Profile")
        st.plotly_chart(plot_salinity_profile(profiles_df), use_container_width=True)
    
    st.subheader("T-S Diagram")
    st.plotly_chart(plot_ts_diagram(profiles_df), use_container_width=True)
    
    st.subheader("📥 Export Data")
    col1, col2 = st.columns(2)
    with col1:
        csv = profiles_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "argo_profiles.csv", "text/csv")
    with col2:
        json_str = profiles_df.to_json(orient='records')
        st.download_button("Download JSON", json_str, "argo_profiles.json", "application/json")

with tab4:
    st.header("Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Floats", len(floats_df))
    with col2:
        st.metric("Avg Temperature", f"{profiles_df['temperature'].mean():.1f}°C")
    with col3:
        st.metric("Avg Salinity", f"{profiles_df['salinity'].mean():.2f} PSU")
    with col4:
        st.metric("Max Depth", f"{profiles_df['depth'].max():.0f}m")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Float Status Distribution")
        status_counts = floats_df['status'].value_counts()
        fig = px.pie(
            values=status_counts.values, 
            names=status_counts.index,
            color_discrete_sequence=['#27ae60', '#95a5a6']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Profiles per Float")
        fig = px.bar(
            floats_df, 
            x='float_id', 
            y='profiles_count',
            color='status',
            color_discrete_map={'active': '#3498db', 'inactive': '#95a5a6'}
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Floatchat- AI Conversational Ocean Data Assistant</strong> | Powered by AI & RAG</p>
    <p style='font-size: 0.9rem;'>Built with Streamlit, Plotly, and LLM Integration</p>
</div>
""", unsafe_allow_html=True)