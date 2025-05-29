"""
Lithium-Water Chemical Reaction Kinetic Estimator
------------------------------------------------
This script models the chemical interaction between lithium and water, allowing the user to estimate reaction kinetics, mass balances, and energy release over time.

Features:
- User input for domain geometry and reaction conditions
- Physical property calculations for lithium and water
- Multiple kinetic models (Arrhenius, linear, exponential)
- Time-stepped simulation of the lithium-water reaction
- Output of key results at each time step

Author: [Samad KHANI]
License: Non-commercial, Attribution-Required (see LICENSE)
"""

import math
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objs as go
import os

st.set_page_config(page_title="Lithium-Water Reaction Estimator", layout="centered")

# =============================================================
# Streamlit App Title and Description
# =============================================================
st.title("Lithium-Water Chemical Reaction Kinetic Estimator")
st.markdown("""
This app models the chemical interaction between lithium and water, allowing you to estimate reaction kinetics, mass balances, and energy release over time.

**Features:**
- User input for domain geometry and reaction conditions
- Physical property calculations for lithium and water
- Multiple kinetic models (Arrhenius, linear, exponential)
- Time-stepped simulation of the lithium-water reaction
- Interactive output and plots
""")

# ================= LICENSE AGREEMENT ENFORCEMENT =================
LICENSE_PATH = os.path.join(os.path.dirname(__file__), 'LICENSE')
with open(LICENSE_PATH, 'r', encoding='utf-8') as f:
    license_text = f.read()

st.header("License Agreement")
with st.expander("View License Terms", expanded=True):
    st.code(license_text, language=None)
agree = st.checkbox("I have read and agree to the terms of the above license.")
if not agree:
    st.warning("You must agree to the license terms to use this application.")
    st.stop()

# =============================================================
# SECTION 1: DOMAIN SELECTION AND GEOMETRY CALCULATION
# =============================================================
def get_domain():
    st.sidebar.header("Domain Geometry")
    shape = st.sidebar.selectbox("Shape", ("Cubic", "Cylindrical", "Hemispherical", "Hemisphere + Cylinder"))
    if shape == "Cubic":
        l = st.sidebar.number_input("Length (m)", 0.0, 100.0, 1.0)
        w = st.sidebar.number_input("Width (m)", 0.0, 100.0, 1.0)
        h = st.sidebar.number_input("Height (m)", 0.0, 100.0, 1.0)
        volume = l * w * h
        area = 2 * (l * w + l * h + h * w)
        surface_area = l * w
    elif shape == "Cylindrical":
        r = st.sidebar.number_input("Radius (m)", 0.0, 100.0, 0.5)
        h = st.sidebar.number_input("Height (m)", 0.0, 100.0, 1.0)
        volume = math.pi * r ** 2 * h
        area = 2 * math.pi * r * (r + h)
        surface_area = math.pi * r ** 2
    elif shape == "Hemispherical":
        r = st.sidebar.number_input("Radius (m)", 0.0, 100.0, 0.5)
        volume = (2/3) * math.pi * r ** 3
        area = 3 * math.pi * r ** 2
        surface_area = math.pi * r ** 2
    else:
        r = st.sidebar.number_input("Radius (m)", 0.0, 100.0, 0.5)
        h = st.sidebar.number_input("Height (m)", 0.0, 100.0, 1.0)
        volume = (2/3) * math.pi * r ** 3 + math.pi * r ** 2 * h
        area = 3 * math.pi * r ** 2 + 2 * math.pi * r * h
        surface_area = math.pi * r ** 2
    return {"shape": shape, "volume": volume, "area": area, "surface_area": surface_area}

# =============================================================
# SECTION 2: INPUT DATA HANDLING
# =============================================================
def get_input_data():
    st.sidebar.header("Reaction Conditions")
    mode = st.sidebar.radio("Leak Mode", ("Steady State", "Time Dependent"))
    if mode == "Steady State":
        up_p = st.sidebar.number_input("Upstream Pressure (bar)", 0.0, 100.0, 1.0)
        up_t = st.sidebar.number_input("Upstream Temp (°C)", -273.0, 1000.0, 25.0)
        down_p = st.sidebar.number_input("Downstream Pressure (bar)", 0.0, 100.0, 1.0)
        down_t = st.sidebar.number_input("Downstream Temp (°C)", -273.0, 1000.0, 25.0)
        leak_rate = st.sidebar.number_input("Lithium Leak Rate (kg/s)", 0.0, 100.0, 0.01)
        break_size = st.sidebar.number_input("Break Size (m²)", 0.0, 100.0, 0.001)
        drainage_rate = st.sidebar.number_input("Drainage Rate (kg/s)", 0.0, 100.0, 0.005)
        gas_flow = st.sidebar.number_input("Gas Flow Rate (kg/s)", 0.0, 100.0, 0.01)
        tmax = st.sidebar.number_input("Total Time (s)", 1, 100000, 1000)
        times = np.arange(0, tmax + 1)
        data = {
            'Time (s)': times,
            'Leak_rate (kg/s)': leak_rate,
            'Break_size (m²)': break_size,
            'Upstream_Pressure (bar)': up_p,
            'Upstream_Temperature (°C)': up_t,
            'Drainage_rate (kg/s)': drainage_rate,
            'Gas_flow_rate (kg/s)': gas_flow,
            'Downstream_Pressure (bar)': down_p,
            'Downstream_Temperature (°C)': down_t,
        }
        df = pd.DataFrame(data)
    else:
        uploaded = st.sidebar.file_uploader("Upload Input_Data.xlsx", type=["xlsx"])
        if uploaded:
            df1 = pd.read_excel(uploaded, sheet_name='Upstream_container_volume')
            df2 = pd.read_excel(uploaded, sheet_name='Downstream_reaction_volume')
            df = pd.concat([df1, df2], axis=1)
            time_cols = df.columns[df.columns == 'Time (s)']
            if len(time_cols) > 1:
                df = df.drop(time_cols[2:], axis=1)
        else:
            st.warning("Upload required for Time Dependent mode.")
            return None
    return df

