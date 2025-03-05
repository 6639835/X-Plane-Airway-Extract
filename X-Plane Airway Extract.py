import csv
import re
from tqdm import tqdm

def load_data(filepath, key_index, value_index, extra_condition_index=None, extra_condition_values=None, type_index=None, type_value=None):
    """
    Loads data from a space-separated file into a dictionary, with optional filtering.

    This function reads a file, splits each line into parts, and creates a dictionary.
    It allows for filtering lines based on values in specified columns.

    Args:
        filepath (str): The path to the input file.
        key_index (int): Index of the column for dictionary keys.
        value_index (int): Index of the column for dictionary values.
        extra_condition_index (int, optional): Index of a column for additional filtering condition.
        extra_condition_values (list of str, optional): Allowed values in the `extra_condition_index` column.
        type_index (int, optional): Index of a column to check for a specific type value.
        type_value (str, optional): Value to match in the `type_index` column.

    Returns:
        dict: A dictionary containing data from the file, filtered as specified.
    """
    data = {}
    try:
        with open(filepath, 'r') as file:
            for line in file:
                parts = line.split()
                if not parts: # Skip empty lines
                    continue
                # Check extra condition if provided
                extra_condition_met = (extra_condition_index is None or
                                       (len(parts) > extra_condition_index and parts[extra_condition_index] in extra_condition_values))
                # Check type condition if provided
                type_condition_met = (type_index is None or
                                      (len(parts) > type_index and parts[type_index] == type_value))

                if extra_condition_met and type_condition_met:
                    if len(parts) > max(key_index, value_index):
                        data[parts[key_index].strip()] = parts[value_index].strip() #strip whitespace for keys and values
    except FileNotFoundError:
        print(f"Error: File not found at path: {filepath}")
        return {} # Return empty dict in case of file not found
    except IndexError:
        print(f"Error: Index out of range while processing file: {filepath}. Check key_index, value_index, etc. against file structure.")
        return {} # Return empty dict in case of index error
    return data

def search_data(waypoint, data_dict):
    """
    Searches for a waypoint in a dictionary and returns its value.

    Args:
        waypoint (str): The key to search for.
        data_dict (dict): The dictionary to search in.

    Returns:
        str or None: The value associated with the waypoint, or None if not found.
    """
    if not waypoint: # Handle empty waypoint string
        return None
    return data_dict.get(waypoint.strip(), None) # strip waypoint to match keys in dict

def sort_key(line):
    """
    Defines a custom sorting key for lines based on the last part, handling alphanumeric sorting.

    This function sorts lines based on the last space-separated part.
    It handles cases where the last part is alphanumeric (e.g., "ABC123") by sorting
    alphabetically by letters and then numerically by numbers.

    Args:
        line (str): A line of text to be sorted.

    Returns:
        tuple: A sorting key tuple for complex sorting.
    """
    parts = line.split()
    if not parts: # Handle empty line case
        return ("", 0) # Return a default sort key for empty lines

    last_part = parts[-1]
    match = re.match(r"([A-Z]+)(\d*)$", last_part)
    if match:
        letters, numbers = match.groups()
        numbers = int(numbers) if numbers else 0
        return (letters, numbers)
    return (last_part, float('inf'))

def get_area_code(waypoint, waypoint_type, earth_fix_data, earth_nav_data):
    """
    Retrieves the area code for a waypoint based on its type and data dictionaries.

    Args:
        waypoint (str): The waypoint identifier.
        waypoint_type (str): The type of waypoint ('DESIGNATED_POINT', 'VORDME', or other).
        earth_fix_data (dict): Dictionary containing earth_fix data.
        earth_nav_data (dict): Dictionary containing earth_nav data.

    Returns:
        tuple: Area code (str) and type code (str), or (None, None) if not found.
    """
    if waypoint_type == 'DESIGNATED_POINT':
        type_code = '11'
        area_data = earth_fix_data
    elif waypoint_type == 'VORDME':
        type_code = '3'
        area_data = earth_nav_data
    else:
        type_code = '2'
        area_data = earth_nav_data # Default to earth_nav_data for other types

    area_code = search_data(waypoint, area_data)
    return area_code, type_code

