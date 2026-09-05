from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
import uvicorn

from .schemas import AnalyticsResponse, URLCreateRequest, URLCreateResponse
from .repository import InMemoryRepository
from .services import URLShortenerService

app = FastAPI(title="Production-ready URL shortner service", version="1.0.0")

# singleton repo for in-memory storage
memory_repo = InMemoryRepository()

def get_service() -> URLShortenerService:
    return URLShortenerService(repo=memory_repo)

@app.post("/shorten", response_model=URLCreateResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(
    request: URLCreateRequest,
    service: URLShortenerService = Depends(get_service)
):
    record = service.shorted_url(
        original_url = str(request.url),
        ttl_seconds = request.ttl_seconds
    )

    return URLCreateResponse(
        short_code = record.short_code,
        original_url = record.original_url,
        created_at = record.created_at,
        expired_at = record.expires_at,
        clicks = record.clicks
    )

@app.get("/{short_code}", response_class=RedirectResponse)
def redirect_to_url(
    short_code: str,
    service: URLShortenerService = Depends(get_service)
):
    original_url = service.resolve_url(short_code)
    if not original_url:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail="URL not found or has expired"
        )
    return RedirectResponse(url=original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.get("/analytics/{short_code}", response_model = AnalyticsResponse)
def get_url_analytics(
    short_code: str,
    service: URLShortenerService = Depends(get_service)
):
    record = service.get_analytics(short_code)
    if not record:
        raise HTTPException(
            status=status.HTTP_404_NOT_FOUND,
            detail="URL analystics for this short code is not available, or has expired"
        )
    return AnalyticsResponse(
        short_code = record.short_code,
        original_url = record.original_url,
        clicks = record.clicks,
        is_expired = record.is_expired,
        created_at =  record.created_at,
        expires_at = record.expires_at
    )


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)