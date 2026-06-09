import streamlit as st
import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import plotly.graph_objects as go

# --- 1. PAGE CONFIG & UI STYLING ---
st.set_page_config(
    page_title="UC EDS DSS - Official", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE INITIALIZATION (Memory Vault) ---
if 'is_initialized' not in st.session_state:
    st.session_state.history_time = [1, 2, 3, 4, 5]
    st.session_state.history_base = [2000] * 5
    st.session_state.history_opt = [2000] * 5
    st.session_state.time_step = 5
    st.session_state.is_initialized = True

if 'show_admin' not in st.session_state: st.session_state.show_admin = False

# Permanent memory for the main UI inputs
if 'active_pcs' not in st.session_state: st.session_state.active_pcs = 25 
if 'proj_on' not in st.session_state: st.session_state.proj_on = False
if 'in_occ' not in st.session_state: st.session_state.in_occ = 24
if 'in_tmp' not in st.session_state: st.session_state.in_tmp = 34
if 'room_mode' not in st.session_state: st.session_state.room_mode = "Typical Classroom"

# Permanent memory for the override inputs (These survive when UI is hidden)
if 'sim_pc_w' not in st.session_state: st.session_state.sim_pc_w = 150
if 'sim_proj_w' not in st.session_state: st.session_state.sim_proj_w = 300
if 'sim_rate' not in st.session_state: st.session_state.sim_rate = 7.55
if 'sim_light_w' not in st.session_state: st.session_state.sim_light_w = 27
if 'sim_fan_w' not in st.session_state: st.session_state.sim_fan_w = 130
if 'admin_s1' not in st.session_state: st.session_state.admin_s1 = False
if 'admin_s2' not in st.session_state: st.session_state.admin_s2 = False

# --- CALLBACK FUNCTIONS ---
def toggle_admin(): 
    st.session_state.show_admin = not st.session_state.show_admin
    # Sync the toggles to the current automated system recommendation when opening Admin Mode
    if st.session_state.show_admin:
        occ = st.session_state.get('in_occ', 24)
        st.session_state.admin_s1 = occ > 0
        st.session_state.admin_s2 = occ >= 15

def reset_admin_defaults():
    st.session_state.sim_pc_w = 150
    st.session_state.sim_proj_w = 300
    st.session_state.sim_light_w = 27
    st.session_state.sim_fan_w = 130
    st.session_state.sim_rate = 7.55
    
    # Sync toggles to automated defaults during reset
    occ = st.session_state.get('in_occ', 24)
    st.session_state.admin_s1 = occ > 0
    st.session_state.admin_s2 = occ >= 15
    
    # Force the UI widgets to rebuild by clearing their cache keys
    for key in ["ui_sim_pc_w", "ui_sim_proj_w", "ui_sim_light_w", "ui_sim_fan_w", "ui_sim_rate", "ui_admin_s1", "ui_admin_s2"]:
        if key in st.session_state:
            del st.session_state[key]

# --- 2. DYNAMIC HARDWARE CONSTANTS ---
ANNUAL_HOURS = 10 * 264 
STD_W_PC = 150 
STD_W_PROJ = 300
STD_W_S1 = 27
STD_W_S2 = 27
STD_W_FANS = 130
STD_RATE = 7.55

if st.session_state.show_admin:
    W_PC = st.session_state.sim_pc_w
    W_PROJ = st.session_state.sim_proj_w
    ACTIVE_RATE = st.session_state.sim_rate
    W_S1 = st.session_state.sim_light_w
    W_S2 = st.session_state.sim_light_w 
    W_FANS = st.session_state.sim_fan_w
else:
    W_PC = STD_W_PC
    W_PROJ = STD_W_PROJ
    ACTIVE_RATE = STD_RATE
    W_S1 = STD_W_S1
    W_S2 = STD_W_S2
    W_FANS = STD_W_FANS

# --- 3. PREMIUM CSS STYLING ---
st.markdown("""
    <style>
    /* Import Premium SaaS Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, p, div, h1, h2, h3, h4, h5, h6, label, button, input {
        font-family: 'Inter', sans-serif;
    }
    
    span.material-symbols-rounded, 
    span.material-icons, 
    i.material-icons,
    [data-baseweb="icon"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }
    
    .block-container {
        padding-top: 1rem !important; 
        padding-bottom: 1rem !important;
        max-width: 98%;
        transition: border 0.4s ease, box-shadow 0.4s ease;
    }
    header[data-testid="stHeader"] { display: none !important; }
    
    .stApp {
        background: linear-gradient(to bottom right, #1a3a26, #09170e);
        z-index: 1;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(to bottom right, #3a1c1c, #1a0a0a);
        opacity: var(--alert-opacity, 0);
        transition: opacity 1.5s ease-in-out;
        z-index: -1;
        pointer-events: none;
    }
    
    div[data-testid="stMetric"] {
        background-color: var(--metric-bg, rgba(38, 39, 48, 0.6)) !important; 
        border: 1px solid var(--metric-border, #464b5d) !important; 
        border-radius: 8px;
        padding: 10px 15px !important;
        transition: background-color 1.5s ease, border-color 1.5s ease !important;
    }
    
    /* Branding Title Styling */
    .brand-text {
        color: #4ade80;
        font-weight: 800;
        font-size: 1rem;
        letter-spacing: 2px;
        margin-bottom: -5px;
        margin-top: 20px;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin-bottom: 1.5rem;
        margin-top: 0px;
    }

    /* Custom Pill Badges for Recommendations */
    .sys-badge {
        padding: 8px 16px; 
        border-radius: 20px; 
        font-weight: 600; 
        font-size: 0.85em; 
        margin-bottom: 8px; 
        display: block; 
        text-align: left;
        letter-spacing: 0.5px;
    }
    .badge-error { background-color: rgba(255, 75, 75, 0.15); border: 1px solid rgba(255, 75, 75, 0.5); color: #ff6b6b; }
    .badge-warning { background-color: rgba(255, 170, 0, 0.15); border: 1px solid rgba(255, 170, 0, 0.5); color: #ffca28; }
    .badge-success { background-color: rgba(0, 255, 0, 0.15); border: 1px solid rgba(0, 255, 0, 0.5); color: #4ade80; }
    .badge-info { background-color: rgba(0, 150, 255, 0.15); border: 1px solid rgba(0, 150, 255, 0.5); color: #60a5fa; }
    
    /* Lowkey legend badges */
    .legend-badge-mini {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.65rem;
        font-weight: 700;
        display: inline-block;
        border: 1px solid rgba(255,255,255,0.1);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    h3 { margin-bottom: 0rem !important; padding-bottom: 0.2rem !important; }
    h4 { margin-bottom: 0rem !important; padding-bottom: 0.5rem !important; font-weight: 700 !important; letter-spacing: 1px;}
    
    /* --- FONT SIZE CONTROL: OUTSIDE THE BOXES --- */
    p, .stMarkdown p { font-size: 1.5rem !important; }
    label, div[data-testid="stWidgetLabel"] p, .stRadio label p {
        font-size: 1.3rem !important; font-weight: 600 !important; 
    }
    h4 { font-size: 2.0rem !important; }

    /* --- FONT SIZE CONTROL: INSIDE THE METRIC BOXES --- */
    div[data-testid="stMetricValue"] {
        font-size: 2.0rem !important; white-space: nowrap !important;
        overflow: hidden !important; text-overflow: ellipsis !important;
    }
    div[data-testid="stMetricLabel"] p { font-size: 1.0rem !important; font-weight: 400 !important; }
    
    /* --- FIX FOR OVERSIZED DELTA & SLIDERS --- */
    div[data-testid="stMetricDelta"], div[data-testid="stMetricDelta"] p, 
    div[data-testid="stMetricDelta"] span, div[data-testid="stMetricDelta"] div {
        font-size: 0.9rem !important; font-weight: 600 !important;
    }
    div[data-testid="stMetricDelta"] svg { width: 1rem !important; height: 1rem !important; }
    div[data-baseweb="slider"] * { font-size: 0.9rem !important; font-weight: 400 !important; }

    /* --- FIX FOR OVERSIZED BUTTONS --- */
    button p, button div, button span { font-size: 1.0rem !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CACHED FUZZY LOGIC ENGINE ---
@st.cache_resource
def build_fuzzy_engine():
    occ = ctrl.Antecedent(np.arange(0, 41, 1), 'occupancy')
    tmp = ctrl.Antecedent(np.arange(20, 41, 1), 'temp')
    rec = ctrl.Consequent(np.arange(0, 101, 1), 'energy_rec')

    occ.automf(3, names=['low', 'medium', 'high'])
    tmp['cool'] = fuzz.trimf(tmp.universe, [20, 20, 26]) 
    tmp['moderate'] = fuzz.trimf(tmp.universe, [24, 28, 32])
    tmp['hot'] = fuzz.trimf(tmp.universe, [30, 40, 40]) 
    rec.automf(3, names=['low', 'medium', 'high'])

    rule_list = [
        ctrl.Rule(occ['low'] & tmp['cool'], rec['low']),      
        ctrl.Rule(occ['low'] & tmp['moderate'], rec['low']),  
        ctrl.Rule(occ['low'] & tmp['hot'], rec['medium']),    
        ctrl.Rule(occ['medium'] & tmp['cool'], rec['low']),      
        ctrl.Rule(occ['medium'] & tmp['moderate'], rec['medium']), 
        ctrl.Rule(occ['medium'] & tmp['hot'], rec['high']),      
        ctrl.Rule(occ['high'] & tmp['cool'], rec['medium']),     
        ctrl.Rule(occ['high'] & tmp['moderate'], rec['high']),   
        ctrl.Rule(occ['high'] & tmp['hot'], rec['high'])         
    ]
    return ctrl.ControlSystem(rule_list), rec

energy_ctrl, energy_rec = build_fuzzy_engine()
sim = ctrl.ControlSystemSimulation(energy_ctrl)

# --- 5. MAIN SCREEN: LOGO & TITLES ---
try:
    st.image("UC_Official_Logo.png", width=350) 
except FileNotFoundError:
    pass
st.markdown('<p class="brand-text">ECOLOGIC DSS</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Energy Usage Calculator</h1>', unsafe_allow_html=True)

# --- 6. MAIN LAYOUT ---
col_in, col_mid, col_out = st.columns([1, 1.2, 1.6], gap="medium")

# ==========================================
# COLUMN 1: CONFIGURATION & INPUTS
# ==========================================
with col_in:
    st.markdown("#### CONFIGURATION")
    
    room_type = st.radio("Mode:", ["Typical Classroom", "Computer Lab"], horizontal=True, key="room_mode")
    proj_override = st.toggle("Projector Active", key="proj_on")
    in_occ = st.slider("Students", 0, 40, key="in_occ") 
    in_tmp = st.slider("Temp (°C)", 20, 40, key="in_tmp") 

    num_pcs = 0 
    if room_type == "Computer Lab":
        if 'active_pcs' not in st.session_state:
            st.session_state.active_pcs = 25
            
        num_pcs = st.number_input(
            "💻 Active PCs", 
            min_value=0, max_value=30, 
            value=st.session_state.active_pcs, key="ui_active_pcs"
        )
        st.session_state.active_pcs = num_pcs

    st.markdown("<br>", unsafe_allow_html=True) 
    
    # --- ADMIN CONTROLS ---
    if not st.session_state.show_admin:
        st.button("⚙️ Enter Admin Mode", on_click=toggle_admin, use_container_width=True)
    else:
        st.button("❌ Exit Admin Mode", on_click=toggle_admin, use_container_width=True)
        
        with st.popover("🛠️ Admin Controls", use_container_width=True):
            c_head1, c_head2 = st.columns([2, 1])
            c_head1.markdown("**🟢 Admin Override Active**")
            c_head2.button("🔄 Reset", on_click=reset_admin_defaults, use_container_width=True)
            st.markdown("---")
            
            st.markdown("**💡 Light Switch Override**")
            c_s1, c_s2 = st.columns(2)
            st.session_state.admin_s1 = c_s1.toggle("Switch 1 Power", value=st.session_state.admin_s1, key="ui_admin_s1")
            st.session_state.admin_s2 = c_s2.toggle("Switch 2 Power", value=st.session_state.admin_s2, key="ui_admin_s2")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**⚡ Hardware Settings**")
            
            if 'sim_pc_w' not in st.session_state: st.session_state.sim_pc_w = 150
            if 'sim_proj_w' not in st.session_state: st.session_state.sim_proj_w = 300
            if 'sim_light_w' not in st.session_state: st.session_state.sim_light_w = 27
            if 'sim_fan_w' not in st.session_state: st.session_state.sim_fan_w = 130
            if 'sim_rate' not in st.session_state: st.session_state.sim_rate = 7.55

            c_w1, c_w2 = st.columns(2)
            with c_w1:
                if room_type == "Computer Lab" and num_pcs > 0:
                    st.session_state.sim_pc_w = st.slider("PC Wattage", 15, 600, value=st.session_state.sim_pc_w, key="ui_sim_pc_w")
                if proj_override:
                    st.session_state.sim_proj_w = st.slider("Proj Wattage", 50, 800, value=st.session_state.sim_proj_w, key="ui_sim_proj_w")
                st.session_state.sim_rate = st.number_input("Rate (₱/kWh)", 5.0, 30.0, step=0.5, value=st.session_state.sim_rate, key="ui_sim_rate")
            with c_w2:
                st.session_state.sim_light_w = st.slider("Light Wattage", 10, 300, value=st.session_state.sim_light_w, key="ui_sim_light_w")
                st.session_state.sim_fan_w = st.slider("Fan Wattage", 30, 250, value=st.session_state.sim_fan_w, key="ui_sim_fan_w")

# --- SIMULATION CALCULATIONS ---
sim.input['occupancy'] = in_occ
sim.input['temp'] = in_tmp
sim.compute()
out_val = sim.output['energy_rec']

if st.session_state.show_admin:
    s1_on, s2_on = st.session_state.admin_s1, st.session_state.admin_s2
    if s1_on and s2_on: draw_lights, rec_lights = W_S1 + W_S2, "FULL (S1 & S2) [OVERRIDE]"
    elif s1_on: draw_lights, rec_lights = W_S1, "DIM (Switch 1) [OVERRIDE]"
    elif s2_on: draw_lights, rec_lights = W_S2, "DIM (Switch 2) [OVERRIDE]"
    else: draw_lights, rec_lights = 0, "OFF [OVERRIDE]"
else:
    if in_occ == 0: draw_lights, rec_lights = 0, "OFF"
    elif in_occ >= 15: draw_lights, rec_lights = W_S1 + W_S2, "FULL (S1 & S2)"
    else: draw_lights, rec_lights = W_S1, "DIM (Switch 1)"

if in_occ == 0: draw_fans, rec_fans = 0, "LOW/OFF"
elif out_val > 65 or in_tmp >= 27: draw_fans, rec_fans = W_FANS, "HIGH"
elif out_val > 40 or in_tmp >= 24: draw_fans, rec_fans = W_FANS * 0.6, "MEDIUM"
else: draw_fans, rec_fans = 0, "LOW/OFF"

active_w = draw_lights + draw_fans + (W_PROJ if proj_override else 0) + (min(num_pcs, in_occ) * W_PC if room_type == "Computer Lab" else 0)
peak_w = max(1, (W_S1 + W_S2) + W_FANS + (W_PROJ if proj_override else 0) + (num_pcs * W_PC))
monthly_base_php, Energy_draw_php = (peak_w/1000 * 10 * 22 * ACTIVE_RATE), (active_w/1000 * 10 * 22 * ACTIVE_RATE)
savings_php, crr_percentage = max(0, monthly_base_php - Energy_draw_php), ((max(0, monthly_base_php - Energy_draw_php)) / monthly_base_php) * 100
eff_score = max(0.0, (1 - (active_w / peak_w)) * 100)

if in_occ == 0: st.markdown("<style>:root {--alert-opacity: 1; --metric-bg: rgba(60, 25, 25, 0.7); --metric-border: #7a3535;}</style>", unsafe_allow_html=True)
else: st.markdown("<style>:root {--alert-opacity: 0; --metric-bg: rgba(38, 39, 48, 0.6); --metric-border: #464b5d;}</style>", unsafe_allow_html=True)

st.session_state.time_step += 1
st.session_state.history_time.append(st.session_state.time_step)
st.session_state.history_base.append(peak_w)
st.session_state.history_opt.append(active_w)
st.session_state.history_time, st.session_state.history_base, st.session_state.history_opt = st.session_state.history_time[-25:], st.session_state.history_base[-25:], st.session_state.history_opt[-25:]

# ==========================================
# COLUMN 2: CONSUMPTION & ACTIONS
# ==========================================
with col_mid:
    st.markdown("#### CONSUMPTION " + ("<span style='color:#ffca28; font-size:0.8em;'>⚠️ ADMIN</span>" if st.session_state.show_admin else ""), unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Baseline", f"{int(peak_w)}W")
    m2.metric("Optimized", f"{int(active_w)}W")
    m3.metric("Saved", f"{int(peak_w - active_w)}W", delta=f"{int(peak_w - active_w)}W Drop")
    m4, m5, m6 = st.columns(3)
    m4.metric("Current ₱", f"₱{monthly_base_php:,.0f}")
    m5.metric("Optimized ₱", f"₱{Energy_draw_php:,.0f}")
    m6.metric("Saved ₱", f"₱{savings_php:,.0f}", delta=f"₱{savings_php:,.0f} Saved")
    st.markdown("<br>", unsafe_allow_html=True) 
    st.markdown("#### SYSTEM RECOMMENDATIONS")
    def b(text, s): st.markdown(f'<div class="sys-badge {s}">{text}</div>', unsafe_allow_html=True)
    if "[OVERRIDE]" in rec_lights: b(f"💡 LIGHTS: {rec_lights}", "badge-warning") 
    elif rec_lights == "FULL (S1 & S2)": b(f"💡 LIGHTS: {rec_lights}", "badge-error")
    elif "DIM" in rec_lights: b(f"💡 LIGHTS: {rec_lights}", "badge-warning")
    else: b(f"💡 LIGHTS: {rec_lights}", "badge-info")
    if rec_fans == "HIGH": b(f"🌀 FANS: {rec_fans}", "badge-error")
    elif rec_fans == "MEDIUM": b(f"🌀 FANS: {rec_fans}", "badge-warning")
    else: b(f"🌀 FANS: {rec_fans}", "badge-success")
    if proj_override: b("🎥 PROJECTOR: " + ("TURN OFF (Empty)" if in_occ == 0 else "ACTIVE"), "badge-error" if in_occ == 0 else "badge-warning")
    else: b("🎥 PROJECTOR: OFF", "badge-info")
    if room_type == "Computer Lab":
        if in_occ == 0 and num_pcs > 0: b(f"💻 PCs: TURN OFF ALL {num_pcs} (Empty)", "badge-error")
        elif num_pcs > in_occ and in_occ > 0: b(f"💻 PCs: TURN OFF {num_pcs - in_occ} (Need: {in_occ})", "badge-warning")
        elif num_pcs > 0: b(f"💻 PCs: {num_pcs} Active (Optimal)", "badge-success")
        else: b("💻 PCs: 0 Active", "badge-info")

# ==========================================
# COLUMN 3: ANALYTICS & PLOTLY GRAPH
# ==========================================
with col_out:
    st.markdown("#### ANALYTICS " + ("<span style='color:#ffca28; font-size:0.8em;'>⚠️ ADMIN</span>" if st.session_state.show_admin else ""), unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    waste = (in_occ == 0 and (proj_override or num_pcs > 0))
    c1.metric("Efficiency", f"{eff_score:.1f}%", delta="" if waste else None, delta_color="inverse" if waste else "normal")
    c2.metric("CRR", f"{crr_percentage:.1f}%")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.history_time, y=st.session_state.history_base, mode='lines', name='Baseline', line=dict(color='rgba(255, 75, 75, 0.6)', width=2, dash='dot')))
    fig.add_trace(go.Scatter(x=st.session_state.history_time, y=st.session_state.history_opt, mode='lines', name='Optimized', line=dict(color='#00FF00', width=3, shape='spline', smoothing=0.3), fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.1)'))
    fig.update_layout(height=300, margin=dict(l=0, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(showticklabels=False, showgrid=False, zeroline=False), yaxis=dict(gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#aaaaaa'), zerolinecolor='rgba(255,255,255,0.1)'))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- 7. MINIMAL LOWKEY LEGEND ---
st.markdown("<div style='text-align: center; opacity: 0.6; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;'> \
    <span class='legend-badge-mini' style='color: #ff6b6b;'>🔴 Critical/Waste</span> &nbsp;&nbsp; \
    <span class='legend-badge-mini' style='color: #ffca28;'>🟡 Caution/Override</span> &nbsp;&nbsp; \
    <span class='legend-badge-mini' style='color: #4ade80;'>🟢 Optimal</span> &nbsp;&nbsp; \
    <span class='legend-badge-mini' style='color: #60a5fa;'>🔵 Standby</span> \
    </div>", unsafe_allow_html=True)
