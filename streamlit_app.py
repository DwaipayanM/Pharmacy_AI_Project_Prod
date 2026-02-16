# streamlit_app.py - Production Web Interface for Pharmacy AI

"""
PHARMACY AI - STREAMLIT WEB INTERFACE
Deploy to Streamlit Cloud for FREE production hosting
"""

import streamlit as st
import sys
from datetime import datetime
import os

# Configure page
st.set_page_config(
    page_title="Pharmacy AI - Master Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import master agent
try:
    from master_agent import MasterAgent
except ImportError:
    st.error("❌ Could not import MasterAgent. Make sure all agent files are present.")
    st.stop()

# Initialize session state
if 'master_agent' not in st.session_state:
    with st.spinner('Initializing Pharmacy AI Master Agent...'):
        try:
            st.session_state.master_agent = MasterAgent()
            st.session_state.conversation_history = []
            st.session_state.initialized = True
        except Exception as e:
            st.error(f"❌ Error initializing Master Agent: {e}")
            st.stop()

# Header
st.title("🏥 Pharmacy AI - Master Agent")
st.markdown("Your intelligent pharmacy operations consultant")

# Sidebar
with st.sidebar:
    st.header("📊 Dashboard")
    
    # Session info
    st.subheader("Session Info")
    st.write(f"**Agents Loaded:** {len(st.session_state.master_agent.agents)}/10")
    st.write(f"**Questions Asked:** {len(st.session_state.conversation_history)}")
    
    # Available agents
    st.subheader("Available Agents")
    agent_names = {
        'demand': 'Demand Forecasting',
        'transfer': 'Store Transfer',
        'supplier': 'Supplier Intelligence',
        'capital': 'Working Capital',
        'inventory': 'Inventory Optimization',
        'pricing': 'Discount & Pricing',
        'prescription': 'Prescription Intelligence',
        'promotion': 'Promotion Effectiveness',
        'compliance': 'Compliance & Regulation',
        'customer': 'Customer Personalization'
    }
    
    for key, name in agent_names.items():
        if key in st.session_state.master_agent.agents:
            st.success(f"✓ {name}")
        else:
            st.error(f"✗ {name}")
    
    # Actions
    st.subheader("Actions")
    if st.button("🗑️ Clear History"):
        st.session_state.conversation_history = []
        st.session_state.master_agent.clear_history()
        st.success("History cleared!")
        st.rerun()
    
    if st.button("🔄 Reload Agents"):
        st.session_state.master_agent = MasterAgent()
        st.success("Agents reloaded!")
        st.rerun()

# Main interface
st.markdown("---")

# Example questions
with st.expander("💡 Example Questions"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Inventory & Ordering:**")
        st.code("What products are expiring in next 30 days?")
        st.code("Show me dead stock with locked capital")
        st.code("Should I order 1000 Ibuprofen?")
        
        st.markdown("**Pricing & Discounts:**")
        st.code("What discount for Paracetamol?")
        st.code("Simulate 15% discount margin impact")
    
    with col2:
        st.markdown("**Demand & Forecasting:**")
        st.code("Predict demand for MED001 next month")
        st.code("Which products are fast-moving?")
        
        st.markdown("**Suppliers & Budget:**")
        st.code("Which supplier for antibiotics?")
        st.code("Can I afford $25,000 order?")
        st.code("Show supplier reliability scores")

# Question input
st.markdown("### 💬 Ask Your Question")
question = st.text_area(
    "Type your question in natural language:",
    height=100,
    placeholder="Example: What will be demand for Paracetamol next month?"
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    ask_button = st.button("🚀 Ask Master Agent", type="primary")
with col2:
    clear_input = st.button("🗑️ Clear Input")

if clear_input:
    st.rerun()

# Process question
if ask_button and question.strip():
    with st.spinner('🤖 Consulting specialized agents...'):
        try:
            # Get answer from Master Agent
            response = st.session_state.master_agent.ask(question)
            
            # Add to history
            st.session_state.conversation_history.append({
                'timestamp': datetime.now(),
                'question': question,
                'response': response
            })
            
            # Display response
            st.markdown("---")
            st.markdown("### 📊 Comprehensive Answer")
            st.markdown(response)
            
        except Exception as e:
            st.error(f"❌ Error processing question: {e}")
            st.exception(e)

elif ask_button:
    st.warning("⚠️ Please enter a question first")

# Conversation history
if st.session_state.conversation_history:
    st.markdown("---")
    st.markdown("### 📜 Conversation History")
    
    for i, entry in enumerate(reversed(st.session_state.conversation_history), 1):
        with st.expander(f"Q{len(st.session_state.conversation_history) - i + 1}: {entry['question'][:60]}... ({entry['timestamp'].strftime('%H:%M:%S')})"):
            st.markdown(f"**Question:** {entry['question']}")
            st.markdown("**Answer:**")
            st.markdown(entry['response'])

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>Pharmacy AI - Master Agent v1.0 | Powered by FREE Gemini API | $0/month cost</p>
    </div>
    """,
    unsafe_allow_html=True
)
