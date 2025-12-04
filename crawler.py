import requests
import datetime
from config import YOUTUBE_API_KEY


class YouTubeCrawler:
    def __init__(self, keywords, days=7, include_shorts=True, start_date=None, end_date=None):
        self.keywords = [k.strip() for k in keywords if k.strip()]
        self.days = days
        self.include_shorts = include_shorts
        self.start_date = start_date
        self.end_date = end_date

        self.base_search_url = "https://www.googleapis.com/youtube/v3/search"
        self.base_video_url = "https://www.googleapis.com/youtube/v3/videos"
        self.base_channel_url = "https://www.googleapis.com/youtube/v3/channels"

    # ============================================================
    def _get_date_filters(self):
        if self.start_date and self.end_date:
            try:
                start = datetime.datetime.strptime(self.start_date, "%Y-%m-%d").isoformat("T") + "Z"
                end = datetime.datetime.strptime(self.end_date, "%Y-%m-%d").isoformat("T") + "Z"
                return start, end
            except:
                pass

        publish_after = (datetime.datetime.utcnow() - datetime.timedelta(days=self.days)).isoformat("T") + "Z"
        return publish_after, None

    # ============================================================
    def run(self, progress_callback=None):
        all_results = []

        for kw in self.keywords:
            if progress_callback:
                progress_callback(f"Searching: {kw}")

            results = self._search_keyword(kw, progress_callback)
            all_results.extend(results)

        unique = {x["video_id"]: x for x in all_results}
        return list(unique.values())

    # ============================================================
    def _search_keyword(self, keyword, progress_callback):
        after, before = self._get_date_filters()

        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": 50,
            "order": "date",
            "publishedAfter": after
        }
        if before:
            params["publishedBefore"] = before

        r = requests.get(self.base_search_url, params=params)
        data = r.json()

        if "items" not in data:
            return []

        video_ids = [item["id"]["videoId"] for item in data["items"]]

        # filter shorts
        if not self.include_shorts:
            video_ids = [vid for vid in video_ids if not self._is_shorts(vid)]

        if not video_ids:
            return []

        video_info = self._fetch_video_details(video_ids)
        results = []

        for v in video_info:
            c = self._fetch_channel_info(v["channel_id"])
            results.append({**{"keyword": keyword}, **v, **c})

        return results

    # shorts = video id starting with S
    def _is_shorts(self, vid):
        return vid.startswith("S")

    # ============================================================
    def _fetch_video_details(self, ids):
        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet,statistics",
            "id": ",".join(ids)
        }
        r = requests.get(self.base_video_url, params=params)
        data = r.json()

        output = []
        for item in data.get("items", []):
            s = item["snippet"]
            st = item.get("statistics", {})
            output.append({
                "video_id": item["id"],
                "title": s.get("title", ""),
                "description": s.get("description", ""),
                "publishedAt": s.get("publishedAt", ""),
                "channel_id": s.get("channelId", ""),
                "channel_title": s.get("channelTitle", ""),
                "video_url": f"https://www.youtube.com/watch?v={item['id']}",
                "views": st.get("viewCount", "0"),
                "likes": st.get("likeCount", "0"),
                "comments": st.get("commentCount", "0"),
            })
        return output

    # ============================================================
    def _fetch_channel_info(self, cid):
        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet,statistics",
            "id": cid
        }
        r = requests.get(self.base_channel_url, params=params)
        data = r.json()

        if not data.get("items"):
            return {}

        item = data["items"][0]
        s = item["snippet"]
        stats = item["statistics"]

        return {
            "channel_url": f"https://www.youtube.com/channel/{cid}",
            "channel_country": s.get("country", "Unknown"),
            "subscribers": stats.get("subscriberCount", "0")
        }
