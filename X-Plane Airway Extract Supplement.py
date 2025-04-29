import csv
import re
import os
import logging
import datetime
from tqdm import tqdm
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class NavigationType(Enum):
    DESIGNATED_POINT = ('DESIGNATED_POINT', '11')
    VORDME = ('VORDME', '3')
    NDB = ('NDB', '2')

    def __init__(self, code_type: str, type_code: str):
        self.code_type = code_type
        self.type_code = type_code

@dataclass
class NavigationPoint:
    identifier: str
    type: NavigationType
    area_code: Optional[str] = None

def get_navigation_type(code_type: str) -> Optional[NavigationType]:
    """Get the navigation type from the code type string.
    
    Args:
        code_type: String representing the navigation type code
        
    Returns:
        NavigationType enum if found, None otherwise
    """
    if not code_type:
        logging.error("Empty code type provided")
        return None
        
    for nav_type in NavigationType:
        if nav_type.code_type == code_type:
            return nav_type
    logging.warning(f"Unknown navigation type encountered: {code_type}")
    return None

def process_navigation_point(
    identifier: str,
    code_type: str,
    earth_fix_data: Dict[str, str],
    earth_nav_data: Dict[str, str]
) -> Optional[NavigationPoint]:
    """Process a navigation point and return its details.
    
    Args:
        identifier: The navigation point identifier
        code_type: The type of navigation point
        earth_fix_data: Dictionary of fix point data
        earth_nav_data: Dictionary of navigation point data
        
    Returns:
        NavigationPoint object if valid, None otherwise
    """
    if not identifier:
        logging.error("Empty identifier provided")
        return None
        
    nav_type = get_navigation_type(code_type)
    if not nav_type:
        return None

    # Get area code based on navigation type
    area_code = None
    if nav_type == NavigationType.DESIGNATED_POINT:
        area_code = earth_fix_data.get(identifier)
        if not area_code:
            logging.warning(f"No area code found for fix point {identifier}")
    else:  # VORDME or NDB
        area_code = earth_nav_data.get(identifier)
        if not area_code:
            logging.warning(f"No area code found for {nav_type.code_type} point {identifier}")

    if not area_code:
        return None

    return NavigationPoint(
        identifier=identifier,
        type=nav_type,
        area_code=area_code
    )

