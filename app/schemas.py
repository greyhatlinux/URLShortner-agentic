from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional


class URLCreateRequest(BaseModel) : 
    url: HttpUrl
    ttl_seconds: Optional[int] = Field(
        default = 86400,
        gt = 0,
        description = "Time to Live in seconds for the shortened URL (default : 24 hours)"
    )
    
class URLCreateResponse(BaseModel):
    original_url: HttpUrl
    short_code: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    clicks: int
    
    
class AnalyticsResponse(BaseModel):
    short_code: str
    original_url: str
    clicks: int
    is_expired: bool
    created_at: datetime
    expires_at: Optional[datetime]

