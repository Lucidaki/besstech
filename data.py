import pandas as pd
import numpy as np

def get_bess_data():
    """
    Returns a DataFrame containing performance and financial data for various BESS technologies
    across different time horizons (Current, 3 Years, 5 Years, 10 Years).
    
    Data is representative based on industry trends (NREL, BNEF) as of late 2024/early 2025.
    """
    
    # Define technologies and their categories
    technologies = {
        'Li-ion LFP': {'Type': 'Commercial', 'Maturity': 'Mature'},
        'Li-ion NMC': {'Type': 'Commercial', 'Maturity': 'Mature'},
        'Lead-Acid': {'Type': 'Commercial', 'Maturity': 'Legacy'},
        'Vanadium Redox Flow': {'Type': 'Commercial', 'Maturity': 'Early Commercial'},
        'Sodium-ion': {'Type': 'Developing', 'Maturity': 'Early Commercial'},
        'Solid State': {'Type': 'Developing', 'Maturity': 'R&D/Pilot'},
        'Metal-Air (Iron-Air)': {'Type': 'Developing', 'Maturity': 'Pilot'},
        'Zinc-Hybrid': {'Type': 'Developing', 'Maturity': 'Pilot'}
    }
    
    timeframes = [0, 3, 5, 10] # Years from now
    
    data = []
    
    for tech, info in technologies.items():
        for year in timeframes:
            # Base values (approximate current status)
            capex = 0 # $/kWh
            efficiency = 0 # %
            cycles = 0 # cycles
            energy_density = 0 # Wh/L
            opex_percent = 0 # % of CAPEX/year
            
            # Logic to generate representative trends
            # Note: These are rough estimates for demonstration purposes
            
            if tech == 'Li-ion LFP':
                base_capex = 130
                capex = base_capex * (0.95 ** year) # 5% year on year decline
                efficiency = 95 + (0.1 * year)
                cycles = 6000 + (200 * year)
                energy_density = 350 + (10 * year)
                opex_percent = 1.5
                
            elif tech == 'Li-ion NMC':
                base_capex = 145
                capex = base_capex * (0.96 ** year)
                efficiency = 96 + (0.05 * year)
                cycles = 4000 + (100 * year)
                energy_density = 450 + (15 * year)
                opex_percent = 2.0
                
            elif tech == 'Lead-Acid':
                base_capex = 100
                capex = base_capex * (0.99 ** year) # Very mature, slow decline
                efficiency = 85 + (0.1 * year)
                cycles = 1500 + (10 * year)
                energy_density = 80
                opex_percent = 3.0

            elif tech == 'Vanadium Redox Flow':
                base_capex = 250 # High initial capex, but long life
                capex = base_capex * (0.90 ** year) # Fast learning curve expected
                efficiency = 75 + (0.5 * year) # Improvements expected
                cycles = 20000 # Almost infinite cycle life
                energy_density = 40 + (2 * year)
                opex_percent = 1.0
                
            elif tech == 'Sodium-ion':
                base_capex = 110 # Promising low cost
                if year == 0: base_capex = 150 # Higher now due to scale
                capex = base_capex * (0.92 ** year)
                efficiency = 92 + (0.2 * year)
                cycles = 4000 + (300 * year)
                energy_density = 250 + (15 * year)
                opex_percent = 1.5
                
            elif tech == 'Solid State':
                base_capex = 500 # Very high now
                if year == 0: 
                    capex = 800
                elif year >= 3:
                    capex = 400 * (0.85 ** (year-3))
                    
                efficiency = 98
                cycles = 5000 + (500 * year)
                energy_density = 800 + (20 * year)
                opex_percent = 1.0
                
            elif tech == 'Metal-Air (Iron-Air)':
                base_capex = 200
                if year >= 3:
                     capex = 70 * (0.95 ** (year-3)) # Target $20/kWh long term
                else: 
                     capex = 200
                     
                efficiency = 60 # Low efficiency is characteristic
                cycles = 5000 
                energy_density = 100
                opex_percent = 0.5
            
            elif tech == 'Zinc-Hybrid':
                 base_capex = 180
                 capex = 180 * (0.94 ** year)
                 efficiency = 80 + (0.2 * year)
                 cycles = 10000
                 energy_density = 150
                 opex_percent = 1.2

            # Normalize constraints
            efficiency = min(efficiency, 99.9)
            
            data.append({
                'Technology': tech,
                'Category': info['Type'],
                'Maturity': info['Maturity'],
                'Timeframe (Years)': year,
                'Year': 2025 + year,
                'CAPEX ($/kWh)': round(capex, 2),
                'Efficiency (%)': round(efficiency, 2),
                'Cycle Life': int(cycles),
                'Energy Density (Wh/L)': int(energy_density),
                'OPEX (% of CAPEX)': opex_percent,
                'LCOS ($/MWh)': calculate_simplified_lcos(capex, opex_percent, cycles, efficiency) 
            })
            
    return pd.DataFrame(data)

def calculate_simplified_lcos(capex, opex_percent, cycles, efficiency):
    """
    Very simplified LCOS model for relative comparison.
    LCOS ~= (CAPEX + NPV(OPEX)) / Total Discharged Energy
    """
    # Assumptions
    dod = 0.8 # Depth of discharge
    discount_rate = 0.07
    
    # Total Energy Throughput (kWh) per kWh of capacity over life
    # Capped at calendar life of ~20 years if cycles are huge
    # Assuming 1 cycle per day
    max_years = 20
    daily_cycles = 1
    total_physical_cycles = cycles
    total_calendar_cycles = max_years * 365 * daily_cycles
    
    realizable_cycles = min(total_physical_cycles, total_calendar_cycles)
    
    total_energy_discharged = realizable_cycles * dod * (efficiency / 100.0)
    
    # Costs
    # Initial Investment
    investment = capex
    
    # O&M NPV
    # Simple annuity approximation for O&M
    annual_opex = capex * (opex_percent / 100.0)
    
    # NPV of O&M over the operational life (years)
    operational_years = realizable_cycles / 365
    if discount_rate > 0:
        opex_npv = annual_opex * ((1 - (1 + discount_rate)**(-operational_years)) / discount_rate)
    else:
        opex_npv = annual_opex * operational_years
        
    total_cost = investment + opex_npv
    
    # LCOS $/kWh -> $/MWh
    if total_energy_discharged > 0:
        lcos_kwh = total_cost / total_energy_discharged
        return round(lcos_kwh * 1000, 2)
    return 0

if __name__ == "__main__":
    df = get_bess_data()
    print(df.head())
    print(f"\nGenerated {len(df)} rows.")
