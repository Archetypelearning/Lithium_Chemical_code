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
import matplotlib.pyplot as plt

# =============================================================
# SECTION 1: DOMAIN SELECTION AND GEOMETRY CALCULATION
# =============================================================
def chemical_reaction_domain():
    """
    Prompts the user to select the shape of the reaction domain and input its dimensions.
    Returns a dictionary with calculated volume, area, surface area, and characteristic length.
    """
    print("\nSelect the domain shape for the chemical interactions from the following options:")
    print("1. Cubic")
    print("2. Cylindrical")
    print("3. Hemispherical")
    print("4. Hemisphere + Cylinder")
    domain_choice = input("Enter the number corresponding to your choice (1, 2, 3, or 4): ")
    if domain_choice == '1':
        shape = "cubic"
        length = float(input("Enter the length of the cube (m): "))
        width = float(input("Enter the width of the cube (m): "))
        height = float(input("Enter the height of the cube (m): "))
        volume = length * width * height
        area = (2 * (length * width)) + (2 * (length * height)) + (2 * (height * width))
        surface_area = length * width
        charac_length = math.sqrt(area)
    elif domain_choice == '2':
        shape = "cylindrical"
        radius = float(input("Enter the radius of the cylinder (m): "))
        height = float(input("Enter the height of the cylinder (m): "))
        volume = math.pi * (radius ** 2) * height
        area = 2 * math.pi * radius * (radius + height)
        surface_area = math.pi * (radius ** 2)
        charac_length = math.sqrt(surface_area)
    elif domain_choice == '3':
        shape = "hemispherical"
        radius = float(input("Enter the radius of the hemisphere (m): "))
        volume = (2/3) * math.pi * (radius ** 3)
        area = 3 * math.pi * (radius ** 2)
        surface_area = math.pi * (radius ** 2)
        charac_length = radius * 2
    elif domain_choice == '4':
        shape = "Hemisphere + Cylinder"
        radius = float(input("Enter the radius of the hemisphere (m): "))
        height = float(input("Enter the height of the cylinder (m): "))
        volume = ((2/3) * math.pi * (radius ** 3)) + (math.pi * (radius ** 2)*height)
        area = (3 * math.pi * (radius ** 2)) + (2 * math.pi * (radius * height))
        surface_area = math.pi * (radius ** 2)
        charac_length = math.sqrt(surface_area)
    else:
        print("Invalid choice. Please restart and choose a valid option.")
        return None
    return {"shape": shape, "volume": volume, "area": area, "surface_area": surface_area, "charac_length": charac_length}

# =============================================================
# SECTION 2: INPUT DATA HANDLING
# =============================================================
def input_data():
    """
    Prompts the user to select steady-state or transient conditions and input relevant parameters.
    Returns a DataFrame of input data and the transient choice.
    """
    print("\nDefine whether the leak is steady state or time dependent: ")
    print("1. S.S (boundary condition keep constant with time, unique values)")
    print("2. T.D (boundary condition changes with respect to time, time series data imported from (Input_Data.xlsx) file)")
    transient_choice = input("Enter the number corresponding to your choice (1 or 2): ")
    if transient_choice == '1':
        upstream_pressure = float(input("Enter the pressure in the upstream container (bar): "))
        upstream_temperature = float(input("Enter the temperature in the upstream container (°C): "))
        downstream_pressure = float(input("Enter the pressure in the downstream reaction volume (bar): "))
        downstream_temperature = float(input("Enter the temperature in the downstream reaction volume (°C): "))
        leak_rate = float(input("Enter the lithium leak rate into the reaction volume (kg/s): "))
        break_size = float(input("Enter the break cross section size (m²): "))
        drainage_rate = float(input("Enter the lithium drainage rate from the reaction volume (kg/s): "))
        gas_flow_rate = float(input("Enter the gas flow rate over the lithium pool (kg/s): "))

        transient_time = int(input("Enter the total transient time (s): "))
        time_values = list(range(0, transient_time + 1, 1))
        data_handler = {
            'Time (s)': time_values,
            'Leak_rate (kg/s)': [leak_rate] * len(time_values),
            'Break_size (m²)': [break_size] * len(time_values),
            'Upstream_Pressure (bar)': [upstream_pressure] * len(time_values),
            'Upstream_Temperature (°C)': [upstream_temperature] * len(time_values),
            'Drainage_rate (kg/s)': [drainage_rate] * len(time_values),
            'Gas_flow_rate (kg/s)': [gas_flow_rate] * len(time_values),
            'Downstream_Pressure (bar)': [downstream_pressure] * len(time_values),
            'Downstream_Temperature (°C)': [downstream_temperature] * len(time_values),
        }
        df_input_data = pd.DataFrame(data_handler)
    elif transient_choice == '2':
        print("\nPlease ensure 'Input_Data.xlsx' is present in the working directory with the correct sheet names.")
        df1 = pd.read_excel('Input_Data.xlsx', sheet_name='Upstream_container_volume')
        df2 = pd.read_excel('Input_Data.xlsx', sheet_name='Downstream_reaction_volume')
        df_input_data = pd.concat([df1, df2], axis=1)
        time_columns = df_input_data.columns[df_input_data.columns == 'Time (s)']
        if len(time_columns) > 1:
            df_input_data = df_input_data.drop(time_columns[2:], axis=1)
    else:
        print("Invalid choice for transient. Please restart and choose a valid option.")
        return None
    return df_input_data, transient_choice

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
def reaction_coeff_calculation(coeff_choice, temp_for_coeff, frequency_for_coeff=None, activation_energy_for_coeff=None, gas_constant=8.314):
    """
    Calculates the reaction rate coefficient based on the selected method.
    - Arrhenius (1): Requires frequency factor and activation energy.
    - Linear (2) or Exponential (3): Empirical fits.
    """
    if coeff_choice == '1':
        return frequency_for_coeff * math.exp(-(activation_energy_for_coeff / (gas_constant * temp_for_coeff)))
    elif coeff_choice == '2':
        return ((0.8173 * temp_for_coeff) - 30.738)*(1/(100*3600))
    elif coeff_choice == '3':
        return (0.9384 * math.exp(0.0431 * temp_for_coeff))*(1/(100*3600))
    else:
        print("Invalid choice. Please restart and choose a valid option.")
        return None

