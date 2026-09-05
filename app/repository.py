from abc import ABC, abstractmethod
from typing import Optional, Dict
from datetime import datetime, timezone

class URLRecord: 
    """Internal domain entity representing shortened URL"""
    def __init__(self, short_code: str, original_url: str, ttl_seconds: Optional[int]):
        self.short_code = short_code
        self.original_url = original_url
        self.created_at = datetime.now(timezone.utc)
        self.expires_at = (
            datetime.fromtimestamp(self.created_at.timestamp() + ttl_seconds, tz=timezone.utc)
            if ttl_seconds
            else None
        )
        self.clicks = 0
        
    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
class BaseRepository(ABC):
        @abstractmethod
        def save(self, record: URLRecord) -> URLRecord:
            pass
        
        @abstractmethod
        def get(self, short_code: str) -> Optional[URLRecord]:
            pass
        
        @abstractmethod
        def increment_clicks(self, short_code: str)-> Optional[URLRecord]:
            pass
        
        
class InMemoryRepository(BaseRepository):
        def __init__(self):
            self._db: Dict[str, URLRecord] = {}
            
        def save(self, record: URLRecord) -> URLRecord:
            self._db[record.short_code] = record
            return record
        
        def get(self, short_code: str) -> Optional[URLRecord]:
            record = self._db.get(short_code)
            if record and record.is_expired:
                del self._db[short_code]
                return None
            return record
        
        def increment_clicks(self, short_code: str) -> None:
            record = self.get(short_code)
            if record: 
                record.clicks += 1