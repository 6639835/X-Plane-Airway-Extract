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
    with open(filepath, 'r') as file:
        for line in file:
            parts = line.split()
            if (extra_condition_index is None or (len(parts) > extra_condition_index and parts[extra_condition_index] in extra_condition_values)) and \
               (type_index is None or (len(parts) > type_index and parts[type_index] == type_value)):
                if len(parts) > max(key_index, value_index):
                    data[parts[key_index]] = parts[value_index]
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
    return data_dict.get(waypoint, None)

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
    last_part = line.split()[-1]
    match = re.match(r"([A-Z]+)(\d*)$", last_part)
    if match:
        letters, numbers = match.groups()
        numbers = int(numbers) if numbers else 0
        return (letters, numbers)
    return (last_part, float('inf'))

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

    with open(csv_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        total_rows = sum(1 for _ in reader)
        csvfile.seek(0)
        next(reader)

        for row in tqdm(reader, total=total_rows, desc="Processing Rows"):
            first_part = row['CODE_POINT_START']
            third_part = '11' if row['CODE_TYPE_START'] == 'DESIGNATED_POINT' else '3' if row['CODE_TYPE_START'] == 'VORDME' else '2'
            second_part = search_data(first_part, earth_fix_data if third_part == '11' else earth_nav_data)

            if not second_part:
                print(f"Warning: No area code found for {first_part}. Skipping row.")
                continue

            fourth_part = row['CODE_POINT_END']
            sixth_part = '11' if row['CODE_TYPE_END'] == 'DESIGNATED_POINT' else '3' if row['CODE_TYPE_END'] == 'VORDME' else '2'
            fifth_part = search_data(fourth_part, earth_fix_data if sixth_part == '11' else earth_nav_data)

            if not fifth_part:
                print(f"Warning: No area code found for {fourth_part}. Skipping row.")
                continue

            seventh_part = 'N' if row['CODE_DIR'] == 'X' else row['CODE_DIR']
            ninth_part = '0'
            tenth_part = '600'
            eleventh_part = row['TXT_DESIG']

            for i in range(1, 3):
                dat_line = (
                    f"{first_part:>5}{second_part:>3}{third_part:>3}{fourth_part:>6}"
                    f"{fifth_part:>3}{sixth_part:>3}{seventh_part:>2}{i:>2}{ninth_part:>4}"
                    f"{tenth_part:>4} {eleventh_part}\n"
                )
                output_lines.append(dat_line)

    output_lines.sort(key=sort_key)

    with open(output_file, 'w') as datfile:
        datfile.writelines(output_lines)

    print("Processing completed!")


# Example usage (paths remain unchanged)
csv_file = '/RTE_SEG.csv'
earth_fix_path = 'earth_fix.dat'
earth_nav_path = 'earth_nav.dat'
output_file = 'output.dat'

convert_csv_to_dat(csv_file, earth_fix_path, earth_nav_path, output_file)
