import gradio as gr

import time
from dotenv import load_dotenv
import os
from typing import Generator

from assistant.llm import LLM
from assistant.reranker import Reranker
from assistant.esupport import ESupport

load_dotenv(dotenv_path=".env")

llm_model_name = os.getenv("LLM_MODEL_NAME")
llm_base_url = os.getenv("LLM_BASE_URL")
llm_api_key = os.getenv("LLM_API_KEY")

jina_api_key = os.getenv("JINA_API_KEY")
jina_model_name = os.getenv("JINA_MODEL_NAME")

esuport_email = os.getenv("ESUPORT_EMAIL")
esuport_password = os.getenv("ESUPORT_PASSWORD")

llm = LLM(
    model_name=llm_model_name,
    base_url=llm_base_url,
    api_key=llm_api_key
)

reranker = Reranker(
    model=jina_model_name,
    api_key=jina_api_key
)

def process(question) -> Generator[str,str,str]:
    """
    处理函数，接收用户输入的问题，并返回答案
    """
    esupport = ESupport(
        driver_path="C:\\chromedriver-win64\\chromedriver.exe"
    )
    log = "Submit Question: {}\n".format(question)
    log += "Try to Login...\n"
    answer = ""
    yield log, answer, ""
    try:
        esupport.login(
            email=os.environ.get("ESUPORT_EMAIL"), 
            password=os.environ.get("ESUPORT_PASSWORD")
        )
        log += "Login Successfully.\n"
        yield log, answer, ""
        keywords = llm.generate_keywords(query=question)
        log += "Generate Keywords: {}\n".format(keywords)
        yield log, answer, ""
        articles = esupport.search_articles(search=keywords)
        log += "Searched Articles Count: {}\n".format(len(articles))
        yield log, answer, ""
        
        top5 = []
        if(len(articles) > 0):
            top5 = reranker.get_top_5_results(query=question, articles=articles)
            log += "Fetching Articles Details...\n"
            yield log, answer, ""
            top5 = esupport.get_article_details(articles=top5)
            log += "Fetching Articles Details Successfully.\n"
            yield log, answer, ""
        
        log += "Generating Answer...\n"
        yield log, answer, ""
        answer = llm.rag(query=question, articles=top5)
        log += "Generating Answer Successfully.\n"
        yield log, answer, format_links(top5)
    except TimeoutError as e:
        log += f"\nError: Timeout occurred while processing the task. {e}"
        yield log, answer, ""
    finally:
        esupport.exit()
        
def format_links(articles: list[dict]) -> str:
    """
    将文章列表中的链接格式化为字符串
    """
    links = [f" - [{article['title']}]({article['link']})" for article in articles]
    return "\n".join(links)
    

with gr.Blocks() as app:
    gr.Markdown("# eSupport Assistant")
    
    with gr.Row():
        with gr.Column():
            question_input = gr.Textbox(placeholder="Enter your question", label="Question")
            submit_btn = gr.Button("Submit")
            log_text = gr.Textbox(label="Monitor", interactive=False, lines=15)
        with gr.Column():
            answer_input = gr.Textbox(label="Answer", interactive=False, lines=10)
            links = gr.Markdown(label="Top 5")

    submit_btn.click(fn=process, inputs=[question_input], outputs=[log_text, answer_input, links])


app.launch()