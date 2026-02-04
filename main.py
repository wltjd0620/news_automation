import feedparser
import google.generativeai as genai
import requests
import os

# 1. 뉴스 수집 함수
def get_news():
    print("뉴스 데이터를 가져오는 중...")
    # 경제/테크 관련 구글 뉴스 RSS
    rss_url = "https://news.google.com/rss/search?q=경제+IT+테크&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    # 최신 뉴스 8개 추출
    for entry in feed.entries[:8]:
        news_items.append(f"제목: {entry.title}\n링크: {entry.link}")
    
    return "\n\n".join(news_items)

# 2. Gemini 뉴스 요약 함수
def summarize_news(news_text):
    print("Gemini AI를 이용해 요약 생성 중...")
    # 환경 변수에서 API 키 로드
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    # 404 에러 방지를 위해 'models/' 경로 명시
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    prompt = f"""
    당신은 유능한 경제/테크 뉴스 큐레이터입니다. 아래 뉴스 리스트를 직장인이 읽기 좋게 요약해주세요.
    - '경제 뉴스'와 '테크 뉴스' 섹션으로 구분할 것.
    - 각 뉴스당 핵심 요약을 1문장으로 작성하고 바로 아래에 원본 링크를 넣을 것.
    - 전체적인 어조는 친절하고 전문적인 뉴스레터 스타일로 작성할 것.
    
    뉴스 리스트:
    {news_text}
    """
    
    response = model.generate_content(prompt)
    
    # 토큰 사용량 정보 추출
    usage = response.usage_metadata
    token_info = (
        f"\n\n---"
        f"\n📊 사용 토큰: {usage.total_token_count}"
        f"\n💡 일일 무료 한도: 1,500회 요청 가능"
    )
    
    return response.text + token_info

# 3. 텔레그램 전송 함수
def send_telegram(text):
    print("텔레그램으로 메시지 전송 중...")
    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text,
        "disable_web_page_preview": False  # 링크 미리보기 활성화
    }
    
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("✅ 성공적으로 전송되었습니다.")
    else:
        print(f"❌ 전송 실패: {res.text}")

if __name__ == "__main__":
    try:
        news_data = get_news()
        if not news_data:
            print("가져온 뉴스가 없습니다.")
        else:
            summary = summarize_news(news_data)
            send_telegram(summary)
    except Exception as e:
        print(f"❗ 오류 발생: {e}")