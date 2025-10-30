"""
Generic lookup function for querying DataFrames with flexible criteria.

This module provides a robust lookup system with support for:
- Multiple search criteria
- Comparison operators (>, <, >=, <=, =)
- Fallback criteria for alternative searches
- Multiple output formats (DataFrame or list of dictionaries)
"""

import pandas as pd


def lookup(df, criteria, output_columns=None, output_format='dictionary_list', fallback_criteria=None):
    """
    Looks up values in a DataFrame based on multiple criteria with fallback support.
    
    Args:
        df (pd.DataFrame): The input DataFrame to search.
        criteria (dict): Dictionary specifying the initial search conditions.
                        - Simple format: {'column': value} for equality
                        - Operator format: {'column': (operator, value)} for comparisons
                        - Operators: '>', '<', '>=', '<=', '='
        output_columns (list, optional): List of column names to include in output.
                                        If None, all columns are included.
        output_format (str): Desired output format:
                            - 'dataframe': Returns a pandas DataFrame
                            - 'dictionary_list': Returns a list of dictionaries (default)
        fallback_criteria (list, optional): List of dictionaries with fallback criteria.
                                           Each dict contains columns to update in the
                                           original criteria if no results are found.
    
    Returns:
        pd.DataFrame or list: Matching data based on output_format.
                             Returns empty DataFrame or empty list if no matches found.
    
    Examples:
        >>> # Simple equality lookup
        >>> lookup(df, {'fuel_type': 'Diesel'}, output_columns=['emission_factor'])
        [{'emission_factor': 2.68}]
        
        >>> # Lookup with comparison operator
        >>> lookup(df, {'year': ('>=', 2020)}, output_format='dataframe')
        
        >>> # Lookup with fallback
        >>> lookup(df, 
        ...        {'state': 'CA', 'year': 2024},
        ...        fallback_criteria=[{'state': 'Any'}])
    """
    try:
        print(f"lookup called with criteria: {criteria}")
        
        # Initial search using primary criteria
        result = _perform_lookup(df, criteria, output_columns, output_format)
        if result:
            return result
        
        # If no results and fallback criteria provided, attempt fallback searches
        if fallback_criteria:
            for criteria_update in fallback_criteria:
                updated_criteria = criteria.copy()
                updated_criteria.update(criteria_update)
                print(f"Applying fallback criteria: {updated_criteria}")
                result = _perform_lookup(df, updated_criteria, output_columns, output_format)
                if result:
                    return result
        
        # If no results after fallback, return empty result
        print("No matching data found.")
        return pd.DataFrame() if output_format == 'dataframe' else []
        
    except (KeyError, IndexError, TypeError, ValueError) as e:
        print(f"Error during lookup: {e}")
        return pd.DataFrame() if output_format == 'dataframe' else []


def _perform_lookup(df, criteria, output_columns, output_format):
    """
    Internal function to perform the actual lookup based on criteria.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        criteria (dict): Dictionary specifying the search conditions.
        output_columns (list): List of column names to include in output.
        output_format (str): Desired output format.
    
    Returns:
        pd.DataFrame or list or None: Matching data or None if no matches found.
    """
    # Data validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")
    if not isinstance(criteria, dict):
        raise TypeError("Input 'criteria' must be a dictionary.")
    
    # Initialize mask as True for all rows
    combined_mask = pd.Series([True] * len(df), index=df.index)
    
    # Apply criteria
    for col, criteria_value in criteria.items():
        if isinstance(criteria_value, tuple):
            # Handle tuple criteria (operator, value) format
            if len(criteria_value) == 3:
                # Flexible format: (operation_row_column, operator, value)
                operation_row_col, operator, value = criteria_value
                col = operation_row_col
            elif len(criteria_value) == 2:
                # Standard format: (operator, value)
                operator, value = criteria_value
            else:
                raise ValueError(f"Invalid criteria format for column '{col}'.")
            
            # Apply operator
            if operator == '>':
                criteria_mask = df[col] > value
            elif operator == '<':
                criteria_mask = df[col] < value
            elif operator == '>=':
                criteria_mask = df[col] >= value
            elif operator == '<=':
                criteria_mask = df[col] <= value
            elif operator == '=':
                criteria_mask = df[col] == value
            else:
                raise ValueError(f"Invalid operator '{operator}' for column '{col}'.")
        else:
            # Simple equality check
            criteria_mask = df[col] == criteria_value
        
        # Combine with overall mask
        combined_mask &= criteria_mask
    
    # Filter rows
    matched_rows = df[combined_mask]
    
    if output_format == 'dataframe':
        # Return DataFrame
        if output_columns is None:
            print(f"lookup returning: {matched_rows}")
            return matched_rows
        else:
            if any(isinstance(col, slice) for col in output_columns):
                print(f"lookup returning columns: {matched_rows.loc[:, output_columns]}")
                return matched_rows.loc[:, output_columns]
            else:
                print(f"lookup returning columns: {matched_rows[output_columns]}")
                return matched_rows[output_columns]
    
    elif output_format == 'dictionary_list':
        # Return list of dictionaries
        intervention_data = []
        if matched_rows.shape[0] > 0:
            for _, row in matched_rows.iterrows():
                if output_columns is None:
                    intervention_data.append(row.to_dict())
                else:
                    intervention_data.append({key: row[key] for key in output_columns})
        print(f"lookup returning: {intervention_data}")
        return intervention_data
    
    else:
        raise ValueError("Invalid 'output_format' specified. Use 'dataframe' or 'dictionary_list'.")
