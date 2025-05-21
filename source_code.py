import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Domain selection and calculation ---
def chemical_reaction_domain():
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

# --- Input data ---
def input_data():
    print("\nDefine whether the leak is steady state or time dependent: ")
    print("1. S.S (boundary condition keep constant with time, unique values)")
    print("2. T.D (boundary condition changes with respect to time, time series data imported from .xlsx file)")
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

# --- Physical property calculations ---
def calculate_lithium_density(temperature):
    return 562 - 0.1 * temperature

def calculate_water_density(temperature):
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

# --- Reaction coefficient calculation ---
def reaction_coeff_calculation(coeff_choice, temp_for_coeff, frequency_for_coeff=None, activation_energy_for_coeff=None, gas_constant=8.314):
    if coeff_choice == '1':
        return frequency_for_coeff * math.exp(-(activation_energy_for_coeff / (gas_constant * temp_for_coeff)))
    elif coeff_choice == '2':
        return ((0.8173 * temp_for_coeff) - 30.738)*(1/(100*3600))
    elif coeff_choice == '3':
        return (0.9384 * math.exp(0.0431 * temp_for_coeff))*(1/(100*3600))
    else:
        print("Invalid choice. Please restart and choose a valid option.")
        return None

# --- Main program ---
def main():
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
    MW_Li = 0.06941
    MW_LiOH = 0.02395
    MW_H2 = 0.002016
    reac_area = surface_area
    H2O_tot = 0
    Li_tot = 0
    LiOH_tot = 0
    H2_tot = 0
    time_steps = len(df['Time (s)'])
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
        energy_in_kj = 222 * H2O_in_mole
        H2O_tot += H2O_in_kg
        Li_tot += Li_in_kg
        LiOH_tot += LiOH_in_kg
        H2_tot += H2_in_kg
        print(f"Time step {seconds}, Reaction coeff. = {reac_coeff:.3e} (kg/m².s), H2O_mass = {H2O_in_kg:.3e} (kg), Li_mass = {Li_in_kg:.3e} (kg)")
    print(f"\n**Calculation successfully completed by time reaching to: {time_steps-1} seconds**")

if __name__ == "__main__":
    main() 