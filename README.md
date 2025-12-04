📌 README.md（英文）
# Flydigi & Gamesir YouTube Crawler (GUI Version)

A Windows-based YouTube crawling tool for monitoring 

This project is ideal for brand analysis, competitor monitoring, and weekly YouTube content tracking.

---

## ⭐ Features

### 🔍 YouTube Data Crawling
- Search YouTube for specific keywords 
- Supports multiple keywords, separated by commas
- Custom **Start Date – End Date** range
- Or use fallback: **search last X days**
- Optional: include or exclude **YouTube Shorts**
- Fetches video and creator metadata

### 📊 Excel Output
Exports results into an Excel file that includes:
- Video title
- Video ID
- Video URL
- Description
- Publish date
- View count
- Channel name
- Channel URL
- Subscriber count
- Country
- Plus: **auto-generated charts**

### 🖥️ GUI Interface
- Built with Tkinter + ttk widgets
- Settings panel with clean alignment
- Real-time log panel
- Form options:
  - Keywords
  - API Key
  - Include Shorts
  - Search Days (fallback)
  - Custom Start Date / End Date
  - Select which categories to export (video / creator data)

### ⚙️ Modular Structure
The project is split into separate files:
- `main.py` – entry point
- `ui.py` – GUI interface
- `crawler.py` – YouTube API logic
- `excel_export.py` – Excel writer and chart generator

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt

2. Set Up YouTube API

You will need a YouTube Data API v3 Key.
Create one at:

https://console.cloud.google.com/apis/credentials

Then paste your API key into the GUI field.

▶️ Run the Application
python main.py

📁 Output

Each crawl generates:

/output/YYYY-MM-DD_keyword_report.xlsx


With:

Raw video data

Raw creator data

Charts (e.g., view distribution)

📦 Folder Structure
project/
│
├── main.py
├── ui.py
├── crawler.py
├── excel_export.py
├── requirements.txt
└── README.md

⚠️ Notes

This tool uses the official YouTube API
→ your daily quota (10,000 units/day) applies

YouTube search returns up to 50 results per request

Avoid frequent crawling to prevent exhausting your quota
