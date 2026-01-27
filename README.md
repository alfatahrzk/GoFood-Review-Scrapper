# 🍔 GoFood Review Intelligence & Scraper

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![Selenium](https://img.shields.io/badge/Scraping-Selenium-green)

An advanced web application to scrape, analyze, and visualize customer reviews from **GoFood** in real-time. This tool helps business owners and data analysts uncover hidden insights, track top-selling menu items, and monitor customer sentiment without manual data entry.

## 🚀 Key Features

* **Dynamic Scraping:** Input any GoFood restaurant URL and scrape reviews instantly.
* **Smart Load More:** Options to scrape a limited number of reviews (Fast) or **ALL** available reviews (Deep Dive).
* **Anti-Ghost Logic:** Automatically filters out duplicate and empty review elements caused by HTML loading glitches.
* **Business Intelligence Dashboard:**
    * **🏆 Top Menu Analysis:** Visualizes the most frequently purchased items based on receipt data.
    * **☁️ Word Cloud:** Identifies trending keywords (complaints or compliments) with slang normalization.
    * **📊 Sentiment Distribution:** Breakdown of customer satisfaction based on ratings.
* **Dynamic Export:** Download clean datasets as CSV with auto-generated filenames based on the restaurant's name.

## 🛠️ Tech Stack

* **Framework:** Streamlit
* **Scraping:** Selenium WebDriver (Headless Chrome)
* **Data Processing:** Pandas, Regex
* **Visualization:** Matplotlib, Seaborn, WordCloud
* **Deployment:** Streamlit Cloud (Linux/Debian environment compatibility)

## 📂 Project Structure

```text
├── app.py                  # Main application source code
├── requirements.txt        # Python dependencies
├── packages.txt            # System dependencies for Streamlit Cloud (Chromium)
├── README.md               # Documentation
└── .gitignore              # Files to ignore in git