# =============================================================
# SECTION 3: PHYSICAL PROPERTY CALCULATIONS
# =============================================================
def calculate_lithium_density(temperature):
    """
    Returns the density of lithium (kg/m³) as a function of temperature (K).
    """
    return 562 - 0.1 * temperature

def calculate_water_density(temperature):
    """
    Returns the density of water (kg/m³) as a function of temperature (K).
    """
    a= -2.8054253e-10
    b = 1.0556302e-7
    c = -4.6170461e-5
    d = -0.0079870401
    e = 16.945176
    f = 999.83952
    g = 0.01687985
    numerator = ((((a * temperature + b) * temperature + c) * temperature + d) * temperature + e) * temperature + f
    denominator = 1 + g * temperature
    return numerator / denominator

# =============================================================
# SECTION 4: REACTION COEFFICIENT (KINETIC) CALCULATION
# =============================================================
def get_kinetics():
    st.sidebar.header("Kinetics")
    model = st.sidebar.selectbox("Model", ("Arrhenius", "Linear", "Exponential"))
    if model == "Arrhenius":
        freq = st.sidebar.number_input("Pre-exponential Factor (kg/m².s)", 0.0, 1e10, 1.0)
        ea = st.sidebar.number_input("Activation Energy (J/mol)", 0.0, 1e6, 50000.0)
    else:
        freq = None
        ea = None
    return model, freq, ea

def reaction_coeff(model, temp, freq=None, ea=None, R=8.314):
    if model == 'Arrhenius':
        return freq * math.exp(-(ea / (R * temp)))
    elif model == 'Linear':
        return ((0.8173 * temp) - 30.738) / (100 * 3600)
    elif model == 'Exponential':
        return (0.9384 * math.exp(0.0431 * temp)) / (100 * 3600)
    return 0

# =============================================================
# SECTION 5: MAIN SIMULATION LOGIC
# =============================================================
@st.cache_data(show_spinner=False)
def run_sim(domain, df, model, freq, ea):
    MW_H2O, MW_Li, MW_LiOH, MW_H2 = 0.01801528, 0.006941, 0.02395, 0.002016
    area = domain['surface_area']
    alfa, beta = 1, 0.45
    n = len(df)
    t = df['Time (s)'].values
    T = df['Downstream_Temperature (°C)'].values
    leak = df['Leak_rate (kg/s)'].values if 'Leak_rate (kg/s)' in df else np.zeros(n)
    drain = df['Drainage_rate (kg/s)'].values if 'Drainage_rate (kg/s)' in df else np.zeros(n)
    gas = df['Gas_flow_rate (kg/s)'].values if 'Gas_flow_rate (kg/s)' in df else np.zeros(n)
    H2O, Li, LiOH, H2, heat = [], [], [], [], []
    vap_flow, li_inv = [], []
    li_pool, vap = 0, 0
    for i in range(n):
        reac_coeff = reaction_coeff(model, T[i], freq, ea)
        H2O_kg = reac_coeff * math.log(alfa + beta * t[i]) * area if t[i] > 0 else 0
        H2O_mol = H2O_kg / MW_H2O
        Li_kg = H2O_mol * MW_Li
        LiOH_kg = H2O_mol * MW_LiOH
        H2_kg = H2O_mol * 0.5 * MW_H2
        heat_kj = 222 * H2O_mol
        H2O.append(H2O_kg)
        Li.append(Li_kg)
        LiOH.append(LiOH_kg)
        H2.append(H2_kg)
        heat.append(heat_kj)
        vap += gas[i] - H2O_kg
        vap_flow.append(vap)
        li_pool += leak[i] - drain[i] - Li_kg
        li_inv.append(li_pool)
    return t, H2O, Li, LiOH, H2, heat, vap_flow, li_inv

# =============================================================
# SECTION 6: PLOTTING WITH PLOTLY
# =============================================================
def plot_lines(x, ys, names, title, ytitle):
    fig = go.Figure()
    for y, name in zip(ys, names):
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=name))
    fig.update_layout(title=title, xaxis_title='Time (s)', yaxis_title=ytitle, template='plotly_dark', height=400)
    st.plotly_chart(fig, use_container_width=True)

# =============================================================
# MAIN STREAMLIT APP LOGIC
# =============================================================
def main():
    domain = get_domain()
    df = get_input_data()
    if df is None:
        st.stop()
    model, freq, ea = get_kinetics()
    if st.button("Run Simulation"):
        t, H2O, Li, LiOH, H2, heat, vap_flow, li_inv = run_sim(domain, df, model, freq, ea)
        st.subheader("Simulation Results")
        plot_lines(t, [H2O, Li], ["H₂O (kg)", "Li (kg)"], "Reactants vs Time", "Mass (kg)")
        plot_lines(t, [H2, LiOH], ["H₂ (kg)", "LiOH (kg)"], "Products vs Time", "Mass (kg)")
        plot_lines(t, [heat], ["Heat Released (kJ)"], "Cumulative Heat Generation", "Heat (kJ)")
        plot_lines(t, [vap_flow], ["Cumulative Water/Vapour Flow (kg)"], "Water/Vapour Flow Over Pool", "Flow (kg)")
        plot_lines(t, [li_inv], ["Lithium Inventory (kg)"], "Lithium Inventory in Pool", "Inventory (kg)")
        st.success(f"Calculation completed for {int(t[-1])} seconds.")

if __name__ == "__main__":
    main() 
