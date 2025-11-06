import os
from fastapi import FastAPI, Query
from pydantic import BaseModel
import feedparser
from datetime import datetime, timezone
from dateutil import parser as dparser

app = FastAPI(title="SkyNews.Tr Aggregator", version="0.1.0")

# Minimal source list (you can expand later)
DEFAULT_SOURCES_TR = [
    "https://www.shgm.gov.tr/tr/anasayfa.rss",
    "https://www.iga.aero/haberler.rss",
]
DEFAULT_SOURCES_GLOBAL = [
    "https://simpleflying.com/rss",
    "https://www.flightglobal.com/feeds/rss",
    "https://www.aviation24.be/feed/",
]

class Article(BaseModel):
    id: str
    title: str
    link: str
    source: str
    published: str
    summary: str | None = None
    category: str | None = None

@app.get("/health")
async def health():
    return {"ok": True}

def parse_feed(url: str, category: str | None = None):
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries[:20]:
        link = getattr(e, "link", "")
        title = getattr(e, "title", "")
        summary = getattr(e, "summary", None)
        published = None
        for key in ("published", "updated", "created"):
            val = getattr(e, key, None)
            if val:
                try:
                    published = dparser.parse(val)
                    break
                except Exception:
                    pass
        if not published:
            published = datetime.now(timezone.utc)
        src = feed.feed.get("title", url)
        items.append(Article(
            id=link or title,
            title=title,
            link=link,
            source=src,
            published=published.isoformat(),
            summary=summary,
            category=category
        ))
    return items

@app.get("/articles")
async def articles(turkey_first: bool = Query(False)):
    # Pull fresh on every request (simple demo). Add caching later.
    tr = []
    for u in DEFAULT_SOURCES_TR:
        try:
            tr.extend(parse_feed(u, category="TR"))
        except Exception:
            pass
    gl = []
    for u in DEFAULT_SOURCES_GLOBAL:
        try:
            gl.extend(parse_feed(u, category="GLOBAL"))
        except Exception:
            pass
    items = (tr + gl) if turkey_first else (gl + tr)
    # sort by time desc
    items.sort(key=lambda x: x.published, reverse=True)
    return {"articles": [a.model_dump() for a in items[:50]]}
