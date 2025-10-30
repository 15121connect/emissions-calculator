# Annual Greenhouse Gas Emissions Calculator

A Python-based tool for calculating annual greenhouse gas emissions across various operational profiles including buildings, vehicles, transportation refrigeration units (TRUs), industrial operations, and agricultural activities.

## Overview

This project provides a flexible framework for calculating CO2-equivalent emissions based on operational data and reference datasets. It supports multiple emission sources including:

- **Fuel consumption** (stationary and mobile sources)
- **Vehicle operations** (distance-based calculations)
- **Refrigerant leakage** (stationary refrigeration systems)
- **Transportation Refrigeration Units** (TRUs)
- **Agricultural emissions** (livestock, fertilizers, waste)

## Project Structure

```
emissions-calculator/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/                          # Place your CSV files here
│   │   ├── operation_data_test.csv
│   │   ├── fuel_data.csv
│   │   ├── refrigerant_gwp.csv
│   │   ├── refrigerator_data.csv
│   │   ├── vehicle_interventions.csv
│   │   ├── vehicle_interventions_tru.csv
│   │   ├── farm_emissions.csv
│   │   └── ... (other CSV files)
│   └── outputs/                      # Generated results
├── src/
│   ├── __init__.py
│   ├── data_loader.py               # CSV loading utilities
│   ├── lookup.py                    # Generic lookup function
│   └── emissions_calculator.py      # Main calculation logic
├── scripts/
│   └── calculate_emissions.py       # Executable script
└── notebooks/
    └── analysis.ipynb               # Jupyter notebook for exploration
```

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd emissions-calculator
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Place your CSV data files in the `data/raw/` directory.

## Usage

### Option 1: Run as Script

Calculate emissions for your operational data:

```bash
python scripts/calculate_emissions.py
```

This will:
- Load all CSV files from `data/raw/`
- Process the operation data
- Calculate emissions for each operation
- Save results to `data/outputs/annual_emissions.csv`

### Option 2: Use in Jupyter Notebook

Open `notebooks/analysis.ipynb` to explore the data interactively and customize calculations.

### Option 3: Use as Library

```python
from src.data_loader import load_data_from_directory
from src.emissions_calculator import calculate_annual_emissions

# Load data
dataframes = load_data_from_directory('data/raw/')

# Calculate emissions
results = calculate_annual_emissions(
    dataframes['operation_data_test_2'],
    dataframes['fuel_data'],
    dataframes['refrigerant_gwp'],
    dataframes['refrigerator_data'],
    dataframes['vehicle_interventions'],
    dataframes['vehicle_interventions_tru'],
    dataframes['farm_emissions']
)

print(results)
```

## Data Requirements

### Required CSV Files

The calculator requires the following reference data files in `data/raw/`:

1. **operation_data_test_2.csv** - Main operational data with columns including:
   - `operation_id`, `entity`, `fuel_type`, `fuel_amount`, `operating_distance`
   - `refrigerator_type`, `refrigerant_type`, `refrigerant_charge`, `number_of_refrigerators`
   - `vehicle_subcategory`, `vehicle_production_year`, `vehicle_manufacturer`
   - `tru_subcategory`, `tru_model_year`, `tru_refrigerant_type`, `tru_number_of_vehicle_units`
   - `livestock_type`, `livestock_count`, `fertilizer_type`, `fertilizer_amount`
   - `waste_type`, `waste_amount`, `target_completion_year`, `state_or_province`

2. **fuel_data.csv** - Fuel emission factors by type, mode, location, and year
3. **refrigerant_gwp.csv** - Global Warming Potential values for refrigerants
4. **refrigerator_data.csv** - Annual leakage rates by refrigerator type
5. **vehicle_interventions.csv** - Vehicle fuel efficiency data
6. **vehicle_interventions_tru.csv** - TRU specifications and emission factors
7. **farm_emissions.csv** - Agricultural emission factors

## Calculation Methodology

The calculator performs three main stages for each operation:

1. **Data Lookup**: Retrieves relevant emission factors and technical specifications from reference datasets using a flexible lookup function with fallback support
2. **Data Preprocessing**: Validates and converts numeric values with error handling
3. **Emissions Calculation**: Computes emissions for each source category:
   - Fuel emissions: `fuel_amount × emission_factor`
   - Vehicle emissions: `distance / fuel_efficiency × emission_factor`
   - Refrigerant emissions: `charge × leakage_rate × GWP × units`
   - TRU emissions: Combination of diesel operation and refrigerant leakage
   - Agricultural emissions: `quantity × emission_factor`

Total emissions are the sum of all applicable source categories.

## Features

- **Flexible Lookup System**: Generic lookup function with fallback criteria for missing data
- **Multi-year Support**: Handles current and forecast emission factors
- **Error Handling**: Robust handling of missing or invalid data
- **Multiple Entity Types**: Supports buildings, vehicles, TRUs, industrial, and farm operations
- **Modular Design**: Easy to extend with new emission sources or calculation methods

## Output

The calculator produces a DataFrame with the following columns:
- `operation_id`: Unique identifier for each operation
- `fuel_emissions`: Emissions from fuel consumption (kg CO2e)
- `vehicle_emissions`: Emissions from vehicle operations (kg CO2e)
- `refrigerant_emissions`: Emissions from refrigerant leakage (kg CO2e)
- `livestock_emissions`: Emissions from livestock (kg CO2e)
- `fertilizer_emissions`: Emissions from fertilizers (kg CO2e)
- `waste_emissions`: Emissions from waste (kg CO2e)
- `tru_emissions`: Emissions from TRUs (kg CO2e)
- `total_emissions`: Sum of all emission sources (kg CO2e)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see [License](License.txt) file for details

## Contact

Ola Oguntoye | 15121connect@gmail.com
