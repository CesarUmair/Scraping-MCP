from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ARRAY, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base

# Association table for many-to-many relationship between content and tags
content_tags = Table(
    'content_tags',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('content.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Content(Base):
    """Content model for storing all types of content (articles, tweets, etc.)"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), index=True)  # WSJ, Twitter, etc.
    raw_content = Column(Text)
    clean_content = Column(Text)
    title = Column(String(255), nullable=True)
    url = Column(String(512), nullable=True)
    date = Column(Date, index=True)
    metadata = Column(JSONB, nullable=True)  # For additional source-specific data
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tags = relationship("Tag", secondary=content_tags, back_populates="content_items")

class Tag(Base):
    """Tags for categorizing content"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    content_items = relationship("Content", secondary=content_tags, back_populates="tags")

class Source(Base):
    """Source configuration for data ingestion"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    type = Column(String(20))  # web, twitter, email, etc.
    config = Column(JSONB)  # Configuration for the source
    is_active = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now()) 