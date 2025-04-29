# ✈️ X-Plane Airway Converter

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

**Transform your CSV navigation data into perfect X-Plane DAT files with automatic area code magic! ✨**

A powerful utility that saves X-Plane enthusiasts countless hours by automating the tedious process of creating properly formatted airway files. Say goodbye to manual area code lookups forever!

## 📋 Table of Contents

- [🚀 Introduction](#-introduction)
- [✨ Features](#-features)
- [📥 Installation](#-installation)
- [🔧 Usage](#-usage)
- [📊 Data Formats](#-data-formats)
- [📝 Examples](#-examples)
- [❓ FAQ](#-faq)
- [👥 Contributing](#-contributing)
- [📜 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [🔍 Troubleshooting](#-troubleshooting)
- [📞 Contact](#-contact)

## 🚀 Introduction

Creating custom airways for X-Plane has traditionally been a tedious process requiring manual area code lookups and careful formatting. This tool revolutionizes your workflow by:

1. 📚 Reading your route segment data from CSV files
2. 🔍 Automatically resolving area codes from X-Plane's navigation data files
3. ✅ Validating data integrity with comprehensive error checking
4. 📊 Displaying real-time progress for large datasets
5. 📝 Generating perfectly formatted DAT files ready for immediate use in X-Plane

Save hours of manual work and eliminate frustrating errors with this streamlined conversion utility!

> "This tool saved me countless hours of tedious work creating custom airways for my virtual airline routes." - X-Plane Enthusiast

## ✨ Features

- **🔄 CSV to DAT Conversion**: Transform complex CSV route segment data into X-Plane DAT files with a single command
- **🧠 Intelligent Area Code Resolution**: Automatically extracts area codes from `earth_fix.dat` and `earth_nav.dat` reference files
- **🛡️ Robust Data Validation**: Comprehensive error checking with detailed logging for easy troubleshooting
- **📈 Progress Visualization**: Real-time progress display for large datasets using the slick tqdm library
- **📊 Smart Output Organization**: Automatically sorts airway data for optimal X-Plane performance
- **📝 Perfect X-Plane Formatting**: Includes all required headers and terminators in the output files
- **🎯 High Performance**: Efficiently processes thousands of route segments in seconds

## 📥 Installation

### Requirements

- 🐍 Python 3.8 or higher
- 📦 pip package manager
- 📊 tqdm library for progress visualization

### Setup

1. Clone the repository (optional):
   ```bash
   git clone https://github.com/6639835/X-Plane-Airway-Extract.git
   cd X-Plane-Airway-Extract
   ```

2. Install the required dependencies:
   ```bash
   pip install tqdm
   ```

That's it! No complex configuration needed - you're ready to start converting airways!

## 🔧 Usage

### Basic Usage

1. Prepare your CSV file with the following columns:
   - `CODE_POINT_START` - Starting waypoint identifier (e.g., "EDDF")
   - `CODE_TYPE_START` - Starting waypoint type (e.g., "DESIGNATED_POINT", "VORDME", etc.)
   - `CODE_POINT_END` - Ending waypoint identifier (e.g., "EDDT")
   - `CODE_TYPE_END` - Ending waypoint type
   - `CODE_DIR` - Direction code (e.g., "N", "E", "W", "S", "X")
   - `TXT_DESIG` - Airway designator (e.g., "Q123")

2. Run the script:
   ```bash
   python X-Plane-Airway.py
   ```

3. Watch the magic happen! The script will:
   - Load reference data
   - Process your routes with a slick progress bar
   - Generate a perfectly formatted X-Plane DAT file

### Advanced Configuration

Customize the script by modifying these path variables:

```python
csv_file = '/path/to/your/RTE_SEG.csv'               # Your input CSV file
earth_fix_path = '/path/to/your/earth_fix.dat'       # Earth fix reference file
earth_nav_path = '/path/to/your/earth_nav.dat'       # Earth nav reference file
output_file = '/path/to/your/output.dat'             # Where to save the result
```

**Pro Tip**: The `earth_fix.dat` and `earth_nav.dat` files can be found in your X-Plane installation directory, typically under `/X-Plane 12/Custom Data/` or `/X-Plane 11/Custom Data/`.

## 📊 Data Formats

### Input CSV Format

Your CSV should contain these columns (order matters!):

```
CODE_POINT_START,CODE_TYPE_START,CODE_POINT_END,CODE_TYPE_END,CODE_DIR,TXT_DESIG
EDDF,DESIGNATED_POINT,EDDT,DESIGNATED_POINT,N,Q123
EDDT,DESIGNATED_POINT,EDDH,DESIGNATED_POINT,N,Q123
```

### Output DAT Format

The generated DAT file follows X-Plane's exact specifications:

```
I
1100 Version - data cycle 2504, build 20250429, metadata AwyXP1100. Copyright (c) 2024 Justin

EDDF DT 11 EDDT DT 11 N 1  0 600 Q123
EDDT DT 11 EDDH DT 11 N 1  0 600 Q123
99
```

### Reference DAT Files

The tool needs these X-Plane reference files:
- `earth_fix.dat` - Contains fix points and their area codes
- `earth_nav.dat` - Contains navigation aids and their area codes

## 📝 Examples

### Basic Conversion Example

```bash
# Assuming files are in their default locations
python X-Plane-Airway.py

# Console output:
# 2025-04-29 10:15:23 - INFO - Loaded 80171 fix points and 4907 nav points
# Processing Rows: 100%|██████████| 5280/5280 [00:08<00:00, 632.50it/s]
# 2025-04-29 10:15:32 - INFO - Processing completed! Wrote 10558 lines to /path/to/output.dat
```

### Custom Paths Example

```python
# Modify these lines in the script:
csv_file = '/Users/pilot/Documents/navdata/my_airways.csv'
earth_fix_path = '/Applications/X-Plane 12/Custom Data/earth_fix.dat'
earth_nav_path = '/Applications/X-Plane 12/Custom Data/earth_nav.dat'
output_file = '/Users/pilot/Documents/navdata/custom_airways.dat'
```

## ❓ FAQ

### How do I find the area codes for my waypoints?
You don't need to! That's the beauty of this tool - it automatically extracts the area codes from X-Plane's navigation data files.

### Can I convert multiple CSV files at once?
Currently, the tool processes one CSV file at a time. For multiple files, you would need to run the script multiple times with different input/output paths.

### What if some waypoints don't have area codes?
The tool will log warnings about missing area codes and skip those route segments. Check your CSV for typos or verify that the waypoints exist in your X-Plane navigation data.

### Can I use this with older X-Plane versions?
Yes! The tool is compatible with X-Plane 11 and 12, as long as you have the appropriate `earth_fix.dat` and `earth_nav.dat` files.

### How large a CSV file can I process?
The tool has been tested with CSV files containing over 10,000 route segments. Processing time depends on your computer's specifications, but it's typically very fast.

## 👥 Contributing

Contributions are enthusiastically welcomed! Here's how to help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-new-feature`)
3. 💻 Implement your changes
4. ✅ Commit your improvements (`git commit -am 'Add some amazing feature'`)
5. 📤 Push to the branch (`git push origin feature/amazing-new-feature`)
6. 🔄 Open a Pull Request

### Contribution Guidelines

- Follow PEP 8 style guidelines for clean, readable code
- Include helpful comments for complex sections
- Write clear commit messages that explain your changes
- Add tests for new features when possible
- Update documentation to reflect your changes

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- 🎮 Laminar Research for creating X-Plane and documenting the navigation data formats
- 📊 [tqdm](https://pypi.org/project/tqdm/) library creators for the awesome progress bar functionality
- 🌐 The X-Plane community for inspiration and support
- 💻 Open source contributors who make projects like this possible

## 🔍 Troubleshooting

### Common Issues and Solutions

#### "File Not Found" Errors
- Double-check all file paths in the script
- Verify that the files actually exist at those locations
- Make sure you have read/write permissions for those directories

#### "KeyError in CSV" Errors
- Ensure your CSV headers exactly match the required column names
- Check for hidden characters or spaces in your CSV headers
- Verify that your CSV is properly formatted (try opening it in a text editor)

#### "Missing Area Codes" Warnings
- Check for typos in waypoint identifiers
- Verify that the waypoints exist in your X-Plane navigation data
- Make sure you're using the correct `earth_fix.dat` and `earth_nav.dat` files for your region

#### Performance Issues
- For very large CSV files, ensure your computer has sufficient memory
- Close other memory-intensive applications while running the script
- If processing is slow, consider splitting your CSV into smaller files

### Getting More Help

If you're still experiencing issues:
1. Check the log output for specific error messages
2. Review the script comments for additional guidance
3. Contact the developer using the information below

## 📞 Contact

For support, questions, or just to share your success stories:

- ✉️ Email: [6639835@gmail.com](mailto:6639835@gmail.com)
- 🌐 GitHub: [Open an Issue](https://github.com/6639835/X-Plane-Airway-Extract/issues)
- 🛫 X-Plane Forums: [Discuss the tool](https://forums.x-plane.org/)

---

<p align="center">
  <i>Happy Flying!</i>
</p>