def convert_csv_to_dat(csv_file, earth_fix_path, earth_nav_path, output_file):
    """
    Converts a CSV file to a DAT format, enriching data with area codes from earth_fix.dat and earth_nav.dat.

    This function reads route segment data from a CSV file, looks up area codes for start and end waypoints
    in `earth_fix.dat` or `earth_nav.dat` based on waypoint types, and writes the processed data to a DAT file.

    Args:
        csv_file (str): Path to the input CSV file.
        earth_fix_path (str): Path to the earth_fix.dat file.
        earth_nav_path (str): Path to the earth_nav.dat file.
        output_file (str): Path to the output DAT file to be created.
    """
    # Load earth_fix.dat and earth_nav.dat into dictionaries
    earth_fix_data = load_data(earth_fix_path, 2, 4, 3, ["ENRT"], 3, "ENRT")
    earth_nav_data = load_data(earth_nav_path, 7, 9, 8, ["ENRT"], 8, "ENRT")

    output_lines = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames is None: # Check if CSV is empty or has no header
                print(f"Warning: CSV file '{csv_file}' is empty or has no header. No data processed.")
                return

            required_headers = ['CODE_POINT_START', 'CODE_TYPE_START', 'CODE_POINT_END', 'CODE_TYPE_END', 'CODE_DIR', 'TXT_DESIG']
            missing_headers = [header for header in required_headers if header not in reader.fieldnames]
            if missing_headers:
                print(f"Error: CSV file '{csv_file}' is missing required headers: {missing_headers}. Please check the CSV file.")
                return

            total_rows = sum(1 for _ in reader) # Efficiently count rows for tqdm
            csvfile.seek(0) # Reset file pointer to the beginning
            next(reader) # Skip header again after counting rows

            for row in tqdm(reader, total=total_rows, desc="Processing Rows"):
                start_waypoint = row['CODE_POINT_START']
                start_waypoint_type = row['CODE_TYPE_START']
                end_waypoint = row['CODE_POINT_END']
                end_waypoint_type = row['CODE_TYPE_END']

                start_area_code, start_type_code = get_area_code(start_waypoint, start_waypoint_type, earth_fix_data, earth_nav_data)
                if not start_area_code:
                    print(f"Warning: No area code found for start waypoint '{start_waypoint}'. Skipping row.")
                    continue

                end_area_code, end_type_code = get_area_code(end_waypoint, end_waypoint_type, earth_fix_data, earth_nav_data)
                if not end_area_code:
                    print(f"Warning: No area code found for end waypoint '{end_waypoint}'. Skipping row.")
                    continue

                direction_code = 'N' if row['CODE_DIR'] == 'X' else row['CODE_DIR']
                designation_text = row['TXT_DESIG']

                for i in range(1, 3): # Loop for creating two output lines
                    dat_line = (
                        f"{start_waypoint:>5}{start_area_code:>3}{start_type_code:>3}{end_waypoint:>6}"
                        f"{end_area_code:>3}{end_type_code:>3}{direction_code:>2}{i:>2}{'0':>4}"
                        f"{'600':>4} {designation_text}\n"
                    )
                    output_lines.append(dat_line)

    except FileNotFoundError:
        print(f"Error: CSV file not found at path: {csv_file}")
        return
    except KeyError as e:
        print(f"Error: Missing column in CSV file: {e}. Please check CSV headers.")
        return
    except Exception as e: # Catch other potential CSV reading errors
        print(f"An unexpected error occurred while processing CSV file: {e}")
        return


    output_lines.sort(key=sort_key)

    try:
        with open(output_file, 'w') as datfile:
            datfile.writelines(output_lines)
    except Exception as e:
        print(f"Error writing to output file '{output_file}': {e}")
        return

    print("Processing completed!")


# Example usage (paths remain unchanged)
csv_file = 'RTE_SEG.csv'
earth_fix_path = 'earth_fix.dat'
earth_nav_path = 'earth_nav.dat'
output_file = 'output.dat'

convert_csv_to_dat(csv_file, earth_fix_path, earth_nav_path, output_file)
