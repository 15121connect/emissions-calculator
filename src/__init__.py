"""
Emissions Calculator Package

A Python package for calculating annual greenhouse gas emissions from various operational sources.
"""

from .data_loader import load_data_from_directory
from .lookup import lookup
from .emissions_calculator import calculate_annual_emissions

__version__ = "0.1.0"
__all__ = ['load_data_from_directory', 'lookup', 'calculate_annual_emissions']
