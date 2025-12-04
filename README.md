# Flydigi & Gamesir YouTube Crawler (GUI Version)

A Windows-based YouTube crawling tool for monitoring Flydigi and Gamesir brand videos.

This project is ideal for brand analysis, competitor monitoring, and weekly YouTube content tracking.

---

## ⭐ Features

### 🔍 YouTube Data Crawling

* Search YouTube for specific keywords
* Supports multiple keywords, separated by commas
* Custom **Start Date – End Date** range
* Or use fallback: **search last X days**
* Choose video type: **All / Shorts / Long videos**
* Fetches video and creator metadata
* Handles total views, likes, comments, duration, and more

### 📊 Excel Output

Exports results into an Excel file that includes:

* Video title
* Video ID
* Video URL
* Description
* Publish date
* Duration
* View count
* Like count
* Comment count
* Channel name
* Channel URL
* Subscriber count
* Country
* Plus: **auto-generated charts**

  * Total Views per keyword
  * Average Views per keyword

### 🖥️ GUI Interface

* Built with Tkinter + ttk widgets
* Clean left-aligned settings panel
* Real-time log panel
* Form options:

  * Keywords
  * API Key
  * Video Type (All / Shorts / Long)
  * Search Days (fallback)
  * Custom Start Date / End Date
  * Select which categories to export (video / creator data)

### ⚙️ Modular Structure

The project is split into separate files:

* `main.py` – entry point
* `ui.py` – GUI interface
* `crawler.py` – YouTube API logic
* `exporter.py` – Excel writer and chart generator

---

## 🚀 Getting Started

1. Install Dependencies

```bash
pip install -r requirements.txt
```

2. Set Up YouTube API

You will need a YouTube Data API v3 Key.
Create one at:

[https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)

Then paste your API key into the GUI field.

---

### ▶️ Run the Application

```bash
python main.py
```

---

## 📁 Output

Each crawl generates an Excel file:

```
yt_report_YYYYMMDD_HHMMSS.xlsx
```

With:

* Raw video data
* Raw creator data
* Charts (Total Views & Average Views per keyword)

---

## 📦 Folder Structure

```
project/
│
├── main.py
├── ui.py
├── crawler.py
├── exporter.py
├── requirements.txt
└── README.md
```

---

## ⚠️ Notes

* This tool uses the official YouTube Data API → your daily quota (10,000 units/day) applies
* YouTube search returns up to 50 results per request
* Avoid frequent crawling to prevent exhausting your quota
