import tweepy
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self):
        """Initialize Twitter client with credentials from environment variables."""
        load_dotenv()
        
        # Get Twitter API credentials from environment variables
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        self.api = None
        self.initialize()
        
    def initialize(self):
        """Initialize the Twitter API client."""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            logger.warning("Twitter API credentials are not fully configured")
            return
            
        try:
            # Set up authentication
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )
            
            # Create API instance
            self.api = tweepy.API(auth)
            
            # Verify credentials
            self.api.verify_credentials()
            logger.info("Twitter API authentication successful")
        except Exception as e:
            logger.error(f"Twitter API authentication failed: {str(e)}")
            self.api = None
            
    def fetch_timeline(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch tweets from the user's timeline.
        
        Args:
            count: Number of tweets to fetch (max 200)
            
        Returns:
            List of normalized tweet data
        """
        if not self.api:
            logger.error("Twitter API client not initialized")
            return []
            
        try:
            # Fetch tweets from timeline
            tweets = self.api.home_timeline(count=min(count, 200))
            return [self._normalize_tweet(tweet._json) for tweet in tweets]
        except Exception as e:
            logger.error(f"Error fetching timeline: {str(e)}")
            return []
            
    def fetch_user_tweets(self, username: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch tweets from a specific user.
        
        Args:
            username: Twitter username without the '@' symbol
            count: Number of tweets to fetch (max 200)
            
        Returns:
            List of normalized tweet data
        """
        if not self.api:
            logger.error("Twitter API client not initialized")
            return []
            
        try:
            # Fetch tweets from the user
            tweets = self.api.user_timeline(screen_name=username, count=min(count, 200))
            return [self._normalize_tweet(tweet._json) for tweet in tweets]
        except Exception as e:
            logger.error(f"Error fetching tweets for user {username}: {str(e)}")
            return []
            
    def search_tweets(self, query: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Search for tweets matching a query.
        
        Args:
            query: Search query
            count: Number of tweets to fetch (max 100)
            
        Returns:
            List of normalized tweet data
        """
        if not self.api:
            logger.error("Twitter API client not initialized")
            return []
            
        try:
            # Search for tweets
            tweets = self.api.search_tweets(q=query, count=min(count, 100))
            return [self._normalize_tweet(tweet._json) for tweet in tweets]
        except Exception as e:
            logger.error(f"Error searching tweets for query '{query}': {str(e)}")
            return []
            
    def _normalize_tweet(self, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize tweet data to a consistent format.
        
        Args:
            tweet_data: Raw tweet data from the Twitter API
            
        Returns:
            Normalized tweet data
        """
        # Extract basic information
        tweet_id = tweet_data.get("id_str")
        text = tweet_data.get("full_text", tweet_data.get("text", ""))
        created_at = tweet_data.get("created_at")
        
        # Parse the date
        date = None
        if created_at:
            try:
                date_obj = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                date = date_obj.date().isoformat()
            except Exception:
                pass
                
        # Get user information
        user = tweet_data.get("user", {})
        username = user.get("screen_name")
        user_name = user.get("name")
        
        # Get URLs
        urls = []
        entities = tweet_data.get("entities", {})
        if "urls" in entities:
            urls = [url.get("expanded_url") for url in entities.get("urls", [])]
            
        # Get hashtags
        hashtags = []
        if "hashtags" in entities:
            hashtags = [tag.get("text") for tag in entities.get("hashtags", [])]
            
        # Construct normalized data
        return {
            "title": f"Tweet by @{username}",
            "raw_content": text,
            "clean_content": text,  # Tweets are already clean text
            "date": date,
            "url": f"https://twitter.com/{username}/status/{tweet_id}",
            "source": "Twitter",
            "metadata": {
                "tweet_id": tweet_id,
                "username": username,
                "user_name": user_name,
                "urls": urls,
                "hashtags": hashtags,
                "retweet_count": tweet_data.get("retweet_count", 0),
                "favorite_count": tweet_data.get("favorite_count", 0),
                "is_retweet": "retweeted_status" in tweet_data,
            }
        } 