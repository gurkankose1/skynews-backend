from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

app = FastAPI(title="SkyNews.Tr API", version="0.1.0")

# CORS (şimdilik herkese açık; sonra domainlerini yazarsın)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

# Şimdilik örnek veri döndürüyoruz (RSS sonra eklenecek)
@app.get("/articles")
def articles(turkey_first: bool = True):
    now = datetime.now(timezone.utc).isoformat()
    sample = [
        {
            "id": "1",
            "title": "Deneme Haberi: SkyNews.Tr yayında",
            "link": "https://skynews-web.vercel.app/",
            "source": "SkyNews.Tr",
            "published": now,
            "summary": "Bu yalnızca test içeriği. RSS ekleyince gerçek haberler gelecek.",
            "category": "TR" if turkey_first else "GLOBAL",
        }
    ]
    return {"articles": sample}
