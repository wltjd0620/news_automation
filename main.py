import feedparser
import google.generativeai as genai
import requests
import os

# 1. 뉴스 수집 설정 (구글 뉴스 RSS 활용)
def get_news():
    # 경제 및 테크 키워드로 검색된 뉴스 RSS
    rss_url = "https://news.google.com/rss/search?q=경제+IT+테크&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries[:8]: # 최신 뉴스 8개 추출
        news_items.append(f"제목: {entry.title}\n링크: {entry.link}")
    return "\n\n".join(news_items)

# 2. Gemini를 이용한 요약
def summarize_news(news_text):
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    아래 뉴스 리스트를 읽고, 바쁜 직장인을 위해 핵심만 요약해줘.
    - 경제와 테크 섹션으로 구분할 것.
    - 각 뉴스는 한 줄 요약과 원본 링크를 포함할 것.
    - 말투는 친절한 뉴스레터 형식으로 작성할 것.
    
    뉴스 리스트:
    {news_text}
    """
    response = model.generate_content(prompt)
    return response.text

# 3. 텔레그램 전송
def send_telegram(text):
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    news_data = get_news()
    summary = summarize_news(news_data)
    send_telegram(summary)