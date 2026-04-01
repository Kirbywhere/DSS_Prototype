import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# --- 1. PAGE CONFIG & UI STYLING ---
st.set_page_config(page_title="UC EDS DSS - Integrated Logic", layout="wide")

st.markdown("""
    <style>
    .main { padding-top: 0rem; }
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    /* Metrics */
    div[data-testid="stMetric"] {
        background-color: #262730; 
        border: 1px solid #464b5d; 
        border-radius: 10px; 
        padding: 8px !important;
    }
    [data-testid="stMetricValue"] { color: #00ffcc !important; font-size: 32px !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 16px !important; }
    
    /* Insight Box */
    .insight-box {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #333;
        font-size: 17px; 
        line-height: 1.4;
    }
    .override-alert {
        background-color: #3e2723;
        border-left: 5px solid #ff9800;
        padding: 10px;
        font-size: 14px;
        color: #ffd9a3;
        margin-bottom: 10px;
    }
    
    /* Professional Headers */
    h3 { font-size: 24px !important; margin-bottom: 8px !important; margin-top: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZE SESSION STATE ---
if 'pc_count' not in st.session_state: 
    st.session_state.pc_count = 20

# --- 3. SIDEBAR LOGIC GRAPH ---
with st.sidebar:
    st.header("⚙️ Inference Engine")
    show_graph = st.checkbox("🔍 VIEW LOGIC GRAPH", value=False)
    graph_container = st.empty()
    st.divider()
    st.info("PROTOTYPE uWu")

# --- 4. MAIN SCREEN: 3-SECTION LAYOUT ---
st.title("🐆 EDS Decision-Support System")
col_in, col_mid, col_out = st.columns([1, 1.1, 1.1], gap="medium")

with col_in:
    st.subheader("🏢 Configuration")
    room_type = st.radio("Mode:", ["Typical Classroom", "Computer Lab"], horizontal=True)
    
    # Projector toggle moved up for accessibility
    proj_override = st.toggle("Projector Active", value=False)
    
    st.write("---") 

    in_occ = st.slider("Students", 0, 40, 24) 
    in_tmp = st.slider("Temp (°C)", 20, 40, 34) 

    num_pcs = 0 
    if room_type == "Computer Lab":
        st.write("💻 **PCs**")
        c1, c2, c3 = st.columns([1,1.5,1])
        if c1.button("➖"): st.session_state.pc_count = max(0, st.session_state.pc_count - 1)
        if c3.button("➕"): st.session_state.pc_count = min(30, st.session_state.pc_count + 1)
        c2.markdown(f"<center><h3>{st.session_state.pc_count}</h3></center>", unsafe_allow_html=True)
        num_pcs = st.session_state.pc_count

# --- 5. FUZZY LOGIC CALCULATIONS (Streamlined 9-Rule Engine) ---
occupancy = ctrl.Antecedent(np.arange(0, 41, 1), 'occupancy')
temp = ctrl.Antecedent(np.arange(20, 41, 1), 'temp')
energy_rec = ctrl.Consequent(np.arange(0, 101, 1), 'energy_rec')

occupancy.automf(3, names=['low', 'medium', 'high'])
temp['cool'] = fuzz.trimf(temp.universe, [20, 20, 26]) 
temp['moderate'] = fuzz.trimf(temp.universe, [24, 28, 32])
temp['hot'] = fuzz.trimf(temp.universe, [30, 40, 40]) 
energy_rec.automf(3, names=['low', 'medium', 'high'])

# Updated Deterministic Rules
rules = [
    # LOW OCCUPANCY
    ctrl.Rule(occupancy['low'] & temp['cool'], energy_rec['low']),      
    ctrl.Rule(occupancy['low'] & temp['moderate'], energy_rec['low']),  
    ctrl.Rule(occupancy['low'] & temp['hot'], energy_rec['medium']),    

    # MEDIUM OCCUPANCY
    ctrl.Rule(occupancy['medium'] & temp['cool'], energy_rec['low']),      
    ctrl.Rule(occupancy['medium'] & temp['moderate'], energy_rec['medium']), 
    ctrl.Rule(occupancy['medium'] & temp['hot'], energy_rec['high']),      

    # HIGH OCCUPANCY
    ctrl.Rule(occupancy['high'] & temp['cool'], energy_rec['medium']),     
    ctrl.Rule(occupancy['high'] & temp['moderate'], energy_rec['high']),   
    ctrl.Rule(occupancy['high'] & temp['hot'], energy_rec['high'])         
]

energy_ctrl = ctrl.ControlSystem(rules)
sim = ctrl.ControlSystemSimulation(energy_ctrl)

sim.input['occupancy'], sim.input['temp'] = in_occ, in_tmp
sim.compute()
out_val = sim.output['energy_rec']

# --- 6. SYNCHRONIZED WATTAGE MATH ---
W_S1, W_S2, W_FANS, W_PROJ, W_PC = 27, 27, 130, 300, 150 

# Zero-Occupancy overrides & String mapping
if in_occ == 0:
    draw_lights = 0
    draw_fans = 0
    rec_lights = "OFF"
    rec_fans = "OFF"
else:
    if in_occ > 20 or out_val > 70: 
        draw_lights = W_S1 + W_S2
        rec_lights = "FULL (S1 & S2)"
    elif in_occ > 0 or out_val > 35: 
        draw_lights = W_S1
        rec_lights = "DIM (Switch 1)"
    else: 
        draw_lights = 0
        rec_lights = "OFF"

    if out_val > 65 or in_tmp >= 27: 
        draw_fans = W_FANS
        rec_fans = "HIGH"
    elif out_val > 40 or in_tmp >= 24: 
        draw_fans = W_FANS * 0.6
        rec_fans = "MEDIUM"
    else: 
        draw_fans = 0
        rec_fans = "LOW/OFF"
        
calc_pc_load = num_pcs * W_PC
active_w = draw_lights + draw_fans + (W_PROJ if proj_override else 0) + calc_pc_load
peak_w = (W_S1 + W_S2) + W_FANS + W_PROJ + calc_pc_load 
if peak_w == 0: peak_w = 1

# --- 7. EFFICIENCY & PERFORMANCE LOGIC ---
monthly_base_php = (peak_w/1000 * 10 * 22 * 7.55)
current_draw_php = (active_w/1000 * 10 * 22 * 7.55)
savings_php = max(0, monthly_base_php - current_draw_php)
crr_percentage = (savings_php / monthly_base_php) * 100

if in_occ == 0:
    if active_w > 0:
        eff_score = max(0, (1 - (active_w / peak_w)) * 100)
    else:
        eff_score = 100.0
else:
    eff_score = 100 - out_val

# Sidebar Graph Rendering
if show_graph:
    with graph_container:
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('#0E1117'); ax.set_facecolor('#262730')
        ax.tick_params(colors='white', labelsize=9)
        energy_rec.view(sim=sim)
        st.pyplot(plt.gcf(), use_container_width=True)

# --- 8. OUTPUTS ---
with col_mid:
    st.subheader("⚡ Consumption")
    m1, m2 = st.columns(2)
    m1.metric("Current Draw", f"{int(active_w)}W")
    m2.metric("Monthly Savings", f"₱{savings_php:,.0f}")
    
    st.markdown("### ✅ Recommended Actions")
    
    if rec_lights == "FULL (S1 & S2)": st.error(f"💡 LIGHTS: {rec_lights}")
    elif rec_lights == "DIM (Switch 1)": st.warning(f"💡 LIGHTS: {rec_lights}")
    else: st.info(f"💡 LIGHTS: {rec_lights}")

    if rec_fans == "HIGH": st.error(f"🌀 FANS: {rec_fans}")
    elif rec_fans == "MEDIUM": st.warning(f"🌀 FANS: {rec_fans}")
    else: st.success(f"🌀 FANS: {rec_fans}")
    
    if proj_override: 
        if in_occ == 0:
            st.error("🎥 PROJECTOR: LEFT ON (WASTE DETECTED)")
        else:
            st.error("🎥 PROJECTOR: ACTIVE")
            
    if room_type == "Computer Lab" and in_occ == 0 and num_pcs > 0:
        st.error(f"💻 PCs: {num_pcs} UNITS RUNNING (WASTE DETECTED)")
    elif room_type == "Computer Lab" and num_pcs > in_occ and in_occ > 0:
        st.warning(f"💻 PCs: {num_pcs} Active (Only {in_occ} needed)")

with col_out:
    st.subheader("📊 Analytics")
    c1, c2 = st.columns(2)
    
    eff_delta_color = "normal"
    eff_delta = None
    if in_occ == 0 and active_w > 0:
        eff_delta = "-WASTE"
        eff_delta_color = "inverse"
        
    c1.metric("Efficiency", f"{eff_score:.1f}%", delta=eff_delta, delta_color=eff_delta_color)
    c2.metric("CRR", f"{crr_percentage:.1f}%", help="Cost Reduction Ratio: Money saved vs. max potential cost.")
    
    if in_occ == 0:
        mode = "Vacant"
        desc = "Room is empty. Systems forced to standby."
        if proj_override:
            st.markdown("""<div class="override-alert">⚠️ <b>Waste Alert:</b> Projector is running in an empty room!</div>""", unsafe_allow_html=True)
        if room_type == "Computer Lab" and num_pcs > 0:
             st.markdown(f"""<div class="override-alert">⚠️ <b>Waste Alert:</b> {num_pcs} PCs are running in an empty lab!</div>""", unsafe_allow_html=True)
    elif out_val < 35:
        mode, desc = "Conservation", f"Low thermal load ({in_tmp}°C) detected."
    elif out_val < 70:
        mode, desc = "Balanced", f"Moderate demand ({in_occ} users) detected."
    else:
        mode, desc = "Performance", f"High thermal load ({in_tmp}°C) detected."

    if room_type == "Computer Lab" and in_occ > 0 and num_pcs > in_occ:
        excess = num_pcs - in_occ
        st.markdown(f"""<div class="override-alert">⚠️ <b>Efficiency Alert:</b> {excess} extra PCs are running! Only {in_occ} needed.</div>""", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="insight-box">
            <b>Status:</b> {mode} Mode<br>
            {desc} Optimized draw is <b>{int(active_w)}W</b>.
        </div>
        """, unsafe_allow_html=True)

    # --- 3. DETAILED EXECUTIVE SUMMARY ---
    st.markdown("### 📋 Executive Summary")
    
    # Calculate Load Factor
    load_factor = (active_w / peak_w) * 100
    
    # --- DYNAMIC SCENARIO LOGIC ---
    if in_occ == 0 and active_w > 0:
        # SCENARIO A: WASTE (Vacant but power draw detected)
        theme = "error" # Triggers a red box
        icon = "🚨"
        status_title = "CRITICAL: Energy Waste Detected"
        detail = f"Room is completely empty, but drawing **{int(active_w)}W**. Active manual overrides are nullifying automation savings."
        action = "Turn off the active Projector and/or idle PCs immediately."
        crr_explanation = "Effective savings are compromised. Money is being spent on an empty room."

    elif load_factor > 80:
        # SCENARIO B: CRITICAL LOAD (High Occupancy/Heat)
        theme = "warning" # Triggers a yellow box
        icon = "🔥"
        status_title = "PEAK LOAD: High Demand Operation"
        detail = f"System is operating near maximum capacity (**{load_factor:.1f}%**) to safely accommodate {in_occ} users at {in_tmp}°C."
        action = "Monitor ambient temperature. If it drops, the system will automatically throttle down fans to recover savings."
        crr_explanation = f"CRR is naturally low ({crr_percentage:.0f}%) to prioritize human comfort and safety over cost."

    elif load_factor > 40:
        # SCENARIO C: BALANCED OPERATION
        theme = "info" # Triggers a blue box
        icon = "⚖️"
        status_title = "BALANCED: Comfort & Cost Optimized"
        detail = f"Fuzzy logic has successfully stabilized the room at a **{load_factor:.1f}%** load factor."
        action = "No action required. System is running at ideal efficiency for current conditions."
        crr_explanation = f"CRR is stable ({crr_percentage:.0f}%). The system is perfectly balancing thermal load and energy cost."

    else:
        # SCENARIO D: MAX SAVINGS (Low Occupancy/Cool)
        theme = "success" # Triggers a green box
        icon = "✅"
        status_title = "OPTIMIZED: Maximum Savings Active"
        detail = f"Low thermal demand allow the system to run at just **{load_factor:.1f}%** of peak power."
        action = "No action required. The system is maximizing your energy reduction."
        crr_explanation = f"CRR is excellent ({crr_percentage:.0f}%). The inference engine is successfully throttling unnecessary equipment."

    # --- RENDER THE ENHANCED SUMMARY ---
    summary_text = f"""
    **{icon} {status_title}**
    
    * **Current State:** {detail}
    * **Financial Impact:** {crr_explanation}
    * **Recommended Action:** {action}
    """
    
    # Dynamically render the correct Streamlit call based on the theme
    if theme == "error":
        st.error(summary_text)
    elif theme == "warning":
        st.warning(summary_text)
    elif theme == "success":
        st.success(summary_text)
    else:
        st.info(summary_text)