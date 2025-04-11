from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import shutil
import tempfile
import logging
from datetime import datetime

# Import database dependencies
from app.db.database import get_db_session
from app.db.models import Content as ContentModel, Tag as TagModel, content_tags
from app.models.content import ContentCreate, Content

# Import ingestion modules
from app.ingestion.web_scraper import WebScraper
from app.ingestion.twitter import TwitterClient
from app.ingestion.pdf_processor import PDFProcessor

# Setup logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ingestion", tags=["ingestion"])

# Models for ingestion
class WebScrapeRequest(BaseModel):
    url: str
    source: str
    selectors: Dict[str, str]
    tags: List[str] = []
    
class TwitterRequest(BaseModel):
    query_type: str  # "timeline", "user", or "search"
    query: Optional[str] = None  # Username or search query
    count: int = 20
    tags: List[str] = []
    
class EmailRequest(BaseModel):
    subject: str
    sender: str
    body: str
    date: Optional[str] = None
    tags: List[str] = []

# Endpoints for ingestion
@router.post("/web-scrape", response_model=Content)
async def ingest_web_content(
    request: WebScrapeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ingest content from a web page by scraping it.
    """
    try:
        # Initialize web scraper
        scraper = WebScraper()
        
        # Configure selectors
        config = request.selectors
        
        # Scrape the URL
        # Note: This would be better as a background task, but for simplicity we'll do it synchronously
        content_data = await scraper.scrape_url(request.url, config)
        
        # Add source and tags
        content_data["source"] = request.source
        
        # Create ContentCreate object
        content_create = ContentCreate(
            source=content_data["source"],
            raw_content=content_data["raw_content"],
            clean_content=content_data["clean_content"],
            title=content_data.get("title"),
            url=content_data.get("url"),
            date=datetime.now().date() if not content_data.get("date") else content_data.get("date"),
            metadata=content_data.get("metadata", {}),
            tags=request.tags
        )
        
        # TODO: Save to database
        # For now, return mock response
        return {
            "id": 1,
            "source": content_create.source,
            "raw_content": content_create.raw_content[:100] + "...",  # Truncate for response
            "clean_content": content_create.clean_content[:100] + "..." if content_create.clean_content else None,
            "title": content_create.title,
            "url": content_create.url,
            "date": content_create.date,
            "metadata": content_create.metadata,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": [{"id": 1, "name": tag, "created_at": datetime.now()} for tag in request.tags]
        }
    except Exception as e:
        logger.error(f"Error ingesting web content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting web content: {str(e)}")

@router.post("/twitter", response_model=List[Dict[str, Any]])
async def ingest_twitter_content(
    request: TwitterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ingest content from Twitter based on the specified query type.
    """
    try:
        # Initialize Twitter client
        twitter_client = TwitterClient()
        
        tweets = []
        
        # Fetch tweets based on query type
        if request.query_type == "timeline":
            tweets = twitter_client.fetch_timeline(count=request.count)
        elif request.query_type == "user" and request.query:
            tweets = twitter_client.fetch_user_tweets(username=request.query, count=request.count)
        elif request.query_type == "search" and request.query:
            tweets = twitter_client.search_tweets(query=request.query, count=request.count)
        else:
            raise HTTPException(status_code=400, detail="Invalid query type or missing query parameter")
            
        # TODO: Save tweets to database
        # For now, return the tweets
        return tweets
    except Exception as e:
        logger.error(f"Error ingesting Twitter content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting Twitter content: {str(e)}")

@router.post("/email", response_model=Content)
async def ingest_email_content(
    request: EmailRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ingest content from an email.
    """
    try:
        # Process email data
        email_date = datetime.now().date()
        if request.date:
            try:
                email_date = datetime.strptime(request.date, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        # Create ContentCreate object
        content_create = ContentCreate(
            source="Email",
            raw_content=request.body,
            clean_content=request.body,  # For simplicity, no cleaning
            title=request.subject,
            url=None,
            date=email_date,
            metadata={
                "sender": request.sender,
                "subject": request.subject,
                "ingestion_date": datetime.now().isoformat()
            },
            tags=request.tags
        )
        
        # TODO: Save to database
        # For now, return mock response
        return {
            "id": 1,
            "source": content_create.source,
            "raw_content": content_create.raw_content[:100] + "...",  # Truncate for response
            "clean_content": content_create.clean_content[:100] + "...",
            "title": content_create.title,
            "url": content_create.url,
            "date": content_create.date,
            "metadata": content_create.metadata,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": [{"id": 1, "name": tag, "created_at": datetime.now()} for tag in request.tags]
        }
    except Exception as e:
        logger.error(f"Error ingesting email content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting email content: {str(e)}")
        
@router.post("/pdf", response_model=Content)
async def ingest_pdf_content(
    file: UploadFile = File(...),
    source: str = Form("PDF"),
    tags: str = Form(""),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Ingest content from a PDF file.
    """
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Copy the uploaded file to the temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
        # Process the PDF
        pdf_processor = PDFProcessor()
        content_data = pdf_processor.process_pdf(temp_file_path)
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            
        # Create ContentCreate object
        content_create = ContentCreate(
            source=source,
            raw_content=content_data["raw_content"],
            clean_content=content_data["clean_content"],
            title=content_data.get("title"),
            url=file.filename,  # Use original filename as URL
            date=datetime.now().date() if not content_data.get("date") else content_data.get("date"),
            metadata=content_data.get("metadata", {}),
            tags=tag_list
        )
        
        # TODO: Save to database
        # For now, return mock response
        response = {
            "id": 1,
            "source": content_create.source,
            "raw_content": content_create.raw_content[:100] + "...",  # Truncate for response
            "clean_content": content_create.clean_content[:100] + "...",
            "title": content_create.title,
            "url": content_create.url,
            "date": content_create.date,
            "metadata": content_create.metadata,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "tags": [{"id": 1, "name": tag, "created_at": datetime.now()} for tag in tag_list]
        }
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return response
    except Exception as e:
        logger.error(f"Error ingesting PDF content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ingesting PDF content: {str(e)}") 