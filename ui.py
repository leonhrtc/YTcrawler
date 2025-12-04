# ui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
from tkcalendar import DateEntry
import threading
from crawler import YouTubeCrawler
from exporter import ExcelExporter
from config import YOUTUBE_API_KEY
from datetime import datetime

class CrawlerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Flydigi & Gamesir Crawler — v6")
        self.root.geometry("920x720")
        self.stop_event = threading.Event()
        self._build_ui()

    def _build_ui(self):
        padx=8; pady=6
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=10)

        row = 0
        ttk.Label(frame, text="Keywords (comma separated):").grid(row=row, column=0, sticky="w", padx=padx, pady=pady)
        self.entry_keywords = ttk.Entry(frame, width=60)
        self.entry_keywords.grid(row=row, column=1, columnspan=3, sticky="w")
        self.entry_keywords.insert(0, "flydigi, gamesir")

        row += 1
        self.var_use_date = tk.IntVar(value=0)
        ttk.Checkbutton(frame, text="Enable Date Range", variable=self.var_use_date).grid(
            row=row, column=0, sticky="w", padx=padx
        )

        row +=1

        ttk.Label(frame, text="Start Date:").grid(row=row, column=0, sticky="w", padx=padx)
        self.date_start = DateEntry(frame, width=16, background='darkblue', foreground='white', borderwidth=1)
        self.date_start.grid(row=row, column=1, sticky="w", padx=padx)

        ttk.Label(frame, text="End Date:").grid(row=row, column=2, sticky="w", padx=padx)
        self.date_end = DateEntry(frame, width=16, background='darkblue', foreground='white', borderwidth=1)
        self.date_end.grid(row=row, column=3, sticky="w", padx=padx)

        row+=1
        ttk.Label(frame, text="Or Days to search (if no date range):").grid(row=row, column=0, sticky="w", padx=padx)
        self.entry_days = ttk.Entry(frame, width=8)
        self.entry_days.grid(row=row, column=1, sticky="w", padx=padx)
        self.entry_days.insert(0, "7")

        row+=1
        self.var_shorts = tk.IntVar(value=1)
        ttk.Checkbutton(frame, text="Include Shorts", variable=self.var_shorts).grid(row=row, column=0, sticky="w", padx=padx)

        ttk.Label(frame, text="YouTube API Key:").grid(row=row, column=1, sticky="w", padx=padx)
        self.entry_api = ttk.Entry(frame, width=48)
        self.entry_api.grid(row=row, column=2, columnspan=2, sticky="w", padx=padx)
        self.entry_api.insert(0, YOUTUBE_API_KEY if YOUTUBE_API_KEY else "")

        row+=1
        ttk.Label(frame, text="Output mode:").grid(row=row, column=0, sticky="w", padx=padx)
        self.output_mode = tk.StringVar(value="both")
        ttk.Radiobutton(frame, text="Merged sheet", variable=self.output_mode, value="merged").grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(frame, text="Separate sheets", variable=self.output_mode, value="separate").grid(row=row, column=2, sticky="w")
        ttk.Radiobutton(frame, text="Both", variable=self.output_mode, value="both").grid(row=row, column=3, sticky="w")

        row+=1
        ttk.Label(frame, text="Select output content:").grid(row=row, column=0, sticky="w", padx=padx)
        self.var_video_info = tk.IntVar(value=1)
        self.var_channel_info = tk.IntVar(value=1)
        ttk.Checkbutton(frame, text="Video Info", variable=self.var_video_info).grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(frame, text="Creator Info", variable=self.var_channel_info).grid(row=row, column=2, sticky="w")

        row+=1
        ttk.Label(frame, text="Output Excel:").grid(row=row, column=0, sticky="w", padx=padx)
        self.entry_out = ttk.Entry(frame, width=60)
        self.entry_out.grid(row=row, column=1, columnspan=2, sticky="w")
        self.entry_out.insert(0, f"yt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        ttk.Button(frame, text="Browse...", command=self._choose_file).grid(row=row, column=3, sticky="w")

        row+=1
        self.btn_start = ttk.Button(frame, text="Start", command=self.start)
        self.btn_start.grid(row=row, column=1, sticky="w", pady=8)
        self.btn_stop = ttk.Button(frame, text="Stop", command=self.stop, state="disabled")
        self.btn_stop.grid(row=row, column=2, sticky="w", pady=8)
        self.btn_check_key = ttk.Button(frame, text="Check API Key", command=self.check_api_key)
        self.btn_check_key.grid(row=row, column=3, sticky="w", pady=8)

        # progress
        row+=1
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=880, mode="determinate")
        self.progress.pack(padx=10, pady=(2,10))

        # log
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=6)
        self.log_box = tk.Text(log_frame, height=22)
        self.log_box.pack(fill="both", expand=True)

    def _choose_file(self):
        p = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files","*.xlsx")])
        if p:
            self.entry_out.delete(0, tk.END)
            self.entry_out.insert(0, p)

    def _log(self, msg):
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        def append():
            self.log_box.insert("end", f"[{ts}] {msg}\n")
            self.log_box.see("end")
        self.root.after(0, append)

    def check_api_key(self):
        key = self.entry_api.get().strip()
        if not key:
            messagebox.showwarning("API Key", "Please enter API key to check.")
            return
        # do a quick test search (safe)
        params = {"part":"snippet","q":"test","maxResults":1,"type":"video","key":key}
        try:
            r = requests.get(f"https://www.googleapis.com/youtube/v3/search", params=params, timeout=8)
            if r.status_code == 200:
                messagebox.showinfo("API Key", "API Key looks valid (search OK).")
            else:
                messagebox.showerror("API Key", f"Key invalid or quota issue: {r.status_code}\n{r.text}")
        except Exception as e:
            messagebox.showerror("API Key", f"Request error: {e}")

    def start(self):
        # gather inputs
        keywords = [k.strip() for k in self.entry_keywords.get().split(",") if k.strip()]
        if not keywords:
            messagebox.showwarning("Input", "Please provide keywords.")
            return
        start_date = self.date_start.get_date().isoformat()
        end_date = self.date_end.get_date().isoformat()
        days = self.entry_days.get().strip()
        try:
            days = int(days)
        except:
            days = 7
        include_shorts = bool(self.var_shorts.get())
        api_key = self.entry_api.get().strip() or None
        output_mode = self.output_mode.get()
        include_video_info = bool(self.var_video_info.get())
        include_channel_info = bool(self.var_channel_info.get())
        out_path = self.entry_out.get().strip()

        # disable start, enable stop
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.stop_event.clear()
        self.progress['value'] = 0

        # start background thread
        thread = threading.Thread(target=self._worker, args=(keywords, start_date, end_date, days, include_shorts, api_key, output_mode, include_video_info, include_channel_info, out_path))
        thread.daemon = True
        thread.start()

    def stop(self):
        self.stop_event.set()
        self._log("Stop requested; canceling background tasks...")

    def _worker(self, keywords, start_date, end_date, days, include_shorts, api_key,
                output_mode, include_video_info, include_channel_info, include_chart=True, out_path=None):
        try:
            # 获取输出路径，如果没有传入，则使用 entry_out 或默认文件名
            if out_path is None:
                out_path = self.entry_out.get().strip() if hasattr(self, "entry_out") else ""
                if not out_path:
                    out_path = f"yt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            def progress_cb(msg):
                self._log(msg)

            # 日期和天数逻辑
            if not self.var_use_date.get():  # 如果未勾选日期范围
                start_date = None
                end_date = None
                # days 已经传入，无需修改
            else:
                # 确保 start_date / end_date 为空时使用 None
                start_date = start_date or None
                end_date = end_date or None

            crawler = YouTubeCrawler(
                keywords=keywords,
                start_date=start_date,
                end_date=end_date,
                days=days,
                include_shorts=include_shorts,
                api_key=api_key
            )

            records = crawler.run(progress_callback=progress_cb, stop_event=self.stop_event)
            if self.stop_event.is_set():
                self._log("Crawl stopped by user.")
                self._finish_run()
                return

            self._log(f"Fetched {len(records)} videos")

            # 创建 exporter 并传入图表生成开关
            exporter = ExcelExporter(
                mode=output_mode,
                include_video_info=include_video_info,
                include_channel_info=include_channel_info
            )
            filepath = exporter.export(
                records,
                out_path=out_path
            )

            self._log(f"Exported to {filepath}")
            messagebox.showinfo("Done", f"Exported to\n{filepath}")

        except InterruptedError:
            self._log("Operation interrupted by user.")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self._log(f"Error: {e}\n{tb}")
            messagebox.showerror("Error", str(e))
        finally:
            self._finish_run()

    def _finish_run(self):
        def ui_update():
            self.btn_start.config(state="normal")
            self.btn_stop.config(state="disabled")
            self.progress['value'] = 100
        self.root.after(0, ui_update)

    def run(self):
        self.root.mainloop()
