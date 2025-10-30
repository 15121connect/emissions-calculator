"""
Executable script to calculate annual emissions from operational data.

This script:
1. Loads all CSV files from the data/raw/ directory
2. Calculates annual emissions using the emissions calculator
3. Saves results to data/outputs/annual_emissions.csv

Usage:
    python scripts/calculate_emissions.py
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_loader import load_data_from_directory
from src.emissions_calculator import calculate_annual_emissions


def main():
    """Main execution function."""
    
    # Define paths
    data_dir = project_root / 'data' / 'raw'
    output_dir = project_root / 'data' / 'outputs'
    output_file = output_dir / 'annual_emissions.csv'
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Annual Emissions Calculator")
    print("=" * 60)
    print()
    
    # Load data
    print(f"Loading CSV files from: {data_dir}")
    print()
    dataframes = load_data_from_directory(str(data_dir))
    print()
    print(f"Loaded {len(dataframes)} data files")
    print()
    
    # Validate required dataframes
    required_dataframes = [
        'operation_data_test_2',
        'fuel_data',
        'refrigerant_gwp',
        'refrigerator_data',
        'vehicle_interventions',
        'vehicle_interventions_tru',
        'farm_emissions'
    ]
    
    missing = [df for df in required_dataframes if df not in dataframes]
    if missing:
        print(f"ERROR: Missing required data files: {missing}")
        print("Please ensure all required CSV files are in the data/raw/ directory.")
        sys.exit(1)
    
    # Calculate emissions
    print("Calculating annual emissions...")
    print()
    annual_emissions = calculate_annual_emissions(
        dataframes['operation_data_test_2'],
        dataframes['fuel_data'],
        dataframes['refrigerant_gwp'],
        dataframes['refrigerator_data'],
        dataframes['vehicle_interventions'],
        dataframes['vehicle_interventions_tru'],
        dataframes['farm_emissions']
    )
    
    # Save results
    print()
    print(f"Saving results to: {output_file}")
    annual_emissions.to_csv(output_file, index=False)
    
    # Display summary
    print()
    print("=" * 60)
    print("Calculation Summary")
    print("=" * 60)
    print(f"Total operations processed: {len(annual_emissions)}")
    print(f"Total emissions (kg CO2e): {annual_emissions['total_emissions'].sum():,.2f}")
    print()
    print("Results preview:")
    print(annual_emissions.head())
    print()
    print("Calculation complete!")


if __name__ == "__main__":
    main()
