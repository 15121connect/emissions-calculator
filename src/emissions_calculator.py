"""
Annual emissions calculator for greenhouse gas emissions.

This module calculates annual CO2-equivalent emissions from various sources including:
- Fuel consumption (stationary and mobile)
- Vehicle operations
- Refrigerant leakage
- Transportation Refrigeration Units (TRUs)
- Agricultural operations (livestock, fertilizers, waste)
"""

import pandas as pd
import datetime
from .lookup import lookup


def calculate_annual_emissions(operation_data, fuel_data, refrigerant_gwp, refrigerator_data,
                               vehicle_interventions, vehicle_interventions_tru, farm_emissions):
    """
    Calculates annual emissions for each operation_id in operation_data.
    
    This function performs three main stages:
    1. Lookup secondary data using the generic lookup function
    2. Pre-process data with numeric conversion and error handling
    3. Calculate emissions from all applicable sources
    
    Args:
        operation_data (pd.DataFrame): DataFrame with operation data including:
            - operation_id, entity, fuel_type, fuel_amount, operating_distance
            - refrigerator_type, refrigerant_type, refrigerant_charge, number_of_refrigerators
            - vehicle_subcategory, vehicle_production_year, vehicle_manufacturer
            - tru_subcategory, tru_model_year, tru_refrigerant_type, etc.
            - livestock_type, livestock_count, fertilizer_type, fertilizer_amount
            - waste_type, waste_amount, target_completion_year, state_or_province
        fuel_data (pd.DataFrame): Fuel emission factors by type, mode, location, and year.
        refrigerant_gwp (pd.DataFrame): Global Warming Potential values for refrigerants.
        refrigerator_data (pd.DataFrame): Annual leakage rates by refrigerator type.
        vehicle_interventions (pd.DataFrame): Vehicle fuel efficiency data.
        vehicle_interventions_tru (pd.DataFrame): TRU specifications and emission factors.
        farm_emissions (pd.DataFrame): Agricultural emission factors.
    
    Returns:
        pd.DataFrame: DataFrame with columns:
            - operation_id
            - fuel_emissions
            - vehicle_emissions
            - refrigerant_emissions
            - livestock_emissions
            - fertilizer_emissions
            - waste_emissions
            - tru_emissions
            - total_emissions
    
    Example:
        >>> results = calculate_annual_emissions(
        ...     operation_data=ops_df,
        ...     fuel_data=fuel_df,
        ...     refrigerant_gwp=gwp_df,
        ...     refrigerator_data=refrig_df,
        ...     vehicle_interventions=vehicle_df,
        ...     vehicle_interventions_tru=tru_df,
        ...     farm_emissions=farm_df
        ... )
        >>> print(results[['operation_id', 'total_emissions']])
    """
    results = []
    errors = []
    
    for _, row in operation_data.iterrows():
        
        # ===== STAGE 1: LOOKUP SECONDARY DATA =====
        
        # Refrigerator leakage rate
        annual_leakage_rate = lookup(
            refrigerator_data,
            {'refrigerator_type': row['refrigerator_type']},
            output_columns=['annual_leakage_rate']
        )
        annual_leakage_rate = annual_leakage_rate[0]['annual_leakage_rate'] if annual_leakage_rate else 0
        
        # Refrigerant GWP
        refrigerant_gwp_value = lookup(
            refrigerant_gwp,
            {'refrigerant_type': row['refrigerant_type']},
            output_columns=['refrigerant_gwp']
        )
        refrigerant_gwp_value = refrigerant_gwp_value[0]['refrigerant_gwp'] if refrigerant_gwp_value else 0
        
        # TRU leakage rate
        tru_annual_leakage_rate = lookup(
            refrigerator_data,
            {'refrigerator_type': 'Transportation Refrigeration Unit'},
            output_columns=['annual_leakage_rate']
        )
        tru_annual_leakage_rate = tru_annual_leakage_rate[0]['annual_leakage_rate'] if tru_annual_leakage_rate else 0
        
        # TRU refrigerant GWP
        tru_refrigerant_gwp_value = lookup(
            refrigerant_gwp,
            {'refrigerant_type': row['tru_refrigerant_type']},
            output_columns=['refrigerant_gwp']
        )
        tru_refrigerant_gwp_value = tru_refrigerant_gwp_value[0]['refrigerant_gwp'] if tru_refrigerant_gwp_value else 0
        
        # TRU specifications
        tru_data = lookup(
            vehicle_interventions_tru,
            {'tru_type': row['tru_subcategory'],
             'model_year': row['tru_model_year']},
            output_columns=['co2e_per_kwh_diesel_tru', 'tru_power_rating',
                           'average_load_factor', 'tru_annual_hours',
                           'tru_plug_in_fraction_of_hours']
        )
        emission_factor_diesel_tru = tru_data[0]['co2e_per_kwh_diesel_tru'] if tru_data else 0
        tru_power_rating = tru_data[0]['tru_power_rating'] if tru_data else 0
        average_tru_load_factor = tru_data[0]['average_load_factor'] if tru_data else 0
        tru_annual_hours = tru_data[0]['tru_annual_hours'] if tru_data else 0
        tru_plug_in_fraction_of_hours = tru_data[0]['tru_plug_in_fraction_of_hours'] if tru_data else 0
        
        # Livestock emissions
        emission_per_unit_livestock = lookup(
            farm_emissions,
            {'subcategory': row['livestock_type']},
            output_columns=['emission_per_unit']
        )
        emission_per_unit_livestock = emission_per_unit_livestock[0]['emission_per_unit'] if emission_per_unit_livestock else 0
        
        # Fertilizer emissions
        emission_per_unit_fertilizer = lookup(
            farm_emissions,
            {'subcategory': row['fertilizer_type']},
            output_columns=['emission_per_unit']
        )
        emission_per_unit_fertilizer = emission_per_unit_fertilizer[0]['emission_per_unit'] if emission_per_unit_fertilizer else 0
        
        # Waste emissions
        emission_per_unit_waste = lookup(
            farm_emissions,
            {'subcategory': row['waste_type']},
            output_columns=['emission_per_unit']
        )
        emission_per_unit_waste = emission_per_unit_waste[0]['emission_per_unit'] if emission_per_unit_waste else 0
        
        # Vehicle fuel efficiency with fallbacks
        vehicle_fuel_efficiency = lookup(
            vehicle_interventions,
            {'vehicle_subcategory': row['vehicle_subcategory'], 
             'fuel_type': row['fuel_type'],
             'vehicle_production_year': row['vehicle_production_year'], 
             'vehicle_manufacturer': row['vehicle_manufacturer']},
            output_columns=['fuel_efficiency'],
            fallback_criteria=[
                {'vehicle_production_year': 0}, 
                {'vehicle_manufacturer': 'Others'},
                {'vehicle_production_year': 0, 'vehicle_manufacturer': 'Others'}
            ]
        )
        vehicle_fuel_efficiency = vehicle_fuel_efficiency[0]['fuel_efficiency'] if vehicle_fuel_efficiency else 0
        
        # Fuel emission factors
        fuel_mode = 'mobile' if row['entity'] == 'vehicle' and row['fuel_type'] != 'Electricity' else 'stationary'
        target_year_co2e = f'co2e_{row["target_completion_year"]}'
        current_year = datetime.datetime.now().year
        current_year_co2e = f'co2e_{current_year}'
        
        fuel_emission_factors = lookup(
            fuel_data,
            {'fuel_type': row['fuel_type'], 
             'fuel_mode': fuel_mode,
             'state_or_province': row['state_or_province']},
            output_columns=[current_year_co2e, target_year_co2e],
            fallback_criteria=[{'state_or_province': 'Any'}]
        )
        fuel_emission_factor_current = fuel_emission_factors[0].get(current_year_co2e, 0) if fuel_emission_factors else 0
        
        if row["target_completion_year"] == current_year and len(fuel_emission_factors) == 1:
            fuel_emission_factor_forecast = fuel_emission_factor_current
        else:
            fuel_emission_factor_forecast = fuel_emission_factors[0].get(target_year_co2e, 0) if fuel_emission_factors else 0
        
        
        # ===== STAGE 2: PRE-PROCESS DATA =====
        
        fuel_amount = pd.to_numeric(row['fuel_amount'], errors='coerce')
        fuel_amount = fuel_amount if not pd.isna(fuel_amount) else 0
        
        refrigerant_charge = pd.to_numeric(row['refrigerant_charge'], errors='coerce')
        refrigerant_charge = refrigerant_charge if not pd.isna(refrigerant_charge) else 0
        
        number_of_refrigerators = pd.to_numeric(row['number_of_refrigerators'], errors='coerce')
        number_of_refrigerators = number_of_refrigerators if not pd.isna(number_of_refrigerators) else 0
        
        operating_distance = pd.to_numeric(row['operating_distance'], errors='coerce')
        operating_distance = operating_distance if not pd.isna(operating_distance) else 0
        
        tru_number_of_vehicle_units = pd.to_numeric(row['tru_number_of_vehicle_units'], errors='coerce')
        tru_number_of_vehicle_units = tru_number_of_vehicle_units if not pd.isna(tru_number_of_vehicle_units) else 0
        
        tru_refrigerant_charge = pd.to_numeric(row['tru_refrigerant_charge'], errors='coerce')
        tru_refrigerant_charge = tru_refrigerant_charge if not pd.isna(tru_refrigerant_charge) else 0
        
        livestock_count = pd.to_numeric(row['livestock_count'], errors='coerce')
        livestock_count = livestock_count if not pd.isna(livestock_count) else 0
        
        fertilizer_amount = pd.to_numeric(row['fertilizer_amount'], errors='coerce')
        fertilizer_amount = fertilizer_amount if not pd.isna(fertilizer_amount) else 0
        
        waste_amount = pd.to_numeric(row['waste_amount'], errors='coerce')
        waste_amount = waste_amount if not pd.isna(waste_amount) else 0
        
        
        # ===== STAGE 3: CALCULATE EMISSIONS =====
        
        fuel_emissions = fuel_amount * ((fuel_emission_factor_forecast + fuel_emission_factor_current)) / 2
        
        vehicle_emissions = (operating_distance / vehicle_fuel_efficiency * 
                            ((fuel_emission_factor_forecast + fuel_emission_factor_current) / 2)) if vehicle_fuel_efficiency else 0
        
        refrigerant_emissions = (refrigerant_charge * annual_leakage_rate * 
                                refrigerant_gwp_value * number_of_refrigerators)
        
        livestock_emissions = livestock_count * emission_per_unit_livestock
        
        fertilizer_emissions = fertilizer_amount * emission_per_unit_fertilizer
        
        waste_emissions = waste_amount * emission_per_unit_waste
        
        tru_emissions = ((tru_power_rating * average_tru_load_factor * tru_annual_hours * 
                         tru_plug_in_fraction_of_hours * emission_factor_diesel_tru) + 
                        (tru_refrigerant_gwp_value * tru_refrigerant_charge * 
                         tru_annual_leakage_rate)) * tru_number_of_vehicle_units
        
        total_emissions = (fuel_emissions + vehicle_emissions + refrigerant_emissions + 
                          livestock_emissions + fertilizer_emissions + waste_emissions + 
                          tru_emissions)
        
        results.append({
            'operation_id': row['operation_id'],
            'fuel_emissions': fuel_emissions,
            'vehicle_emissions': vehicle_emissions,
            'refrigerant_emissions': refrigerant_emissions,
            'livestock_emissions': livestock_emissions,
            'fertilizer_emissions': fertilizer_emissions,
            'waste_emissions': waste_emissions,
            'tru_emissions': tru_emissions,
            'total_emissions': total_emissions
        })
    
    annual_emission_table = pd.DataFrame(results)
    
    # Set display format to decimal with 2 decimal places
    pd.options.display.float_format = '{:.2f}'.format
    
    if errors:
        print("Errors encountered during calculation:")
        for error in errors:
            print(error)
    
    return annual_emission_table
