import feedparser
from google import genai  # 최신 라이브러리 사용
import requests
import os

def get_news():
    print("뉴스 데이터를 가져오는 중...")
    # when:24h 를 붙이면 정확히 최근 24시간 이내의 기사만 가져옵니다.
    query = "(경제|IT|테크|반도체)+when:24h"
    
    # URL 인코딩 이슈를 방지하기 위해 f-string 사용
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        return "최근 24시간 내에 수집된 뉴스가 없습니다."
    
    return "\n\n".join([f"제목: {e.title}\n링크: {e.link}" for e in feed.entries[:8]])

def summarize_news(news_text):
    print("Gemini AI 요약 생성 중...")
    # 최신 Client 객체 생성 방식
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    prompt = f"다음 뉴스를 경제와 테크로 분류해서 요약하고 링크를 포함해줘:\n\n{news_text}"
    
    # 모델명 앞에 models/ 를 붙이지 않고 이름만 입력
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return response.text

def send_telegram(text):
    print("텔레그램 전송 중...")
    url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"
    payload = {"chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": text}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("✅ 전송 성공!")
    else:
        print(f"❌ 전송 실패: {res.text}")

if __name__ == "__main__":
    try:
        news_data = get_news()
        summary = summarize_news(news_data)
        send_telegram(summary)
    except Exception as e:
        print(f"❗ 오류 발생: {e}")