import streamlit as st
import pandas as pd
import numpy as np
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
    query_lower = query.lower()
    
    if 'temperature' in query_lower or 'temp' in query_lower:
        return {"text": "Temperature profile data available.", 'viz_type': 'temperature'}
    elif 'salinity' in query_lower:
        return {"text": "Salinity profile data available.", 'viz_type': 'salinity'}
    elif 'float' in query_lower or 'location' in query_lower or 'map' in query_lower:
        return {"text": "Float location data available.", 'viz_type': 'map'}
    elif 'compare' in query_lower or 'ts' in query_lower:
        return {"text": "T-S comparison data available.", 'viz_type': 'compare'}
    else:
        return {"text": "Try asking: Show temperature profiles, Find floats near coordinates, or Compare salinity data.", 'viz_type': None}

# Main header
st.markdown('<div class="main-header">🌊 FloatChat- AI Conversational Ocean Data Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">ARGO Float Data Explorer</div>', unsafe_allow_html=True)

# Load data
floats_df, profiles_df = generate_mock_argo_data()

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.subheader("Data Source")
    data_source = st.selectbox("Select Region", ["Indian Ocean", "Arabian Sea", "Bay of Bengal", "Global"])
    
    st.subheader("Date Range")
    date_range = st.date_input("Select date range", value=(datetime.now() - timedelta(days=180), datetime.now()), max_value=datetime.now())
    
    st.subheader("Parameters")
    params = st.multiselect("Select parameters", ["Temperature", "Salinity", "Pressure", "Oxygen", "Chlorophyll"], default=["Temperature", "Salinity"])
    
    st.divider()
    
    st.subheader("📊 Quick Stats")
    col1, col2 = st.columns(2)
    col1.metric("Active Floats", len(floats_df[floats_df['status'] == 'active']))
    col2.metric("Total Profiles", int(floats_df['profiles_count'].sum()))
    
    st.divider()
    
    st.subheader("🔍 Query Examples")
    examples = ["Show temperature profiles", "Find floats near equator", "Compare salinity data", "Map active floats"]
    for example in examples:
        if st.button(example, key=example, use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": example})
            response = process_nl_query(example)
            st.session_state.chat_history.append({"role": "assistant", "content": response['text']})
            st.rerun()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Interface", "🗺️ Float Data", "📈 Profiles", "📊 Dashboard"])

with tab1:
    st.header("AI Assistant")
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
    st.header("ARGO Float Data")
    st.subheader("Float Details")
    st.dataframe(floats_df, use_container_width=True, hide_index=True)

with tab3:
    st.header("Oceanographic Profiles")
    st.subheader("Temperature & Salinity Data")
    st.dataframe(profiles_df, use_container_width=True)
    
    st.subheader("📥 Export Data")
    col1, col2 = st.columns(2)
    col1.download_button("Download CSV", profiles_df.to_csv(index=False).encode('utf-8'), "argo_profiles.csv", "text/csv")
    col2.download_button("Download JSON", profiles_df.to_json(orient='records'), "argo_profiles.json", "application/json")

with tab4:
    st.header("Analytics Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Floats", len(floats_df))
    col2.metric("Avg Temperature", f"{profiles_df['temperature'].mean():.1f}°C")
    col3.metric("Avg Salinity", f"{profiles_df['salinity'].mean():.2f} PSU")
    col4.metric("Max Depth", f"{profiles_df['depth'].max():.0f}m")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Floatchat- AI Conversational Ocean Data Assistant</strong></p>
    <p style='font-size: 0.9rem;'>Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
