import openai
from typing import List

class LLM:
    """
    LLM are used to generate text based on a given prompt.
    """
    def __init__(self, model_name, base_url, api_key):
        self.model_name = model_name
        self.base_url = base_url
        self.api_key = api_key
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    def generate_keywords(self, query:str) -> str:
        """
        Generate Query Keywords from Search
        @param query: str Query
        @return: str Keywords
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user", 
                "content": f"extract keywords for query and join them with space:\n\n{query}\n\nDon’t add extra information."
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.1,
        )
        
        keywords = response.choices[0].message.content
        
        return keywords
    
    def rag(self, query: str, articles: List[dict]) -> str:
        """
        answer the question using RAG (Retrieval Augmented Generation)
        @param query: str Question
        @param articles: List[dict] Top 5 Articles
        @return: str Answer
        """
        context = ""
        for article in articles:
            context += f"""\
                ## {article['title']}
                **Description**
                {article['description']}
                **Resolution**
                {article['resolution']}
                
                
            """
        
        prompt = f"""\
        you are a helpful assistant that answers questions about the following context.
        you should answer as concisely as possible and use the context provided below.
        if you don't know the answer, just say that you don't know. Don't try to make up an answer.
        if the context doesn't provide enough information to answer the question,just say that you don't know.
        <context>
            {context}
        </context>
        <question>
            {query}
        </question>   
        """
        
        message = [
            {
                "role": "user",
                "content": prompt,
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=0.1,
        )
        
        return response.choices[0].message.content