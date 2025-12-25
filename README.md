# CNKI Research Funding Web Scraper

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Playwright](https://img.shields.io/badge/Playwright-Latest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

An automated web scraping tool for collecting research funding project data from CNKI (China National Knowledge Infrastructure) database. Built with Playwright for reliable browser automation and data extraction.

[中文文档](README_CN.md) | [English](README.md)

## ✨ Features

- 🤖 **Full Browser Automation** - Automated data collection with Playwright
- 🔐 **Manual Login Support** - Pause for IP authentication and filter configuration
- 📊 **Smart Data Extraction** - Extract data from both list pages and detail pages
- 🔗 **URL Preservation** - Automatically save detail page URLs for traceability
- 📅 **Date Recognition** - Intelligent recognition of multiple date formats
- 🔄 **Auto Pagination** - Automatically navigate through all pages
- 📝 **Direct URL Scraping** - Scrape projects directly from URLs in a text file
- 💾 **Excel Export** - Export data to Excel format for easy analysis
- ⚠️ **Error Handling** - Robust error handling and partial data saving

## 📋 Requirements

- Python 3.7+
- Google Chrome or Chromium-based browser
- Stable internet connection

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/wangxz01/cnki-fund-scraper.git
cd cnki-fund-scraper
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browser Driver

```bash
python -m playwright install chromium
```

### 4. Run the Scraper

#### Option 1: Standard Scraping (From List Pages)
```bash
python scraper.py
```

#### Option 2: Direct URL Scraping (From Text File)
1. Create or edit `url.txt` file with project URLs (one per line)
2. Run the direct scraper:
```bash
python scraper2.py
```

## 📖 Usage Guide

### Step-by-Step Process

1. **Launch Script**: Run `python scraper.py`
2. **Browser Opens**: The script automatically opens Chrome and navigates to CNKI
3. **Manual Setup**:
   - Click "IP Login" in the browser
   - Set your desired filters
   - Ensure the page is fully loaded
4. **Start Scraping**: Press `Enter` in the terminal to begin automatic scraping
5. **Automatic Process**:
   - Reads all projects on the current page
   - Clicks each project title
   - Extracts detailed information from the new tab
   - Closes the detail page and returns to the list
   - Clicks "Next Page" to continue
6. **Data Export**: Data is automatically saved as an Excel file upon completion

## 📊 Output Data Structure

The generated Excel file contains the following fields:

| Field | Description |
|-------|-------------|
| Page Number | Page number where data was found |
| Index | Project index on current page |
| List Page Title | Project title from list page |
| **List Page Start Date** | **Start date extracted from list page** |
| **Detail Page URL** | **Complete URL of project detail page** |
| Project Title | Full project title from detail page |
| Project Status | Project status (Active/Completed) |
| Start Date | Project start date from detail page |
| Country/Region | Project country or region |
| Funding Agency | Name of funding organization |
| Funding Amount | Amount of funding |
| Project Type | Type of project |
| Host Institution | Institution hosting the project |
| Project Members | Project team members |
| Project Number | Project identification number |
| Project Source | Project source link |

## ⚙️ Advanced Configuration

### Limit Number of Pages

Edit the `main()` function in `scraper.py`:

```python
# Scrape only the first 5 pages
scraper.run(max_pages=5, headless=False)
```

### Run in Headless Mode

```python
# Run without displaying browser window
scraper.run(max_pages=None, headless=True)
```

### Customize Selectors

If the webpage structure changes, modify the selectors in `scraper.py`:

```python
# In scrape_page() method
title_links = page.query_selector_all('your-selector')

# In click_next_page() method
next_button = page.query_selector('your-next-button-selector')
```

## 🔧 Troubleshooting

### Issue 1: Cannot Find Title Links

**Cause**: Webpage structure doesn't match preset selectors

**Solution**:
1. Press F12 in browser to open developer tools
2. Inspect the HTML structure of project titles
3. Update the `title_links` selector in `scraper.py`

### Issue 2: Cannot Click Next Page

**Cause**: Incorrect next page button selector

**Solution**:
1. Inspect the "Next Page" button HTML structure
2. Update the selector in `click_next_page()` method

### Issue 3: Incomplete Data Extraction

**Cause**: Detail page field selectors are inaccurate

**Solution**:
1. Open a detail page and inspect the data field HTML structure
2. Update the extraction logic in `extract_detail_data()` method

### Issue 4: Scraping Interrupted

**Cause**: Network issues or page load timeout

**Solution**:
- The script automatically saves collected data to `cnki_projects_partial.xlsx`
- Manually adjust timeout settings:

```python
page.wait_for_load_state('networkidle', timeout=30000)  # 30 seconds
```

## ⚠️ Important Notes

1. **Respect Website Terms**: Please comply with CNKI's terms of service and robots.txt
2. **Rate Limiting**: Avoid excessive requests; the script includes built-in delays
3. **Educational Use**: Scraped data is for personal learning and research only
4. **Network Stability**: Ensure stable internet connection to avoid interruptions
5. **Browser Version**: Ensure Chromium browser driver is correctly installed

## 🛠️ Tech Stack

- **Python 3.7+**
- **Playwright**: Browser automation
- **Pandas**: Data processing
- **OpenPyXL**: Excel file operations

## 📁 Project Structure

```
cnki-fund-scraper/
├── scraper.py          # Main scraper script (from list pages)
├── scraper2.py         # Direct URL scraper script (from url.txt)
├── url.txt             # Project URLs for direct scraping
├── requirements.txt    # Python dependencies
├── README.md           # English documentation
├── README_CN.md        # Chinese documentation
├── .gitignore          # Git ignore rules
└── LICENSE             # MIT License
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to [Playwright](https://playwright.dev/) for the powerful browser automation framework
- Thanks to CNKI for providing valuable research funding data

## 📧 Contact

If you have any questions or suggestions, please open an issue on GitHub.

---

**Note**: This tool is for educational and research purposes only. Please use responsibly and in accordance with applicable laws and website terms of service.
