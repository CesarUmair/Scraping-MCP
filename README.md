# MCP Server: Unified Intelligence Aggregator

A lightweight, modular backend system that aggregates and normalizes content from various sources (news articles, research PDFs, Twitter feeds, emails, and manual uploads). The system uses the Model Context Protocol (MCP) to expose functionality as tools for AI assistants.

## Features

- **Centralized Content Storage**: Keep all content in one place with metadata for source, topic, and date
- **Search and Analysis**: Allow full-text search, filtering by date, source, and tag
- **MCP Interface**: Standardized interface for AI assistants to call tools like "search," "list," or "summarize"
- **Modular and Privacy-Focused**: Lightweight, extensible, and secure by design

## Setup and Installation

### Prerequisites

- Python 3.8+
- PostgreSQL (or Supabase account)
- API keys for content sources (Twitter, etc.)

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mcp-server
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install Playwright browsers:
   ```
   playwright install
   ```

5. Create a `.env` file with your credentials:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
   TWITTER_API_KEY=your_key
   TWITTER_API_SECRET=your_secret
   TWITTER_ACCESS_TOKEN=your_token
   TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
   ```

### Running the Application

Start the FastAPI server:
```
uvicorn app.main:app --reload
```

## Project Structure

```
mcp_server/
├── app/
│   ├── api/           # API endpoints and MCP tools
│   ├── core/          # Core application functionality
│   ├── db/            # Database models and connection
│   ├── ingestion/     # Data ingestion modules
│   ├── models/        # Pydantic models
│   ├── utils/         # Utility functions
│   └── main.py        # Application entry point
├── venv/              # Virtual environment
├── .env               # Environment variables
├── .gitignore         # Git ignore file
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Usage

### API Documentation

Once the server is running, you can access the API documentation at:
```
http://localhost:8000/docs
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 