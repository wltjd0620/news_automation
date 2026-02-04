import feedparser
from google import genai
import requests
import os

def get_news():
    print("1. 실시간 뉴스 데이터를 가져오는 중...")
    # 최근 24시간 내의 경제/IT/테크 뉴스 검색
    query = "(경제|비즈니스|IT|AI|테크|반도체)+when:24h"
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        return ""

    news_items = []
    for entry in feed.entries[:10]:
        news_items.append(f"원본제목: {entry.title}\n링크: {entry.link}")
    
    print(f"총 {len(feed.entries)}개 중 상위 {len(news_items)}개를 선별.")
    
    return "\n\n".join(news_items)

def summarize_news(news_text):
    if not news_text:
        return "최근 24시간 내에 수집된 새로운 뉴스가 없습니다."

    print("2. Gemini AI 산업 영향력 분석 및 요약 중...")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    # 기사 단위 분할을 위해 명확한 구분자 [기사]를 사용하도록 지시
    prompt = f"""
    당신은 IT 및 첨단 기술 전문 산업 분석가입니다. 
    제공된 뉴스 리스트를 분석하여, 기술직 직장인이자 연구자를 위한 '데일리 산업 영향력 리포트'를 작성하세요.

    [작성 가이드라인]
    1. 각 기사는 반드시 [제목] 문구로 시작할 것.
    2. 섹션 구분: '경제/비즈니스'와 '테크/기술'로 분류하여 정리할 것.
    3. 뉴스 구성 요소 (반드시 지킬 것):
       <b>핵심을 찌르는 한 줄 제목</b>
       [핵심 요약]: 기사 내용을 1문장으로 명확히 요약
       [인사이트]: 
          * 경제 기사: 단순 지표(환율, 금리 등)를 넘어 현재 글로벌 자본과 권력이 어디로 이동하고 있는지, 시장 전반의 심리(Risk-on/off)와 분위기를 분석하세요. 
          * 테크 기사: 이 기술이나 이슈가 특정 산업에 가져올 변화와 시사점 분석
       [링크] : <a href="원문_링크">기사 원문 보기</a>

    [스타일 및 가독성]
    - 텔레그램 HTML 모드를 사용하므로 <b> 태그를 적절히 활용하여 제목을 강조하세요.
    - 앞 뒤로 불필요한 설명이나 문구를 넣지 말고, 오직 분석 리포트만 출력하세요.
    - 중요도가 낮아 보인다는 이유로 기사를 임의로 제외하지 마세요. 반드시 10개의 기사가 결과물에 포함되어야 합니다.
    - 각 표현은 명확하고 간결하게 작성하세요.

    뉴스 리스트:
    {news_text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    
    except Exception as e:
        print(f"AI 분석 실패: {e}")
        return "AI 분석 중 오류가 발생했습니다."

def send_telegram(text):
    print("3. 텔레그램 메시지 전송 시작...")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # 1. [기사] 키워드로 텍스트를 나눕니다.
    articles = text.split('[기사]')
    articles = [a.strip() for a in articles if a.strip()]

    print(f"총 분석된 기사 개수: {len(articles)}개")

    # 5개씩 묶어서 루프 가동
    chunk_size = 5
    for i in range(0, len(articles), chunk_size):
        chunk = articles[i : i + chunk_size]
        
        header = f"<b>글로벌 마켓 & 테크 리포트 ({i//chunk_size + 1}부)</b>\n\n"
        body = ""
        for item in chunk:
            body += "----------------------------\n<b>[기사]</b> " + item + "\n\n"
        
        payload = {
            "chat_id": chat_id,
            "text": header + body,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "disable_notification": False if i == 0 else True
        }
        
        res = requests.post(url, json=payload)
        print(f"{i//chunk_size + 1}부 전송 시도... 결과: {res.status_code}")
        
        if res.status_code != 200:
            print(f"전송 실패 상세: {res.text}")

if __name__ == "__main__":
    try:
        news_data = get_news()
        summary = summarize_news(news_data)
        send_telegram(summary)
    except Exception as e:
        print(f"최종 오류 발생: {e}")