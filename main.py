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
    
    prompt = f"""
    당신은 전문 산업 분석가이자 기술 전략가입니다. 
    제공된 뉴스 리스트를 바탕으로 바쁜 직장인을 위한 '산업 영향력 보고서'를 작성하세요.

    [작성 가이드라인]
    1. 섹션 구분: '경제/비즈니스'와 '테크/기술'로 분류할 것.
    2. 뉴스 구성:
       - [제목]: 뉴스 제목을 요약하여 표기
       - [핵심 요약]: 해당 기사의 핵심 내용을 1문장으로 정리
       - [산업 영향력 분석]: 
          * 경제 기사: 이 뉴스가 어떤 특정 산업(예: 반도체, 자동차, 금융 등)에 긍정적/부정적 영향을 줄지 분석
          * 테크 기사: 이 기술이 실제 산업 현장(예: 스마트 팩토리, Edge AI, 디스플레이 등)에 미칠 변화와 파급력 분석
       - [원본 링크]: 해당 기사로 바로 이동할 수 있는 링크
    3. 톤앤매너: 전문적이고 객관적인 문체를 사용하되, 가독성을 위해 불렛포인트를 활용할 것.

    뉴스 리스트:
    {news_text}
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.0-flash",
            contents=prompt
        )
        
        # 텔레그램 메시지 길이 제한(4096자)을 고려하여 토큰 정보와 함께 반환
        usage = response.usage_metadata
        token_info = f"\n\n---\n📊 분석 완료 (사용 토큰: {usage.total_token_count})"
        return response.text + token_info
        
    except Exception as e:
        print(f"AI 분석 실패: {e}")
        return "AI 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

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