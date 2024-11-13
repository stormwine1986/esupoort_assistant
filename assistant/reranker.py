import requests
import json
from typing import List

class Reranker:
    """
    Re-ranks the results of a search query.
    """
    def __init__(self, model, api_key):
        self.model = model
        self.api_key = api_key
        self.url = 'https://api.jina.ai/v1/rerank'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {api_key}"
        }
        
    def get_top_5_results(self, query:str, articles: List[dict]) -> list[dict]:
        """
        Get Top 5 Results from articles
        @param query: str Query
        @param articles: List[dict] Articles
        @return: list[dict] Top 5 Results
        """
        data = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query,
            "top_n": 5,
            "documents": [
                article["title"] for article in articles
            ]
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        result = json.loads(response.text)
        sorted_index = [article["index"] for article in result["results"]]
        
        sorted_articles = []
        for index in sorted_index:
            sorted_articles.append(articles[index])
            
        return sorted_articles