def load_fixed_width_data(filepath: str, key_index: int, value_index: int, 
                          extra_condition_index: Optional[int] = None, 
                          extra_condition_values: Optional[Set[str]] = None,
                          type_index: Optional[int] = None, 
                          type_value: Optional[str] = None) -> Dict[str, str]:
    """
    Load data from a fixed-width file into a dictionary.
    
    Args:
        filepath: Path to the data file
        key_index: Column index to use as dictionary key
        value_index: Column index to use as dictionary value
        extra_condition_index: Optional index for filtering data
        extra_condition_values: Set of accepted values for the extra condition
        type_index: Optional index for type filtering
        type_value: Value to match for type filtering
        
    Returns:
        Dictionary mapping keys to values from the specified file
    """
    data = {}
    try:
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            return {}
            
        with open(filepath, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                # Skip header lines that start with 'I' or 'A' (X-Plane format headers)
                if line_num == 1 and (line.startswith('I') or line.startswith('A')):
                    continue
                    
                # Skip terminator lines ("99")
                if line == "99":
                    continue
                    
                parts = line.split()
                if len(parts) <= max(key_index, value_index):
                    logging.warning(f"Line {line_num} has insufficient columns: {line}")
                    continue
                    
                # Check conditions
                condition_met = True
                if extra_condition_index is not None and extra_condition_values is not None:
                    if len(parts) <= extra_condition_index or parts[extra_condition_index] not in extra_condition_values:
                        condition_met = False
                        
                if type_index is not None and type_value is not None:
                    if len(parts) <= type_index or parts[type_index] != type_value:
                        condition_met = False
                
                if condition_met:
                    key = parts[key_index]
                    value = parts[value_index]
                    data[key] = value
                    
        return data
        
    except Exception as e:
        logging.error(f"Error loading data from {filepath}: {str(e)}")
        return {}


def sort_key(line: str) -> tuple:
    """
    Extract sort key from a line based on the last component.
    
    Args:
        line: Text line to analyze
        
    Returns:
        Tuple for sorting (letters, numbers)
        
    Raises:
        ValueError: If the line is empty or invalid
    """
    if not line or not isinstance(line, str):
        raise ValueError("Invalid input: line must be a non-empty string")
        
    parts = line.split()
    if not parts:
        raise ValueError("Empty line provided")
        
    last_part = parts[-1]
    match = re.match(r"([A-Z]+)(\d*)$", last_part)
    if match:
        letters, numbers = match.groups()
        numbers = int(numbers) if numbers else 0
        return (letters, numbers)
    return (last_part, float('inf'))


def get_current_airac_cycle() -> str:
    """
    Get the current AIRAC cycle in YYMM format.
    
    AIRAC cycles follow a 28-day cycle. Each cycle begins exactly 28 days after 
    the previous one, with the first cycle of each year starting in late January.
    
    Returns:
        String representing the current AIRAC cycle (e.g., '2504')
    """
    # AIRAC cycle rules:
    # 1. Each cycle lasts exactly 28 days
    # 2. We can calculate cycles from a known reference date
    
    # Use a known reference cycle as anchor point (2501 = 2025-01-23)
    reference_date = datetime.datetime(2025, 1, 23)
    reference_cycle = 2501
    
    # Get current date
    now = datetime.datetime.now()
    
    # Calculate days since reference date (can be negative if before reference)
    days_diff = (now - reference_date).days
    
    # Calculate cycles since reference (28 days per cycle)
    cycles_diff = days_diff // 28
    
    # Calculate the current cycle number
    current_cycle_num = reference_cycle + cycles_diff
    
    # Format: YYMM where YY=year, MM=sequence within year (01-13)
    year = current_cycle_num // 100
    sequence = current_cycle_num % 100
    
    # Handle year transitions (if needed)
    # If sequence is negative, adjust year and sequence
    if sequence <= 0:
        year -= 1
        sequence += 13
    # If sequence is > 13, adjust year and sequence
    elif sequence > 13:
        year += 1
        sequence -= 13
    
    # Format the cycle as YYMM
    current_cycle = f"{year:02d}{sequence:02d}"
    
    logging.info(f"Calculated AIRAC cycle: {current_cycle} (effective from cycle date)")
    
    return current_cycle

def filter_earth_awy(input_file: str, output_file: str, excluded_areas: Set[str]) -> None:
    """
    Filter out airways where both endpoints are in specified areas.
    
    Args:
        input_file: Path to the original earth_awy.dat file
        output_file: Path to write the filtered file
        excluded_areas: Set of area codes to exclude (e.g., Chinese airspace codes)
        
    Raises:
        FileNotFoundError: If input file is not found
    """
    logging.info(f"Filtering airways from {input_file}...")
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    header_lines = []
    content_lines = []
    has_terminator = False
    filtered_count = 0
    in_header = True  # Flag to track if we're still in the header section
    
    try:
        with open(input_file, 'r', encoding='utf-8') as file_input:
            for line in tqdm(file_input, desc="Filtering Airways"):
                # Preserve header section (everything until we encounter the first valid airway line)
                if in_header:
                    # Check if this might be an airway line (contains at least 11 parts)
                    parts = line.strip().split()
                    if len(parts) >= 11 and not line.startswith('I') and not line.startswith('A'):
                        # This appears to be the first airway line
                        in_header = False
                    else:
                        # Still in header, preserve line
                        header_lines.append(line)
                        continue
                
                # Check for terminator line
                if line.strip() == "99":
                    has_terminator = True
                    continue
                
                # Skip if we're still in header but already handled above
                if in_header:
                    continue
                
                # Process regular content lines
                parts = line.strip().split()
                
                # Skip incomplete lines
                if len(parts) < 11:
                    content_lines.append(line)
                    continue
                
                # Check area codes (positions 1 and 4 in the split line)
                area_start = parts[1]
                area_end = parts[4]
                
                # Filter out if both endpoints are in excluded areas
                if area_start in excluded_areas and area_end in excluded_areas:
                    filtered_count += 1
                    continue
                
                # Keep the line if it doesn't match filter criteria
                content_lines.append(line)
        
        # Write filtered content to output file
        with open(output_file, 'w', encoding='utf-8') as file_output:
            # Write header
            file_output.writelines(header_lines)
            # Write content
            file_output.writelines(content_lines)
            # No terminator line yet - it will be added when new airways are appended
        
        logging.info(f"Filtered {filtered_count} airways from specified areas")
        
    except Exception as e:
        logging.error(f"Error filtering earth_awy.dat: {str(e)}")
        raise

def convert_csv_to_dat(csv_file: str, earth_fix_path: str, earth_nav_path: str, earth_awy_path: str, excluded_areas: Set[str]) -> None:
    """
    Convert navigation data from CSV format to X-Plane DAT format and append to filtered earth_awy.dat.
    
    Args:
        csv_file: Path to input CSV file
        earth_fix_path: Path to earth_fix.dat reference file
        earth_nav_path: Path to earth_nav.dat reference file
        earth_awy_path: Path to earth_awy.dat file to modify
        excluded_areas: Set of area codes to exclude (e.g., Chinese airspace codes)
        
    Raises:
        FileNotFoundError: If any input file is not found
        ValueError: If input files are invalid
    """
    # Validate input files
    for file_path in [csv_file, earth_fix_path, earth_nav_path]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
    
    # Create a temporary file for filtering
    temp_filtered_file = f"{earth_awy_path}.temp"
    
    # Step 1: Filter out airways from excluded areas
    filter_earth_awy(earth_awy_path, temp_filtered_file, excluded_areas)
    
    # Step 2: Load reference data for new airways
    logging.info("Loading reference data...")
    earth_fix_data = load_fixed_width_data(
        earth_fix_path, 2, 4, 3, {"ENRT"}, 3, "ENRT"
    )
    earth_nav_data = load_fixed_width_data(
        earth_nav_path, 7, 9, 8, {"ENRT"}, 8, "ENRT"
    )
    
    if not earth_fix_data or not earth_nav_data:
        raise ValueError("Failed to load reference data")
        
    logging.info(f"Loaded {len(earth_fix_data)} fix points and {len(earth_nav_data)} nav points")
    
    # Step 3: Process CSV and generate new airways
    output_lines = []
    skipped_rows = 0
    processed_rows = 0

    try:
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_fields = {'CODE_POINT_START', 'CODE_TYPE_START', 'CODE_POINT_END', 
                             'CODE_TYPE_END', 'CODE_DIR', 'TXT_DESIG'}
            
            # Validate CSV header
            if not all(field in reader.fieldnames for field in required_fields):
                raise ValueError(f"CSV file missing required fields: {required_fields}")
            
            for row in tqdm(reader, desc="Processing Airways"):
                processed_rows += 1
                
                # Validate required fields
                if not all(row.get(field) for field in required_fields):
                    logging.warning(f"Row {processed_rows} missing required fields")
                    skipped_rows += 1
                    continue
                
                # Process start point
                start_point = process_navigation_point(
                    identifier=row['CODE_POINT_START'],
                    code_type=row['CODE_TYPE_START'],
                    earth_fix_data=earth_fix_data,
                    earth_nav_data=earth_nav_data
                )
                
                if not start_point:
                    skipped_rows += 1
                    continue

                # Use the processed data
                first_part = start_point.identifier
                second_part = start_point.area_code
                third_part = start_point.type.type_code

                # End point processing
                fourth_part = row['CODE_POINT_END']
                
                if row['CODE_TYPE_END'] == 'DESIGNATED_POINT':
                    sixth_part = '11'
                    fifth_part = earth_fix_data.get(fourth_part)
                elif row['CODE_TYPE_END'] == 'VORDME':
                    sixth_part = '3'
                    fifth_part = earth_nav_data.get(fourth_part)
                else:  # Assuming VOR
                    sixth_part = '2'
                    fifth_part = earth_nav_data.get(fourth_part)

                if not fifth_part:
                    logging.warning(f"No area code found for end point {fourth_part}. Skipping row.")
                    skipped_rows += 1
                    continue

                # Direction
                seventh_part = 'N' if row['CODE_DIR'] == 'X' else row['CODE_DIR']
                
                # Fixed values
                ninth_part = '0'
                tenth_part = '600'
                eleventh_part = row['TXT_DESIG']
                
                # Generate both directions of the airway
                for i in range(1, 3):
                    dat_line = (
                        f"{first_part:>5}{second_part:>3}{third_part:>3}{fourth_part:>6}"
                        f"{fifth_part:>3}{sixth_part:>3}{seventh_part:>2}{i:>2}{ninth_part:>4}"
                        f"{tenth_part:>4} {eleventh_part}\n"
                    )
                    output_lines.append(dat_line)

        # Sort new airways
        output_lines.sort(key=sort_key)
        
        # Step 4: Append new airways to filtered file
        with open(temp_filtered_file, 'a', encoding='utf-8') as datfile:
            # Write new airways
            datfile.writelines(output_lines)
            # Add terminator line
            datfile.write("99\n")
            
        # Step 5: Replace original file with updated file
        os.replace(temp_filtered_file, earth_awy_path)

        logging.info(f"Processing completed! Added {len(output_lines)} airway segments to {earth_awy_path}")
        if skipped_rows > 0:
            logging.warning(f"Skipped {skipped_rows} rows due to missing or invalid data")
                
    except Exception as e:
        logging.error(f"Error during processing: {str(e)}")
        raise


if __name__ == "__main__":
    # Define excluded areas (Chinese airspace)
    china_areas = {'ZB', 'ZG', 'ZY', 'ZS', 'ZW', 'ZJ', 'ZP', 'ZL', 'ZH', 'ZU'}
    
    # File paths
    csv_file = 'RTE_SEG.csv'
    earth_fix_path = 'earth_fix.dat'
    earth_nav_path = 'earth_nav.dat'
    earth_awy_path = 'earth_awy.dat'
    
    # Process airway data with filtering
    convert_csv_to_dat(csv_file, earth_fix_path, earth_nav_path, earth_awy_path, china_areas)