# =============================================================
# SECTION 5: MAIN SIMULATION LOOP
# =============================================================
def main():
    """
    Main function to run the lithium-water reaction estimator.
    Handles user interaction, runs the simulation, and prints results.
    """
    print("\n==============================")
    print("Lithium-Water Reaction Estimator")
    print("==============================\n")
    domain_info = chemical_reaction_domain()
    if not domain_info:
        return
    surface_area = domain_info['surface_area']
    print(f"\nDomain: {domain_info['shape']}, Volume: {domain_info['volume']:.2e} m³, Surface Area: {surface_area:.2e} m²")
    df_input_data, transient_choice = input_data()
    df = df_input_data.copy()
    print("\nSelect the reaction rate coefficient (k) calculation option:")
    print("1. Arrhenius equation vs Temperature")
    print("2. Linear extrapolation vs Temperature")
    print("3. Exponential extrapolation vs Temperature")
    coeff_choice = input("Enter the number corresponding to your choice (1, 2 or 3): ")
    if coeff_choice == '1':
        frequency_for_coeff = float(input("Enter frequency rate coefficient (pre-exponential factor) in (kg/m².s): "))
        activation_energy_for_coeff = float(input("Enter activation energy (J/mol): "))
    else:
        frequency_for_coeff = None
        activation_energy_for_coeff = None
    # Kinetic model constants
    alfa = 1
    beta = 0.45
    MW_H2O = 0.01801528
    MW_Li = 0.006941
    MW_LiOH = 0.02395
    MW_H2 = 0.002016
    reac_area = surface_area
    H2O_tot = 0
    Li_tot = 0
    LiOH_tot = 0
    H2_tot = 0
    time_steps = len(df['Time (s)'])
    print("\n--- Simulation Results ---")
    # --- Store time series for plotting ---
    time_series = []
    H2O_series = []
    Li_series = []
    LiOH_series = []
    H2_series = []
    heat_series = []  # Store cumulative heat released (kJ)
    water_vapour_flow_series = []  # Cumulative water/vapour flow over pool (kg)
    lithium_inventory_series = []  # Lithium inventory in pool (kg)

    # Initial lithium inventory in the pool
    lithium_inventory = 0
    # Initial cumulative water/vapour flow
    water_vapour_flow = 0

    for seconds in range(time_steps):
        temp_for_coeff = df.loc[seconds, "Downstream_Temperature (°C)"]
        if coeff_choice == '1':
            reac_coeff = reaction_coeff_calculation(coeff_choice, temp_for_coeff, frequency_for_coeff, activation_energy_for_coeff)
        else:
            reac_coeff = reaction_coeff_calculation(coeff_choice, temp_for_coeff)
        H2O_in_kg = (reac_coeff * math.log(alfa + (beta * (df.loc[seconds, "Time (s)"])))) * reac_area
        H2O_in_mole = H2O_in_kg * (1 / MW_H2O)
        Li_in_mole = H2O_in_mole
        LiOH_in_mole = H2O_in_mole
        H2_in_mole = H2O_in_mole * 0.5
        Li_in_kg = Li_in_mole * MW_Li
        LiOH_in_kg = LiOH_in_mole * MW_LiOH
        H2_in_kg = H2_in_mole * MW_H2
        energy_in_kj = 222 * H2O_in_mole  # Exothermic, positive sign
        H2O_tot += H2O_in_kg
        Li_tot += Li_in_kg
        LiOH_tot += LiOH_in_kg
        H2_tot += H2_in_kg
        print(f"Time step {seconds}, Reaction coeff. = {reac_coeff:.3e} (kg/m².s), H2O_mass = {H2O_in_kg:.3e} (kg), Li_mass = {Li_in_kg:.3e} (kg)")
        # Store for plotting
        time_series.append(df.loc[seconds, "Time (s)"])
        H2O_series.append(H2O_in_kg)
        Li_series.append(Li_in_kg)
        LiOH_series.append(LiOH_in_kg)
        H2_series.append(H2_in_kg)
        heat_series.append(energy_in_kj)

        # --- Water/vapour flow over the pool (cumulative) ---
        if 'Gas_flow_rate (kg/s)' in df.columns:
            gas_flow_rate = df.loc[seconds, 'Gas_flow_rate (kg/s)']
        else:
            gas_flow_rate = 0
        # Assume 1 second per time step (can be adjusted if needed)
        water_vapour_flow += gas_flow_rate * 1
        water_vapour_flow -= H2O_in_kg
        water_vapour_flow_series.append(water_vapour_flow)

        # --- Lithium inventory in the pool ---
        if 'Leak_rate (kg/s)' in df.columns:
            lithium_inlet = df.loc[seconds, 'Leak_rate (kg/s)']
        else:
            lithium_inlet = 0
        if 'Drainage_rate (kg/s)' in df.columns:
            lithium_outlet = df.loc[seconds, 'Drainage_rate (kg/s)']
        else:
            lithium_outlet = 0
        # Update lithium inventory: add inlet, subtract outlet, subtract consumed by reaction
        lithium_inventory += lithium_inlet * 1  # Inlet for this time step
        lithium_inventory -= lithium_outlet * 1  # Outlet for this time step
        lithium_inventory -= Li_in_kg  # Consumed by reaction
        lithium_inventory_series.append(lithium_inventory)

    print(f"\n**Calculation successfully completed by time reaching to: {time_steps-1} seconds**")
    # --- Plot results ---
    plot_reactants(time_series, H2O_series, Li_series)
    plot_products(time_series, H2_series, LiOH_series)
    plot_heat_generation(time_series, heat_series)
    plot_water_vapour_flow(time_series, water_vapour_flow_series)
    plot_lithium_inventory(time_series, lithium_inventory_series)

