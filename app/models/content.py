from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ContentBase(BaseModel):
    source: str
    raw_content: str
    clean_content: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    date: date
    metadata: Optional[Dict[str, Any]] = None

class ContentCreate(ContentBase):
    tags: Optional[List[str]] = []

class Content(ContentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []
    
    class Config:
        orm_mode = True

class SourceBase(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    is_active: int = 1

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Models for search and listing
class SearchParams(BaseModel):
    keyword: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    source: Optional[str] = None
    limit: int = 10
    offset: int = 0

class ListParams(BaseModel):
    source: Optional[str] = None
    tag: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: int = 10
    offset: int = 0 