import logging
import PyPDF2
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        """Initialize the PDF processor."""
        pass
        
    def process_pdf(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a PDF file and extract text and metadata.
        
        Args:
            file_path: Path to the PDF file
            metadata: Optional metadata to supplement extracted data
            
        Returns:
            Dictionary containing extracted content and metadata
        """
        if not os.path.isfile(file_path):
            logger.error(f"PDF file not found: {file_path}")
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        try:
            # Open the PDF file
            with open(file_path, "rb") as file:
                # Create a PDF reader object
                reader = PyPDF2.PdfReader(file)
                
                # Get the number of pages
                num_pages = len(reader.pages)
                
                # Extract document info
                info = reader.metadata
                
                # Extract text from all pages
                raw_text = ""
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    raw_text += page.extract_text() + "\n"
                    
                # Clean the text
                clean_text = self._clean_text(raw_text)
                
                # Extract title
                title = self._extract_title(info, clean_text, os.path.basename(file_path))
                
                # Extract date
                date = self._extract_date(info)
                
                # Prepare metadata
                meta = metadata or {}
                meta.update({
                    "pdf_info": {
                        "num_pages": num_pages,
                        "author": info.author if hasattr(info, "author") else None,
                        "creator": info.creator if hasattr(info, "creator") else None,
                        "producer": info.producer if hasattr(info, "producer") else None,
                        "subject": info.subject if hasattr(info, "subject") else None,
                    },
                    "file_name": os.path.basename(file_path),
                    "process_date": datetime.now().isoformat(),
                })
                
                return {
                    "title": title,
                    "raw_content": raw_text,
                    "clean_content": clean_text,
                    "date": date,
                    "url": file_path,
                    "source": "PDF",
                    "metadata": meta
                }
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
            
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing."""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
        
    def _extract_title(self, info, text: str, fallback_filename: str) -> str:
        """Extract the title from PDF metadata or text."""
        # Try to get title from metadata
        if hasattr(info, "title") and info.title:
            return info.title
            
        # Try to extract from first line of text
        lines = text.strip().split('\n')
        if lines and lines[0].strip():
            # Use the first non-empty line as title if it's not too long
            first_line = lines[0].strip()
            if len(first_line) <= 100:
                return first_line
                
        # Fallback to filename without extension
        return os.path.splitext(fallback_filename)[0]
        
    def _extract_date(self, info) -> Optional[str]:
        """Extract the date from PDF metadata."""
        # Try to get date from metadata
        if hasattr(info, "creation_date") and info.creation_date:
            try:
                # PDF dates can be in various formats
                date_str = info.creation_date
                # Try to parse the date
                if isinstance(date_str, str):
                    # Handle various date formats
                    patterns = [
                        r'D:(\d{4})(\d{2})(\d{2})',  # D:20231101
                        r'(\d{4})-(\d{2})-(\d{2})',  # 2023-11-01
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, date_str)
                        if match:
                            year, month, day = match.groups()
                            return f"{year}-{month}-{day}"
                            
                    return None
                    
                # If it's a datetime object
                if hasattr(date_str, "year") and hasattr(date_str, "month") and hasattr(date_str, "day"):
                    return f"{date_str.year}-{date_str.month:02d}-{date_str.day:02d}"
                    
            except Exception as e:
                logger.warning(f"Error parsing PDF date: {str(e)}")
                
        return None 