# =============================================================
# SECTION 6: PLOTTING REACTANTS AND PRODUCTS
# =============================================================
def plot_reactants(time_series, H2O_series, Li_series):
    """
    Plots the time evolution of reactants (H2O and Li) during the reaction.
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(8, 5))
    plt.plot(time_series, H2O_series, label='H₂O (kg)', linewidth=2, color='royalblue')
    plt.plot(time_series, Li_series, label='Li (kg)', linewidth=2, color='orange')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Mass (kg)', fontsize=12)
    plt.title('Reactants: Lithium and Water vs Time', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show(block=True)

def plot_products(time_series, H2_series, LiOH_series):
    """
    Plots the time evolution of products (H2 and LiOH) during the reaction.
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(8, 5))
    plt.plot(time_series, H2_series, label='H₂ (kg)', linewidth=2, color='crimson')
    plt.plot(time_series, LiOH_series, label='LiOH (kg)', linewidth=2, color='seagreen')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Mass (kg)', fontsize=12)
    plt.title('Products: Hydrogen and Lithium Hydroxide vs Time', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show(block=True)

# =============================================================
# SECTION 7: PLOTTING HEAT GENERATION
# =============================================================
def plot_heat_generation(time_series, heat_series):
    """
    Plots the exothermic heat released (-222 kJ/mol H2O) versus time.
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(8, 5))
    plt.plot(time_series, heat_series, color='crimson', linewidth=2, label='Heat Released (kJ)')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Heat Released (kJ)', fontsize=12)
    plt.title('Cumulative Heat Generation (Exothermic)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show(block=True)

# =============================================================
# SECTION 8: PLOTTING WATER/VAPOUR FLOW AND LITHIUM INVENTORY
# =============================================================
def plot_water_vapour_flow(time_series, water_vapour_flow_series):
    """
    Plots the cumulative water/vapour flow over the reaction pool versus time.
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(8, 5))
    plt.plot(time_series, water_vapour_flow_series, color='dodgerblue', linewidth=2, label='Cumulative Water/Vapour Flow (kg)')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Cumulative Water/Vapour Flow (kg)', fontsize=12)
    plt.title('Cumulative Water/Vapour Flow Over Reaction Pool', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show(block=True)

def plot_lithium_inventory(time_series, lithium_inventory_series):
    """
    Plots the lithium inventory in the reaction pool versus time.
    """
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.figure(figsize=(8, 5))
    plt.plot(time_series, lithium_inventory_series, color='darkorange', linewidth=2, label='Lithium Inventory (kg)')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Lithium Inventory (kg)', fontsize=12)
    plt.title('Lithium Inventory in Reaction Pool vs Time', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show(block=True)

# =============================================================
# SCRIPT ENTRY POINT
# =============================================================
if __name__ == "__main__":
    main() 
