import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio

# Add project root and src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv  # type: ignore
from .base import Scraper, ScrapeResult
from scrapegraph_py import AsyncClient

load_dotenv()


class ScrapegraphAIScraper(Scraper):
    """Scrapes web pages using the ScrapegraphAI."""

    def __init__(self):
        self.api_key = os.getenv("SCRAPEGRAPHAI_API_KEY")
        if not self.api_key:
            raise ValueError("SCRAPEGRAPHAI_API_KEY not set in environment.")
        self.client = AsyncClient(api_key=self.api_key)

    async def scrape(self, url: str, run_id: str) -> ScrapeResult:
        try:
            result = await self.client.markdownify(website_url=url)

            content = result.get("result") if result else ""

            content_size = len(content.encode("utf-8"))

            return ScrapeResult(
                run_id=run_id,
                scraper="scrapegraphai_scraper",
                url=url,
                status_code=200,
                error=result.get("error") if result else None,
                content_size=content_size,
                format="markdown",
                created_at=datetime.now().isoformat(),
                content=content or None,
            )
        except asyncio.TimeoutError:
            return ScrapeResult(
                run_id=run_id,
                scraper="scrapegraphai_scraper",
                url=url,
                status_code=408,  # Timeout status code
                error="Timeout error",
                content_size=0,
                format="markdown",
                created_at=datetime.now().isoformat(),
                content=None,
            )
        except Exception as e:
            return ScrapeResult(
                run_id=run_id,
                scraper="scrapegraphai_scraper",
                url=url,
                status_code=500,
                error=f"{type(e).__name__}: {str(e)}",
                content_size=0,
                format="markdown",
                created_at=datetime.now().isoformat(),
                content=None,
            )

    def check_environment(self) -> bool:
        if not self.api_key:
            return False
        return True
