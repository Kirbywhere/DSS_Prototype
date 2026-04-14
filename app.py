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
if 'active_pcs' not in st.session_state: st.session_state.active_pcs = 20
if 'proj_on' not in st.session_state: st.session_state.proj_on = False
if 'in_occ' not in st.session_state: st.session_state.in_occ = 24
if 'in_tmp' not in st.session_state: st.session_state.in_tmp = 34

# Permanent memory for the override inputs
if 'sim_pc_w' not in st.session_state: st.session_state.sim_pc_w = 150
if 'sim_proj_w' not in st.session_state: st.session_state.sim_proj_w = 300
if 'sim_rate' not in st.session_state: st.session_state.sim_rate = 7.55
if 'sim_light_w' not in st.session_state: st.session_state.sim_light_w = 27
if 'sim_fan_w' not in st.session_state: st.session_state.sim_fan_w = 130

# Callback function to toggle Admin mode cleanly
def toggle_admin(): 
    st.session_state.show_admin = not st.session_state.show_admin
    
    if st.session_state.show_admin:
        st.session_state.sim_pc_w = 150
        st.session_state.sim_proj_w = 300
        st.session_state.sim_light_w = 27
        st.session_state.sim_fan_w = 130
        st.session_state.sim_rate = 7.55

# --- 2. DYNAMIC HARDWARE CONSTANTS ---
ANNUAL_HOURS = 10 * 264 
STD_W_PC = 150 
STD_W_PROJ = 300
STD_W_Switch1 = 27
STD_W_Switch2 = 27
STD_W_FANS = 130
STD_RATE = 7.55

if st.session_state.show_admin:
    W_PC = st.session_state.sim_pc_w
    W_PROJ = st.session_state.sim_proj_w
    ACTIVE_RATE = st.session_state.sim_rate
    W_Switch1 = st.session_state.sim_light_w
    W_Switch2 = st.session_state.sim_light_w 
    W_FANS = st.session_state.sim_fan_w
else:
    W_PC = STD_W_PC
    W_PROJ = STD_W_PROJ
    ACTIVE_RATE = STD_RATE
    W_Switch1 = STD_W_Switch1
    W_Switch2 = STD_W_Switch2
    W_FANS = STD_W_FANS

