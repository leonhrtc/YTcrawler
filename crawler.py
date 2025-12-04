# crawler.py
import requests, time
from utils import parse_duration_seconds, to_iso_start, to_iso_end
from config import YOUTUBE_API_KEY
from datetime import datetime, timedelta

YT_API_BASE = "https://www.googleapis.com/youtube/v3"

class YouTubeCrawler:
    def __init__(self, keywords, start_date=None, end_date=None, days=7, include_shorts=True, api_key=None):
        self.keywords = [k.strip() for k in keywords if k.strip()]
        self.start_date = start_date
        self.end_date = end_date
        self.days = days
        self.include_shorts = include_shorts
        self.api_key = api_key or YOUTUBE_API_KEY

    def _date_filters(self):
        if self.start_date and self.end_date:
            try:
                return to_iso_start(self.start_date), to_iso_end(self.end_date)
            except:
                pass
        # fallback: last self.days
        after = (datetime.utcnow() - timedelta(days=self.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return after, None

    def _request(self, url, params, stop_event=None):
        # Centralized request with stop checking
        if stop_event and stop_event.is_set():
            raise InterruptedError("Stopped by user")
        r = requests.get(url, params=params, timeout=15)
        if stop_event and stop_event.is_set():
            raise InterruptedError("Stopped by user")
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}: {r.text}")
        return r.json()

    def run(self, progress_callback=None, stop_event=None):
        """
        Returns list of result dicts. Each dict includes video fields and channel fields.
        stop_event: threading.Event() used to cancel operation.
        progress_callback: function(msg) to log messages back to UI.
        """
        results = []
        after, before = self._date_filters()

        for i, kw in enumerate(self.keywords, start=1):
            if progress_callback:
                progress_callback(f"[{i}/{len(self.keywords)}] Searching: '{kw}' (after={after} before={before})")
            # search.list (paginated)
            page_token = None
            while True:
                params = {
                    "part": "snippet",
                    "q": kw,
                    "type": "video",
                    "order": "date",
                    "maxResults": 50,
                    "publishedAfter": after,
                    "key": self.api_key
                }
                if before:
                    params["publishedBefore"] = before
                if page_token:
                    params["pageToken"] = page_token

                data = self._request(f"{YT_API_BASE}/search", params, stop_event=stop_event)

                items = data.get("items", [])
                video_ids = [it["id"]["videoId"] for it in items if it.get("id", {}).get("videoId")]
                if not video_ids:
                    if progress_callback:
                        progress_callback("  (no videos on this page)")
                else:
                    # fetch videos details in chunks
                    for j in range(0, len(video_ids), 50):
                        chunk = video_ids[j:j+50]
                        vparams = {
                            "part": "snippet,statistics,contentDetails",
                            "id": ",".join(chunk),
                            "key": self.api_key
                        }
                        vdata = self._request(f"{YT_API_BASE}/videos", vparams, stop_event=stop_event)
                        for v in vdata.get("items", []):
                            # check stop
                            if stop_event and stop_event.is_set():
                                raise InterruptedError("Stopped by user")
                            snippet = v.get("snippet", {})
                            stats = v.get("statistics", {})
                            det = v.get("contentDetails", {})
                            duration = parse_duration_seconds(det.get("duration", "PT0S"))
                            if (not self.include_shorts) and duration < 60:
                                continue
                            item = {
                                "video_id": v.get("id"),
                                "title": snippet.get("title", ""),
                                "description": snippet.get("description", ""),
                                "published_at": snippet.get("publishedAt", ""),
                                "duration_seconds": duration,
                                "view_count": int(stats.get("viewCount", 0) or 0),
                                "like_count": int(stats.get("likeCount", 0) or 0),
                                "comment_count": int(stats.get("commentCount", 0) or 0),
                                "channel_id": snippet.get("channelId", ""),
                                "channel_title": snippet.get("channelTitle", ""),
                                "keyword": kw
                            }
                            results.append(item)
                        time.sleep(0.05)
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
            # throttle small pause
            time.sleep(0.1)

        # fetch channel details (unique channels)
        channel_ids = list({r["channel_id"] for r in results if r.get("channel_id")})
        channel_map = {}
        for i in range(0, len(channel_ids), 50):
            chunk = channel_ids[i:i+50]
            params = {
                "part": "snippet,statistics",
                "id": ",".join(chunk),
                "key": self.api_key
            }
            cdata = self._request(f"{YT_API_BASE}/channels", params, stop_event=stop_event)
            for c in cdata.get("items", []):
                cid = c.get("id")
                ch_snip = c.get("snippet", {})
                ch_stats = c.get("statistics", {})
                channel_map[cid] = {
                    "channel_url": f"https://www.youtube.com/channel/{cid}",
                    "subscriber_count": int(ch_stats.get("subscriberCount", 0) or 0),
                    "country": ch_snip.get("country", "")
                }
            time.sleep(0.05)

        # merge channel info into results
        merged = []
        for r in results:
            cid = r.get("channel_id")
            ch = channel_map.get(cid, {"channel_url":"", "subscriber_count":0, "country":""})
            merged.append({**r, **ch})

        # deduplicate by video_id (keep latest by published_at)
        seen = {}
        for it in merged:
            vid = it["video_id"]
            if vid not in seen:
                seen[vid] = it
            else:
                # keep one with later published_at if any
                if it.get("published_at", "") > seen[vid].get("published_at", ""):
                    seen[vid] = it
        final = list(seen.values())
        if progress_callback:
            progress_callback(f"Total videos found: {len(final)}")
        return final
