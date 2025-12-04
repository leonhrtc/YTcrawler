import tkinter as tk
from tkinter import ttk, messagebox
from crawler import YouTubeCrawler
from exporter import ExcelExporter


class CrawlerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Flydigi & Gamesir YouTube Crawler v5")
        self.window.geometry("820x650")

        # ============ Search Settings ============
        keyword_frame = ttk.LabelFrame(self.window, text="Search Settings")
        keyword_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(keyword_frame, text="Keywords (comma separated):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_keywords = ttk.Entry(keyword_frame, width=50)
        self.entry_keywords.insert(0, "flydigi, gamesir")
        self.entry_keywords.grid(row=0, column=1, padx=5, pady=5)

        # ============ Date Range ============
        ttk.Label(keyword_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", padx=5)
        self.entry_start_date = ttk.Entry(keyword_frame, width=20)
        self.entry_start_date.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(keyword_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5)
        self.entry_end_date = ttk.Entry(keyword_frame, width=20)
        self.entry_end_date.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(keyword_frame, text="OR Days to search:").grid(row=3, column=0, sticky="w", padx=5)
        self.entry_days = ttk.Entry(keyword_frame, width=10)
        self.entry_days.insert(0, "7")
        self.entry_days.grid(row=3, column=1, sticky="w", padx=5)

        # ============ Shorts Toggle ============
        self.include_shorts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(keyword_frame, text="Include Shorts", variable=self.include_shorts_var).grid(
            row=4, column=0, sticky="w", padx=5, pady=5
        )

        # ============ Column Selection ============
        column_frame = ttk.LabelFrame(self.window, text="Select Output Columns")
        column_frame.pack(fill="x", padx=10, pady=10)

        self.col_video_info = tk.BooleanVar(value=True)
        self.col_creator_info = tk.BooleanVar(value=True)

        ttk.Checkbutton(column_frame, text="Video Info", variable=self.col_video_info).grid(
            row=0, column=0, sticky="w", padx=5
        )
        ttk.Checkbutton(column_frame, text="Creator Info", variable=self.col_creator_info).grid(
            row=0, column=1, sticky="w", padx=5
        )

        # ============ Run Button ============
        self.btn_run = ttk.Button(self.window, text="Start Crawling", command=self.start_crawl)
        self.btn_run.pack(pady=10)

        # ============ Messages Output ============
        msg_frame = ttk.LabelFrame(self.window, text="Log Output")
        msg_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_log = tk.Text(msg_frame, height=20)
        self.text_log.pack(fill="both", expand=True)

    def log(self, message):
        self.text_log.insert("end", message + "\n")
        self.text_log.see("end")

    def start_crawl(self):
        keywords = self.entry_keywords.get().strip()
        start_date = self.entry_start_date.get().strip()
        end_date = self.entry_end_date.get().strip()
        days = self.entry_days.get().strip()
        include_shorts = self.include_shorts_var.get()

        output_video_info = self.col_video_info.get()
        output_creator_info = self.col_creator_info.get()

        if not keywords:
            messagebox.showerror("Error", "Please enter keywords.")
            return

        if days:
            try:
                days = int(days)
            except:
                messagebox.showerror("Error", "Days must be a number.")
                return

        self.log("Starting crawler...")

        crawler = YouTubeCrawler(
            keywords=keywords.split(","),
            include_shorts=include_shorts,
            days=days,
            start_date=start_date,
            end_date=end_date,
        )

        results = crawler.run(progress_callback=self.log)

        if not results:
            self.log("No results.")
            return

        exporter = ExcelExporter(
            include_video_info=output_video_info,
            include_creator_info=output_creator_info
        )

        filepath = exporter.export(results)
        self.log(f"Excel saved: {filepath}")
        messagebox.showinfo("Done", f"Excel saved:\n{filepath}")

    def run(self):
        self.window.mainloop()
