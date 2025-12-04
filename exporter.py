# exporter.py
import pandas as pd
import math
from datetime import datetime

def _safe_int(x):
    try:
        return int(x)
    except:
        return 0

class ExcelExporter:
    def __init__(self, mode="both", include_video_info=True, include_channel_info=True):
        """
        mode: "merged", "separate", "both"
        include_video_info / include_channel_info: booleans
        """
        self.mode = mode
        self.include_video_info = include_video_info
        self.include_channel_info = include_channel_info

    def export(self, records, out_path=None):
        """
        records: list of dicts (merged results from crawler)
        out_path: optional output filename, default auto
        returns filepath
        """
        df = pd.DataFrame(records)
        if df.empty:
            raise ValueError("No data to export")

        # unify numeric columns
        for c in ["view_count","like_count","comment_count","subscriber_count","duration_seconds"]:
            if c in df.columns:
                df[c] = df[c].apply(_safe_int)

        if not out_path:
            out_path = f"yt_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        writer = pd.ExcelWriter(out_path, engine="xlsxwriter", datetime_format="yyyy-mm-ddThh:mm:ss")

        # sheet names per keyword if separate: group by keyword
        if self.mode in ("separate","both"):
            for kw, group in df.groupby("keyword"):
                sheet = (kw[:28]+"_YouTube") if len(kw)>28 else f"{kw}_YouTube"
                cols = []
                if self.include_video_info:
                    cols += ["video_id","title","description","published_at","video_url","duration_seconds","view_count","like_count","comment_count"]
                if self.include_channel_info:
                    cols += ["channel_id","channel_title","channel_url","subscriber_count","country"]
                cols = [c for c in cols if c in group.columns]
                group.to_excel(writer, sheet_name=sheet, index=False, columns=cols)

        if self.mode in ("merged","both"):
            cols = []
            if self.include_video_info:
                cols += ["keyword","video_id","title","description","published_at","video_url","duration_seconds","view_count","like_count","comment_count"]
            if self.include_channel_info:
                cols += ["channel_id","channel_title","channel_url","subscriber_count","country"]
            cols = [c for c in cols if c in df.columns]
            df.to_excel(writer, sheet_name="Merged", index=False, columns=cols)

        # Analysis sheet
        ws_summary = "Analysis"
        summary = []
        for kw, group in df.groupby("keyword"):
            summary.append({
                "keyword": kw,
                "video_count": len(group),
                "total_views": int(group["view_count"].sum()) if "view_count" in group else 0,
                "avg_views": int(group["view_count"].mean()) if "view_count" in group and len(group)>0 else 0
            })
        summary_df = pd.DataFrame(summary)
        summary_df.to_excel(writer, sheet_name=ws_summary, index=False)

        # --- Add column charts ---
        workbook = writer.book
        worksheet = writer.sheets[ws_summary]

        chart = workbook.add_chart({'type': 'column'})

        # Total Views
        chart.add_series({
            'name': 'Total Views',
            'categories': [ws_summary, 1, 0, len(summary), 0],
            'values':     [ws_summary, 1, 2, len(summary), 2],
        })

        # Average Views
        chart.add_series({
            'name': 'Average Views',
            'categories': [ws_summary, 1, 0, len(summary), 0],
            'values':     [ws_summary, 1, 3, len(summary), 3],
        })

        chart.set_title({'name': 'Total & Average Views by Keyword'})
        chart.set_x_axis({'name': 'Keyword'})
        chart.set_y_axis({'name': 'Views'})
        chart.set_style(10)  # 可以更改样式

        # Insert chart below the table
        worksheet.insert_chart(len(summary)+3, 0, chart)

        writer.close()
        return out_path
