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

    print(f"찾은 기사 개수 : {len(feed.entries)}")

    news_items = []
    for entry in feed.entries[:10]:
        news_items.append(f"원본제목: {entry.title}\n링크: {entry.link}")
    
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
       [산업 영향력 분석]: 
          * 경제 기사: 단순 지표(환율, 금리 등)를 넘어 현재 글로벌 자본과 권력이 어디로 이동하고 있는지, 시장 전반의 심리(Risk-on/off)와 분위기를 분석하세요. 
          * 테크 기사: 이 기술이나 이슈가 특정 산업에 가져올 변화와 시사점 분석
       <a href="원문_링크">기사 원문 보기</a>

    [스타일 및 가독성]
    - 텔레그램 HTML 모드를 사용하므로 <b> 태그를 적절히 활용하여 제목과 주요 키워드를 강조할 것.
    - 문장은 간결한 경어체를 사용하고, 이모지를 활용해 가독성을 높일 것.

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
    print("3. 텔레그램 메시지 묶음 전송 및 HTML 적용 중...")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # 1. [기사] 키워드로 텍스트를 나눕니다.
    articles = text.split('[기사]')
    articles = [a.strip() for a in articles if a.strip()]

    current_message = "📢 <b>오늘의 글로벌 마켓 & 테크 인사이트</b>\n\n"
    max_length = 3800  # 텔레그램 제한 4096자보다 여유 있게 설정
    first_message = True

    for article in articles:
        # 각 기사를 다시 구성 (구분선 추가)
        formatted_article = "----------------------------\n<b>[기사]</b> " + article + "\n\n"
        
        # 현재 메시지에 추가했을 때 용량이 넘치는지 확인
        if len(current_message) + len(formatted_article) > max_length:
            # 넘친다면 지금까지 쌓인 메시지를 전송
            payload = {
                "chat_id": chat_id,
                "text": current_message,
                "parse_mode": "HTML",
                "disable_notification": not first_message # 첫 메시지만 소리, 나머지는 무음
            }
            requests.post(url, json=payload)
            
            # 새 메시지 시작
            current_message = "📢 <b>분석 리포트 계속...</b>\n\n" + formatted_article
            first_message = False
        else:
            # 용량이 남았다면 현재 메시지에 기사 추가
            current_message += formatted_article

    # 마지막으로 남은 메시지 전송
    if current_message:
        payload = {
            "chat_id": chat_id,
            "text": current_message,
            "parse_mode": "HTML",
            "disable_notification": not first_message
        }
        requests.post(url, json=payload)
        print("✅ 모든 뉴스 묶음 전송 완료!")

if __name__ == "__main__":
    try:
        news_data = get_news()
        summary = summarize_news(news_data)
        send_telegram(summary)
    except Exception as e:
        print(f"최종 오류 발생: {e}")