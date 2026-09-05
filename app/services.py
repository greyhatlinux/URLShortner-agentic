
import secrets
import string
from typing import Optional
from .repository import BaseRepository, URLRecord

class URLShortenerService:
    def __init__(self, repo : BaseRepository):
        self.repo = repo
        
    def _generate_short_code(self, length: int = 6) -> str:
        """Generates a cryptographically secure random string of length = 6"""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))
        
    def shorted_url(self, original_url: str, ttl_seconds: Optional[int]) -> URLRecord:
        for _ in range(5):
            code = self._generate_short_code()
            print(code)
            if self.repo.get(code) is None:
                record = URLRecord(short_code = code, original_url= original_url, ttl_seconds = ttl_seconds)
                return self.repo.save(record)
            
        raise RuntimeError("Failed to generate shortened URL. Please try again later")
    
    def resolve_url(self, short_code: str) -> Optional[str]:
        record = self.repo.get(short_code)
        if not record:
            return None
        
        self.repo.increment_clicks(short_code)
        return record.original_url
    
    def get_analytics(self, short_code: str) -> Optional[URLRecord] :
        return self.repo.get(short_code)