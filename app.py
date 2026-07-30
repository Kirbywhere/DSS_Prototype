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

# --- 2. MASTER STATE INITIALIZATION ---
DEFAULT_STATE = {
    'is_initialized': True,
    'show_admin': False,
    'history_time': [1, 2, 3, 4, 5],
    'history_base': [2000] * 5,
    'history_opt': [2000] * 5,
    'time_step': 5,
    'active_pcs': 25,
    'proj_on': False,
    'in_occ': 24,
    'in_tmp': 34,
    'in_hours': 6.0,  # Added state for custom operating hours
    'room_mode': "Typical Classroom",
    'sim_pc_w': 150,
    'sim_proj_w': 300,
    'sim_rate': 7.55,
    'sim_light_w': 27,
    'sim_fan_w': 130, 
    'admin_s1': False,
    'admin_s2': False,
    'admin_f1': "Mode 3",
    'admin_f2': "Mode 3"
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# --- 3. HARDWARE CONSTANTS & ACTIVE OVERRIDES ---
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
    W_FANS_TOTAL = st.session_state.sim_fan_w
else:
    W_PC = STD_W_PC
    W_PROJ = STD_W_PROJ
    ACTIVE_RATE = STD_RATE
    W_S1 = STD_W_S1
    W_S2 = STD_W_S2
    W_FANS_TOTAL = STD_W_FANS

W_SINGLE_FAN = W_FANS_TOTAL / 2

# --- 4. CALLBACK FUNCTIONS ---
def get_auto_fan_mode(occ, tmp, fuzzy_out):
    if occ == 0:
        return "OFF"
    elif fuzzy_out > 65 or tmp >= 27:
        return "Mode 3"
    elif fuzzy_out > 40 or tmp >= 24:
        return "Mode 2"
    else:
        return "Mode 1"

def toggle_admin(): 
    st.session_state.show_admin = not st.session_state.show_admin
    
    if st.session_state.show_admin:
        occ = st.session_state.in_occ
        tmp = st.session_state.in_tmp
        
        energy_ctrl, _ = build_fuzzy_engine()
        sim_temp = ctrl.ControlSystemSimulation(energy_ctrl)
        sim_temp.input['occupancy'] = occ
        sim_temp.input['temp'] = tmp
        sim_temp.compute()
        out_val = sim_temp.output['energy_rec']
        
        st.session_state.admin_s1 = occ > 0
        st.session_state.admin_s2 = occ >= 15
        
        auto_mode = get_auto_fan_mode(occ, tmp, out_val)
        st.session_state.admin_f1 = auto_mode
        st.session_state.admin_f2 = auto_mode

def reset_admin_defaults():
    override_keys = ['sim_pc_w', 'sim_proj_w', 'sim_light_w', 'sim_fan_w', 'sim_rate']
    for key in override_keys:
        st.session_state[key] = DEFAULT_STATE[key]
        ui_key = f"ui_{key}"
        st.session_state[ui_key] = DEFAULT_STATE[key]
    
    occ = st.session_state.in_occ
    tmp = st.session_state.in_tmp
    
    energy_ctrl, _ = build_fuzzy_engine()
    sim_temp = ctrl.ControlSystemSimulation(energy_ctrl)
    sim_temp.input['occupancy'] = occ
    sim_temp.input['temp'] = tmp
    sim_temp.compute()
    out_val = sim_temp.output['energy_rec']
    
    st.session_state.admin_s1 = occ > 0
    st.session_state.admin_s2 = occ >= 15
    
    auto_mode = get_auto_fan_mode(occ, tmp, out_val)
    st.session_state.admin_f1 = auto_mode
    st.session_state.admin_f2 = auto_mode

def click_toggle_s1():
    st.session_state.admin_s1 = not st.session_state.admin_s1

def click_toggle_s2():
    st.session_state.admin_s2 = not st.session_state.admin_s2

def click_cycle_f1():
    modes = ["OFF", "Mode 1", "Mode 2", "Mode 3"]
    curr = st.session_state.admin_f1
    next_idx = (modes.index(curr) + 1) % 4 if curr in modes else 0
    st.session_state.admin_f1 = modes[next_idx]

def click_cycle_f2():
    modes = ["OFF", "Mode 1", "Mode 2", "Mode 3"]
    curr = st.session_state.admin_f2
    next_idx = (modes.index(curr) + 1) % 4 if curr in modes else 0
    st.session_state.admin_f2 = modes[next_idx]

# --- 5. PREMIUM CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    html, body, p, div, h1, h2, h3, h4, h5, h6, label, button, input {
        font-family: 'Inter', sans-serif;
    }
    
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    }
    
    .block-container {
        padding-top: 1rem !important; 
        padding-bottom: 1rem !important;
        max-width: 98%;
        transition: border 0.4s ease, box-shadow 0.4s ease;
    }
    header[data-testid="stHeader"] { 
        display: none !important; 
    }
    
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

    div[data-testid="stPopoverBody"] {
        width: 1100px !important; 
        max-width: 95vw !important;
        background-color: #1a1b21 !important;
        border: 1px solid #464b5d !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.7) !important;
    }

    div[data-testid="element-container"]:has(.btn-light) + div[data-testid="element-container"] button {
        border-radius: 50% 50% 25% 25% !important; 
        height: 100px !important;
        width: 100% !important;
        max-width: 100px !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="element-container"]:has(.btn-fan) + div[data-testid="element-container"] button {
        border-radius: 50% !important; 
        height: 100px !important;
        width: 100% !important;
        max-width: 100px !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }

    div[data-testid="element-container"]:has(.btn-light) + div button:has(p:contains("ON")) {
        background: rgba(255, 202, 40, 0.15) !important;
        border: 2px solid rgba(255, 202, 40, 0.6) !important;
        box-shadow: 0 0 10px rgba(255, 202, 40, 0.2) !important;
        color: #ffca28 !important;
    }
    
    div[data-testid="element-container"]:has(.btn-fan) + div button:has(p:contains("MODE 1")) {
        background: rgba(74, 222, 128, 0.15) !important;
        border: 2px solid rgba(74, 222, 128, 0.6) !important;
        box-shadow: 0 0 10px rgba(74, 222, 128, 0.2) !important;
        color: #4ade80 !important;
    }

    div[data-testid="element-container"]:has(.btn-fan) + div button:has(p:contains("MODE 2")) {
        background: rgba(255, 202, 40, 0.15) !important;
        border: 2px solid rgba(255, 202, 40, 0.6) !important;
        box-shadow: 0 0 10px rgba(255, 202, 40, 0.2) !important;
        color: #ffca28 !important;
    }

    div[data-testid="element-container"]:has(.btn-fan) + div button:has(p:contains("MODE 3")) {
        background: rgba(255, 107, 107, 0.15) !important;
        border: 2px solid rgba(255, 107, 107, 0.6) !important;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.2) !important;
        color: #ff6b6b !important;
    }

    div[data-testid="element-container"]:has(.btn-light) + div button:has(p:contains("OFF")),
    div[data-testid="element-container"]:has(.btn-fan) + div button:has(p:contains("OFF")) {
        background: rgba(38,39,48,0.8) !important;
        border: 2px solid #464b5d !important;
        color: #888888 !important;
        box-shadow: none !important;
    }
    
    div[data-testid="element-container"]:has(.btn-light) + div button p,
    div[data-testid="element-container"]:has(.btn-fan) + div button p {
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }

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
    
    .legend-badge-mini {
        padding: 4px 10px;
        border-radius: 10px;
        font-size: 0.70rem;
        font-weight: 600;
        display: inline-block;
        border: 1px solid rgba(255,255,255,0.1);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .brand-text { color: #4ade80 !important; font-weight: 800; font-size: 1rem; letter-spacing: 2px; margin-bottom: -5px; margin-top: 20px; }
    
    h3 { margin-bottom: 0rem !important; padding-bottom: 0.2rem !important; }
    h4 { margin-bottom: 0rem !important; padding-bottom: 0.5rem !important; font-weight: 700 !important; letter-spacing: 1px;}
    
    p, .stMarkdown p { font-size: 1.5rem !important; }
    label, div[data-testid="stWidgetLabel"] p, .stRadio label p {
        font-size: 1.2rem !important; font-weight: 600 !important; 
    }
    h4 { font-size: 2.0rem !important; }
    div[data-testid="stMetricValue"] {
        font-size: 2.0rem !important; white-space: nowrap !important;
        overflow: hidden !important; text-overflow: ellipsis !important;
    }
    div[data-testid="stMetricLabel"] p { font-size: 1.0rem !important; font-weight: 400 !important; }
    div[data-testid="stMetricDelta"] p { font-size: 0.9rem !important; font-weight: 600 !important; }
    div[data-baseweb="slider"] * { font-size: 0.9rem !important; font-weight: 400 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. CACHED FUZZY LOGIC ENGINE ---
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

# --- 7. MAIN SCREEN: LOGO & TITLES ---
try:
    st.image("UC_Official_Logo.png", width=350) 
except FileNotFoundError:
    pass

st.markdown('<p class="brand-text">ECOLOGIC DSS</p>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Energy Usage Calculator</h1>', unsafe_allow_html=True)

# --- 8. MAIN LAYOUT ---
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
    
    # NEW: Hours input replacing the hardcoded 220 hours
    in_hours = st.number_input("Operating Hours", min_value=1.0, max_value=720.0, step=0.5, key="in_hours")

    num_pcs = 0 
    if room_type == "Computer Lab":
        num_pcs = st.number_input(
            ":material/computer: Active PCs", 
            min_value=0, 
            max_value=50, 
            value=st.session_state.active_pcs, 
            key="ui_active_pcs"
        )
        st.session_state.active_pcs = num_pcs

    st.markdown("<br>", unsafe_allow_html=True) 
    
    # --- ADMIN CONTROLS ---
    if not st.session_state.show_admin:
        st.button(":material/lock: Enter Admin Mode", on_click=toggle_admin, use_container_width=True)
    else:
        st.button(":material/logout: Exit Admin Mode", on_click=toggle_admin, use_container_width=True)
        
        with st.popover(":material/settings: Admin Controls", use_container_width=True):
            
            with st.container(border=True):
                
                c_head1, c_head2 = st.columns([4, 1])
                c_head1.markdown("### :material/verified_user: Admin Mode")
                c_head2.button(":material/refresh: Reset", on_click=reset_admin_defaults, use_container_width=True)
                
                st.divider()
                
                pop_left, pop_mid, pop_right = st.columns(3)
                
                with pop_left:
                    with st.container(border=True):
                        st.markdown("##### :material/lightbulb: Light Switches")
                        
                        c_s1, c_s2 = st.columns(2)
                        with c_s1:
                            st.markdown("<div style='text-align: center; font-size:0.9em; font-weight:600; color:#ccc; margin-bottom:8px;'>Switch 1</div>", unsafe_allow_html=True)
                            st.markdown('<div class="btn-light"></div>', unsafe_allow_html=True)
                            l1_label = "ON" if st.session_state.admin_s1 else "OFF"
                            st.button(l1_label, on_click=click_toggle_s1, use_container_width=True, key="btn_s1")
                            
                        with c_s2:
                            st.markdown("<div style='text-align: center; font-size:0.9em; font-weight:600; color:#ccc; margin-bottom:8px;'>Switch 2</div>", unsafe_allow_html=True)
                            st.markdown('<div class="btn-light"></div>', unsafe_allow_html=True)
                            l2_label = "ON" if st.session_state.admin_s2 else "OFF"
                            st.button(l2_label, on_click=click_toggle_s2, use_container_width=True, key="btn_s2")
                    
                    with st.container(border=True):
                        st.markdown("##### :material/air: Fan Controls")
                        
                        c_f1, c_f2 = st.columns(2)
                        with c_f1:
                            st.markdown("<div style='text-align: center; font-size:0.9em; font-weight:600; color:#ccc; margin-bottom:8px;'>Fan 1</div>", unsafe_allow_html=True)
                            st.markdown('<div class="btn-fan"></div>', unsafe_allow_html=True)
                            f1_state = st.session_state.admin_f1
                            f1_label = f"{f1_state.upper()}" if f1_state != "OFF" else "OFF"
                            st.button(f1_label, on_click=click_cycle_f1, use_container_width=True, key="btn_f1")
                            
                        with c_f2:
                            st.markdown("<div style='text-align: center; font-size:0.9em; font-weight:600; color:#ccc; margin-bottom:8px;'>Fan 2</div>", unsafe_allow_html=True)
                            st.markdown('<div class="btn-fan"></div>', unsafe_allow_html=True)
                            f2_state = st.session_state.admin_f2
                            f2_label = f"{f2_state.upper()}" if f2_state != "OFF" else "OFF"
                            st.button(f2_label, on_click=click_cycle_f2, use_container_width=True, key="btn_f2")

                with pop_mid:
                    with st.container(border=True):
                        st.markdown("##### :material/bolt: Base Power")
                        
                        st.session_state.sim_light_w = st.number_input(
                            "Light Switch (Watts)", 
                            min_value=10, max_value=1000, step=5,
                            value=st.session_state.sim_light_w, 
                            key="ui_sim_light_w"
                        )
                        st.session_state.sim_fan_w = st.number_input(
                            "Fan Total (Watts)", 
                            min_value=30, max_value=2000, step=10,
                            value=st.session_state.sim_fan_w, 
                            key="ui_sim_fan_w"
                        )
                        
                    with st.container(border=True):
                        st.markdown("##### :material/payments: Utility Cost")
                        st.session_state.sim_rate = st.number_input(
                            "Rate (₱/kWh)", 
                            min_value=1.0, max_value=50.0, step=0.5, 
                            value=st.session_state.sim_rate, 
                            key="ui_sim_rate"
                        )
                    
                with pop_right:
                    with st.container(border=True):
                        st.markdown("##### :material/computer: Device Power")
                        
                        if room_type == "Typical Classroom" and not proj_override:
                            st.info("No active devices in this room.")
                        else:
                            if room_type == "Computer Lab" and num_pcs > 0:
                                st.session_state.sim_pc_w = st.number_input(
                                    "PC Wattage", 
                                    min_value=15, max_value=1500, step=10,
                                    value=st.session_state.sim_pc_w, 
                                    key="ui_sim_pc_w"
                                )
                            if proj_override:
                                st.session_state.sim_proj_w = st.number_input(
                                    "Proj Wattage", 
                                    min_value=50, max_value=2000, step=10,
                                    value=st.session_state.sim_proj_w, 
                                    key="ui_sim_proj_w"
                                )

# --- 9. SIMULATION CALCULATIONS ---
sim.input['occupancy'] = in_occ
sim.input['temp'] = in_tmp
sim.compute()
out_val = sim.output['energy_rec']

if st.session_state.show_admin:
    s1_on = st.session_state.admin_s1
    s2_on = st.session_state.admin_s2
    rec_suffix = " [OVERRIDE]"
else:
    s1_on = in_occ > 0
    s2_on = in_occ >= 15
    rec_suffix = ""

if s1_on and s2_on:
    draw_lights = W_S1 + W_S2
    rec_lights = f"FULL (S1 & S2){rec_suffix}"
elif s1_on:
    draw_lights = W_S1
    rec_lights = f"DIM (Switch 1){rec_suffix}"
elif s2_on:
    draw_lights = W_S2
    rec_lights = f"DIM (Switch 2){rec_suffix}"
else:
    draw_lights = 0
    rec_lights = f"OFF{rec_suffix}"

def calculate_fan_wattage(mode, max_wattage_per_fan):
    if mode == "Mode 3": return max_wattage_per_fan * 1.0
    if mode == "Mode 2": return max_wattage_per_fan * 0.7
    if mode == "Mode 1": return max_wattage_per_fan * 0.4
    return 0

if st.session_state.show_admin:
    f1_mode = st.session_state.admin_f1
    f2_mode = st.session_state.admin_f2
    rec_fans_badge = f"F1: {f1_mode} | F2: {f2_mode} [OVERRIDE]"
else:
    auto_mode = get_auto_fan_mode(in_occ, in_tmp, out_val)
    f1_mode = auto_mode
    f2_mode = auto_mode
    if auto_mode == "Mode 3": rec_fans_badge = "HIGH"
    elif auto_mode == "Mode 2": rec_fans_badge = "MEDIUM"
    elif auto_mode == "Mode 1": rec_fans_badge = "LOW"
    else: rec_fans_badge = "LOW/OFF"

draw_fans = calculate_fan_wattage(f1_mode, W_SINGLE_FAN) + calculate_fan_wattage(f2_mode, W_SINGLE_FAN)

opt_proj_w = W_PROJ if proj_override else 0
opt_pc_count = min(num_pcs, in_occ) if room_type == "Computer Lab" else 0
opt_pc_load = opt_pc_count * W_PC

active_w = draw_lights + draw_fans + opt_proj_w + opt_pc_load
peak_w = max(1, (W_S1 + W_S2) + W_FANS_TOTAL + (W_PROJ if proj_override else 0) + (num_pcs * W_PC))

# NEW: Calculations dynamically using the in_hours parameter
monthly_base_php = (peak_w / 1000 * in_hours * ACTIVE_RATE)
Energy_draw_php = (active_w / 1000 * in_hours * ACTIVE_RATE)
savings_php = max(0, monthly_base_php - Energy_draw_php)
crr_percentage = (savings_php / monthly_base_php) * 100 if monthly_base_php > 0 else 0
eff_score = max(0.0, (1 - (active_w / peak_w)) * 100)

if in_occ == 0: 
    st.markdown("""
        <style>
        :root { --alert-opacity: 1; --metric-bg: rgba(60, 25, 25, 0.7); --metric-border: #7a3535; }
        </style>
    """, unsafe_allow_html=True)
else: 
    st.markdown("""
        <style>
        :root { --alert-opacity: 0; --metric-bg: rgba(38, 39, 48, 0.6); --metric-border: #464b5d; }
        </style>
    """, unsafe_allow_html=True)

st.session_state.time_step += 1
st.session_state.history_time.append(st.session_state.time_step)
st.session_state.history_base.append(peak_w)
st.session_state.history_opt.append(active_w)

st.session_state.history_time = st.session_state.history_time[-25:]
st.session_state.history_base = st.session_state.history_base[-25:]
st.session_state.history_opt = st.session_state.history_opt[-25:]

# ==========================================
# COLUMN 2: CONSUMPTION & ACTIONS
# ==========================================
with col_mid:
    admin_tag = "<span style='color:#ffca28; font-size:0.8em;'><span class='material-symbols-rounded' style='font-size:1em; vertical-align:middle;'>shield</span> OVERRIDE</span>" if st.session_state.show_admin else ""
    st.markdown(f"#### CONSUMPTION {admin_tag}", unsafe_allow_html=True)
        
    watt_savings = int(peak_w - active_w)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Baseline", f"{int(peak_w)}W")
    m2.metric("Optimized", f"{int(active_w)}W")
    m3.metric("Saved", f"{watt_savings}W", delta=f"{watt_savings}W Drop", delta_color="normal")
    
    m4, m5, m6 = st.columns(3)
    # NEW: Updated formatting to accommodate precise smaller hourly rates
    m4.metric("Unoptimized ₱", f"₱{monthly_base_php:,.2f}")
    m5.metric("Optimized ₱", f"₱{Energy_draw_php:,.2f}")
    m6.metric("Saved ₱", f"₱{savings_php:,.2f}", delta=f"₱{savings_php:,.2f} Saved", delta_color="normal")
    
    st.markdown("<br>", unsafe_allow_html=True) 
    st.markdown("#### SYSTEM RECOMMENDATIONS")
    
    def badge(icon_name, text, style_class): 
        st.markdown(f'<div class="sys-badge {style_class}"><span class="material-symbols-rounded" style="font-size: 1.1em; vertical-align: bottom; margin-right: 6px;">{icon_name}</span><span>{text}</span></div>', unsafe_allow_html=True)
        
    if "[OVERRIDE]" in rec_lights: 
        badge("lightbulb", f"LIGHTS: {rec_lights}", "badge-warning") 
    elif "FULL" in rec_lights: 
        badge("lightbulb", f"LIGHTS: {rec_lights}", "badge-error")
    elif "DIM" in rec_lights: 
        badge("lightbulb", f"LIGHTS: {rec_lights}", "badge-warning")
    else: 
        badge("lightbulb", f"LIGHTS: {rec_lights}", "badge-info")
        
    if "[OVERRIDE]" in rec_fans_badge:
        badge("mode_fan", f"FANS: {rec_fans_badge}", "badge-warning")
    elif "HIGH" in rec_fans_badge: 
        badge("mode_fan", f"FANS: {rec_fans_badge}", "badge-error")
    elif "MEDIUM" in rec_fans_badge: 
        badge("mode_fan", f"FANS: {rec_fans_badge}", "badge-warning")
    elif "LOW" in rec_fans_badge and "OFF" not in rec_fans_badge:
        badge("mode_fan", f"FANS: {rec_fans_badge}", "badge-success")
    else: 
        badge("mode_fan", f"FANS: {rec_fans_badge}", "badge-info")
        
    if proj_override: 
        if in_occ == 0:
            badge("videocam", "PROJECTOR: TURN OFF (Empty)", "badge-error")
        else:
            badge("videocam", "PROJECTOR: ACTIVE", "badge-warning")
    else: 
        badge("videocam", "PROJECTOR: OFF", "badge-info")
        
    if room_type == "Computer Lab":
        if in_occ == 0 and num_pcs > 0: 
            badge("computer", f"PCs: TURN OFF ALL {num_pcs} (Empty)", "badge-error")
        elif num_pcs > in_occ and in_occ > 0: 
            badge("computer", f"PCs: TURN OFF {num_pcs - in_occ} (Needed: {in_occ})", "badge-warning")
        elif num_pcs > 0: 
            badge("computer", f"PCs: {num_pcs} Active (Optimal)", "badge-success")
        else: 
            badge("computer", "PCs: 0 Active", "badge-info")

# ==========================================
# COLUMN 3: ANALYTICS & PLOTLY GRAPH
# ==========================================
with col_out:
    st.markdown(f"#### ANALYTICS {admin_tag}", unsafe_allow_html=True)
        
    c1, c2 = st.columns(2)
    waste_occurring = (in_occ == 0 and (proj_override or num_pcs > 0))
    
    if waste_occurring:
        c1.metric("Efficiency", f"{eff_score:.1f}%", delta="", delta_color="inverse")
    else:
        c1.metric("Efficiency", f"{eff_score:.1f}%", delta=None, delta_color="normal")
        
    c2.metric("CRR", f"{crr_percentage:.1f}%")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=st.session_state.history_time, 
        y=st.session_state.history_base, 
        mode='lines', 
        name='Baseline', 
        line=dict(color='rgba(255, 75, 75, 0.6)', width=2, dash='dot')
    ))
    
    fig.add_trace(go.Scatter(
        x=st.session_state.history_time, 
        y=st.session_state.history_opt, 
        mode='lines', 
        name='Optimized', 
        line=dict(color='#00FF00', width=3, shape='spline', smoothing=0.3), 
        fill='tozeroy', 
        fillcolor='rgba(0, 255, 0, 0.1)'
    ))
    
    fig.update_layout(
        height=300, 
        margin=dict(l=0, r=20, t=10, b=20), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        showlegend=False, 
        xaxis=dict(
            showticklabels=False, 
            showgrid=False, 
            zeroline=False
        ), 
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)', 
            tickfont=dict(color='#aaaaaa'), 
            zerolinecolor='rgba(255,255,255,0.1)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# --- 10. MINIMAL LOWKEY LEGEND (REVERTED TO COLORED CIRCLES) ---
st.markdown("""
    <div style='text-align: center; opacity: 0.6; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;'>
        <span class='legend-badge-mini' style='color: #ff6b6b;'>🔴 Critical / Active Waste</span> &nbsp;&nbsp; 
        <span class='legend-badge-mini' style='color: #ffca28;'>🟡 Caution / Override Active</span> &nbsp;&nbsp; 
        <span class='legend-badge-mini' style='color: #4ade80;'>🟢 Optimal Efficiency</span> &nbsp;&nbsp; 
        <span class='legend-badge-mini' style='color: #60a5fa;'>🔵 System Standby</span> 
    </div>
    """, unsafe_allow_html=True)
