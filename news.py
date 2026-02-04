import feedparser
from google import genai
import requests
import os

def get_news():
    print("1. 실시간 뉴스 데이터를 가져오는 중...")
    # 최근 24시간 내의 경제/IT/테크 뉴스 검색
    query = "(경제|IT|테크|반도체)+when:24h"
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        return ""

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
    당신은 전문 산업 분석가입니다. 다음 뉴스들을 분석하여 보고서를 작성하세요.
    
    [작성 규칙]
    1. 각 기사의 시작은 반드시 [기사] 라는 문구로 시작할 것.
    2. 뉴스 구성:
       - [제목]: 핵심 내용을 담은 요약 제목
       - [핵심 요약]: 기사 내용을 1문장으로 정리
       - [산업 영향력 분석]: 
          * 경제 기사: 관련 국가와 산업에 미칠 긍정적/부정적 영향 분석
          * 테크 기사: 기술이 해당 산업에 미칠 변화 분석
       - [원본 링크]: 제공된 링크 그대로 기입
    3. 경제와 테크 섹션을 나누어 작성할 것.

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
    print("3. 텔레그램 기사 단위 분할 전송 중...")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # [기사] 단어를 기준으로 텍스트 분할
    articles = text.split('[기사]')
    
    # 빈 요소 제거 및 정리
    articles = [a.strip() for a in articles if a.strip()]

    current_message = "📢 오늘의 산업 영향력 뉴스 요약\n\n"
    max_length = 3800  # 텔레그램 제한 4096자 대비 여유분 확보

    for article in articles:
        formatted_article = "----------------------------\n[기사] " + article + "\n\n"
        
        # 현재 메시지에 새 기사를 추가했을 때 용량 초과 여부 확인
        if len(current_message) + len(formatted_article) > max_length:
            # 초과 시 지금까지의 메시지 전송
            requests.post(url, json={"chat_id": chat_id, "text": current_message})
            # 새 메시지 시작
            current_message = "📢 뉴스 요약 계속...\n\n" + formatted_article
        else:
            current_message += formatted_article

    # 마지막 남은 기사 꾸러미 전송
    if current_message:
        requests.post(url, json={"chat_id": chat_id, "text": current_message})
        print("✅ 모든 메시지 전송 완료")

if __name__ == "__main__":
    try:
        news_data = get_news()
        summary = summarize_news(news_data)
        send_telegram(summary)
    except Exception as e:
        print(f"최종 오류 발생: {e}")