# --- 3. PREMIUM CSS STYLING ---
st.markdown("""
    <style>
    /* Import Premium SaaS Font */
    @import url('https://fonts.googleapis.com/csSwitch2?family=Inter:wght@300;400;600;700;800&display=swap');

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
        padding-bottom: 2rem !important;
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
        margin-bottom: 2rem;
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
    
    h3 { margin-bottom: 0rem !important; padding-bottom: 0.2rem !important; }
    h4 { margin-bottom: 0rem !important; padding-bottom: 0.5rem !important; font-weight: 700 !important; letter-spacing: 1px;}
    
    /* --- FONT SIZE CONTROL: OUTSIDE THE BOXES --- */
    /* 1. Increase general text and Markdown paragraphs */
    p, .stMarkdown p {
        font-size: 1.5rem !important; 
    }
    /* 2. Increase input labels (Sliders, Toggles, Radio buttons) */
    label, div[data-testid="stWidgetLabel"] p, .stRadio label p {
        font-size: 1.3rem !important;
        font-weight: 600 !important; 
    }
    /* 3. Increase H4 Headings */
    h4 {
        font-size: 2.0rem !important; 
    }

    /* --- FONT SIZE CONTROL: INSIDE THE METRIC BOXES --- */
    /* Resize Metric Text to prevent cutoff for large numbers */
    div[data-testid="stMetricValue"] {
        font-size: 2.0rem !important; 
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    /* Ensure the metric label inside the box doesn't inherit the larger general <p> size */
    div[data-testid="stMetricLabel"] p {
        font-size: 1.0rem !important;
        font-weight: 400 !important;
    }
    
    /* --- FIX FOR OVERSIZED DELTA / WATTAGE DROP NUMBERS --- */
    /* Forces the text, arrows, and any hidden paragraph tags inside the delta back to a small size */
    div[data-testid="stMetricDelta"], 
    div[data-testid="stMetricDelta"] p, 
    div[data-testid="stMetricDelta"] span, 
    div[data-testid="stMetricDelta"] div {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    /* Shrinks the little up/down arrow icon so it matches the smaller text */
    div[data-testid="stMetricDelta"] svg {
        width: 1rem !important;
        height: 1rem !important;
    }
    
    /* --- FIX FOR OVERSIZED SLIDER NUMBERS --- */
    /* Targets the inner mechanics of the slider to shrink the min/max/current values back to normal */
    div[data-baseweb="slider"] * {
        font-size: 0.9rem !important; 
        font-weight: 400 !important;
    }

    /* --- FIX FOR OVERSIZED BUTTONS (Admin & Popovers) --- */
    /* Forces the text inside all buttons back down to a standard, clean size */
    button p, 
    button div, 
    button span {
        font-size: 1.0rem !important; 
        font-weight: 600 !important;
    }
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
    # Increased size for better branding presence
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
    
    proj_override = st.toggle("Projector Active", value=st.session_state.proj_on)
    st.session_state.proj_on = proj_override
    
    in_occ = st.slider("Students", 0, 40, value=st.session_state.in_occ) 
    st.session_state.in_occ = in_occ
    
    in_tmp = st.slider("Temp (°C)", 20, 40, value=st.session_state.in_tmp) 
    st.session_state.in_tmp = in_tmp

    num_pcs = 0 
    if room_type == "Computer Lab":
        num_pcs = st.number_input("💻 Active PCs", min_value=0, max_value=50, value=st.session_state.active_pcs)
        st.session_state.active_pcs = num_pcs

    st.markdown("<br>", unsafe_allow_html=True) 
    
    # --- ADMIN CONTROLS ---
    if not st.session_state.show_admin:
        st.button("⚙️ Enter Admin Mode", on_click=toggle_admin, use_container_width=True)
    else:
        st.button("❌ Exit Admin Mode", on_click=toggle_admin, use_container_width=True)
        
        with st.popover("🛠️ Open Admin Controls", use_container_width=True):
            st.markdown("#### 🛠️ Manual Override Variables")
            
            if room_type == "Computer Lab" and num_pcs > 0:
                st.slider("PC Wattage", 15, 600, key="sim_pc_w", help="Standard: ~150W")
                
            if proj_override:
                st.slider("Projector Wattage", 50, 800, key="sim_proj_w", help="Standard: ~300W")
                
            st.slider("Light Bulb Wattage", 10, 300, key="sim_light_w", help="Standard: ~27W")
            st.slider("Fan Wattage", 30, 250, key="sim_fan_w", help="Standard: ~130W")
            st.number_input("Rate (₱/kWh)", 5.0, 30.0, step=0.5, key="sim_rate")


# --- SIMULATION CALCULATIONS ---
sim.input['occupancy'] = in_occ
sim.input['temp'] = in_tmp
sim.compute()
out_val = sim.output['energy_rec']

if in_occ == 0:
    draw_lights, draw_fans = 0, 0
    rec_lights, rec_fans = "OFF", "OFF"
    opt_proj_w, opt_pc_load = 0, 0
else:
    if in_occ > 20 or out_val > 70: 
        draw_lights, rec_lights = W_Switch1 + W_Switch2, "FULL (Switch1 & Switch2)"
    elif in_occ > 0 or out_val > 35: 
        draw_lights, rec_lights = W_Switch1, "DIM (Switch1)"
    else: 
        draw_lights, rec_lights = 0, "OFF"

    if out_val > 65 or in_tmp >= 27: 
        draw_fans, rec_fans = W_FANS, "HIGH"
    elif out_val > 40 or in_tmp >= 24: 
        draw_fans, rec_fans = W_FANS * 0.6, "MEDIUM"
    else: 
        draw_fans, rec_fans = 0, "LOW/OFF"

    opt_proj_w = W_PROJ if proj_override else 0
    opt_pc_count = min(num_pcs, in_occ) if room_type == "Computer Lab" else 0
    opt_pc_load = opt_pc_count * W_PC

active_w = draw_lights + draw_fans + opt_proj_w + opt_pc_load

peak_w = (W_Switch1 + W_Switch2) + W_FANS + (W_PROJ if proj_override else 0) + (num_pcs * W_PC)
if peak_w == 0: peak_w = 1

monthly_base_php = (peak_w/1000 * 10 * 22 * ACTIVE_RATE)
Energy_draw_php = (active_w/1000 * 10 * 22 * ACTIVE_RATE)
savings_php = max(0, monthly_base_php - Energy_draw_php)
crr_percentage = (savings_php / monthly_base_php) * 100

# Calculate true system efficiency based on actual power savings
if peak_w > 0:
    eff_score = max(0.0, (1 - (active_w / peak_w)) * 100)
else:
    eff_score = 0.0

# --- DYNAMIC "STANDBY / ALERT" THEME OVERRIDE ---
if in_occ == 0:
    st.markdown("""
        <style>
        :root {
            --alert-opacity: 1;
            --metric-bg: rgba(60, 25, 25, 0.7);
            --metric-border: #7a3535;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        :root {
            --alert-opacity: 0;
            --metric-bg: rgba(38, 39, 48, 0.6);
            --metric-border: #464b5d;
        }
        </style>
    """, unsafe_allow_html=True)

# --- UPDATE HISTORY FOR GRAPH ---
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
    if st.session_state.show_admin:
        st.markdown("#### CONSUMPTION <span style='color:#ffca28; font-size:0.8em;'>⚠️ OVERRIDDEN</span>", unsafe_allow_html=True)
    else:
        st.markdown("#### CONSUMPTION")
    
    watt_savings = int(peak_w - active_w)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Baseline", f"{int(peak_w)}W")
    m2.metric("Optimized", f"{int(active_w)}W")
    m3.metric("Saved", f"{watt_savings}W", delta=f"{watt_savings}W Drop", delta_color="normal")
    
    m4, m5, m6 = st.columns(3)
    m4.metric("Current", f"₱{monthly_base_php:,.0f}")
    m5.metric("Optimized", f"₱{Energy_draw_php:,.0f}")
    m6.metric("Saved", f"₱{savings_php:,.0f}", delta=f"₱{savings_php:,.0f} Saved", delta_color="normal")
    
    st.markdown("<br>", unsafe_allow_html=True) 
    
    # SYSTEM RECOMMENDATIONS WITH CUSTOM BADGES
    st.markdown("#### SYSTEM RECOMMENDATIONS")
    
    def badge(text, style_class):
        st.markdown(f'<div class="sys-badge {style_class}">{text}</div>', unsafe_allow_html=True)

    if rec_lights == "FULL (Switch1 & Switch2)": badge(f"💡 LIGHTS: {rec_lights}", "badge-error")
    elif rec_lights == "DIM (Switch1)": badge(f"💡 LIGHTS: {rec_lights}", "badge-warning")
    else: badge(f"💡 LIGHTS: {rec_lights}", "badge-info")

    if rec_fans == "HIGH": badge(f"🌀 FANS: {rec_fans}", "badge-error")
    elif rec_fans == "MEDIUM": badge(f"🌀 FANS: {rec_fans}", "badge-warning")
    else: badge(f"🌀 FANS: {rec_fans}", "badge-success")
    
    if proj_override: 
        if in_occ == 0: badge("🎥 PROJECTOR: TURN OFF (Room Empty)", "badge-error")
        else: badge("🎥 PROJECTOR: ACTIVE (In Use)", "badge-warning")
    else:
        badge("🎥 PROJECTOR: OFF", "badge-info")
            
    if room_type == "Computer Lab":
        if in_occ == 0 and num_pcs > 0: 
            badge(f"💻 PCs: TURN OFF ALL {num_pcs} (Empty)", "badge-error")
        elif num_pcs > in_occ and in_occ > 0: 
            badge(f"💻 PCs: TURN OFF {num_pcs - in_occ} (Only {in_occ} needed)", "badge-warning")
        elif num_pcs > 0:
            badge(f"💻 PCs: {num_pcs} Active (Optimal)", "badge-success")
        else:
            badge("💻 PCs: 0 Active", "badge-info")

# ==========================================
# COLUMN 3: ANALYTICS & PLOTLY GRAPH
# ==========================================
with col_out:
    if st.session_state.show_admin:
        st.markdown("#### ANALYTICS <span style='color:#ffca28; font-size:0.8em;'>⚠️ OVERRIDDEN</span>", unsafe_allow_html=True)
    else:
        st.markdown("#### ANALYTICS")
        
    c1, c2 = st.columns(2)
    
    waste_occurring = (in_occ == 0 and (proj_override or num_pcs > 0))
    eff_delta = "-WASTE" if waste_occurring else None
    eff_delta_color = "inverse" if eff_delta else "normal"
    
    c1.metric("Efficiency", f"{eff_score:.1f}%", delta=eff_delta, delta_color=eff_delta_color)
    c2.metric("CRR", f"{crr_percentage:.1f}%")
    
    # SAAS STYLE GRAPH
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=st.session_state.history_time, y=st.session_state.history_base, 
        mode='lines', name='Baseline', 
        line=dict(color='rgba(255, 75, 75, 0.6)', width=2, dash='dot'),
        hoverinfo='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=st.session_state.history_time, y=st.session_state.history_opt, 
        mode='lines', name='Optimized', 
        line=dict(color='#00FF00', width=3, shape='spline', smoothing=0.3), 
        fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.1)',
        hoverinfo='y'
    ))

    last_x = st.session_state.history_time[-1]
    last_base_y = st.session_state.history_base[-1]
    last_opt_y = st.session_state.history_opt[-1]

    fig.add_annotation(x=last_x, y=last_base_y, text="Baseline", showarrow=False, 
                       yshift=15, font=dict(family="Inter", color="#FF4B4B", size=12, weight="bold"))
    fig.add_annotation(x=last_x, y=last_opt_y, text="Optimized", showarrow=False, 
                       yshift=-15, font=dict(family="Inter", color="#00FF00", size=12, weight="bold"))

    # Dynamically find the highest point so the graph ceiling scales perfectly
    max_y = max(max(st.session_state.history_base), max(st.session_state.history_opt))
    ceiling = max_y * 1.2 if max_y > 0 else 100
    
    # Calculate a slight "basement" (5% of the ceiling) so the 0 line hovers
    floor = -(ceiling * 0.05) 

    fig.update_layout(
        height=300, 
        margin=dict(l=0, r=20, t=10, b=20), 
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(
            title="Per Adjustment", 
            title_font=dict(family="Inter", size=11, color='#aaaaaa'), 
            showticklabels=False, 
            showgrid=False, 
            zeroline=False
        ), 
        yaxis=dict(
            range=[floor, ceiling], 
            gridcolor='rgba(255,255,255,0.05)', 
            title="Watts", 
            title_font=dict(family="Inter", size=11, color='#aaaaaa'), 
            tickfont=dict(color='#aaaaaa'),
            zeroline=True, 
            zerolinecolor='rgba(255,255,255,0.1)' 
        )
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
