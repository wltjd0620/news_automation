import feedparser
from google import genai
import requests
import os

def get_news():
    print("1. 실시간 뉴스 데이터를 가져오는 중...")

    queries = {
        "경제/비즈니스": "(경제|비즈니스|금융|증시|환율)+when:24h",
        "테크/기술": "(반도체|IT|AI|디스플레이|임베디드)+when:24h"
    }
    
    all_news_items = []
    
    for category, q in queries.items():
        rss_url = f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(rss_url)
        
        # 각 카테고리에서 상위 5개씩 추출
        selected = feed.entries[:5]
        print(f"✅ {category} 뉴스 {len(selected)}개 선별 완료")
        
        for entry in selected:
            all_news_items.append(f"[{category}] 원본제목: {entry.title}\n링크: {entry.link}")
    
    return "\n\n".join(all_news_items)

def summarize_news(news_text):
    if not news_text:
        return "최근 24시간 내에 수집된 새로운 뉴스가 없습니다."

    print("2. Gemini AI 산업 영향력 분석 및 요약 중...")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    prompt = f"""
    당신은 IT 및 첨단 기술 전문 산업 분석가입니다. 
    제공된 10개의 뉴스 리스트를 [경제/비즈니스] 5개와 [테크/기술] 5개로 나누어,
    기술직 직장인이자 연구자를 위한 '데일리 뉴스 요약'을 작성하세요.

    [작성 가이드라인]
    1. 각 기사는 반드시 [기사] 문구로 시작할 것. ( 메시지 분할을 위한 구분자 )
    2. 섹션 구분: '경제/비즈니스'와 '테크/기술' 중 어느 카테고리에 속하는지 명시하세요.
    3. 뉴스 구성 요소 (반드시 지킬 것, 각 항목 사이 빈 줄 필수):
       <b>핵심을 찌르는 한 줄 제목</b>

       [핵심 요약]
       기사 내용을 1문장으로 명확히 요약

       [인사이트]
          * 경제 기사: 단순 지표(환율, 금리 등)를 넘어 현재 글로벌 자본과 권력이 어디로 이동하고 있는지, 시장 전반의 심리(Risk-on/off)와 분위기를 분석하세요. 
          * 테크 기사: 이 기술이나 이슈가 특정 산업에 가져올 변화와 시사점 분석

       [링크]
       <a href="원문_링크">기사 원문 보기</a>

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
    print("3. 카테고리별 메시지 분할 전송 시작...")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    articles = text.split('[기사]')
    articles = [a.strip() for a in articles if a.strip()]
    
    # 5개씩 묶어서 전송 (경제 5개 / 테크 5개)
    titles = ["📈 경제/비즈니스 인사이트", "🚀 테크/기술 산업 리포트"]
    current_msg = ""
    max_len = 3800
    
    # 기사들을 5개씩 나눕니다 (0~4번: 경제, 5~9번: 테크)
    for idx, start_idx in enumerate([0, 5]):
        category_chunk = articles[start_idx : start_idx + 5]
        current_msg = f"<b>{titles[idx]}</b>\n\n"
        
        for article in category_chunk:
            formatted_article = "----------------------------\n<b>[기사]</b> " + article + "\n\n"
            
            # 한 카테고리 내에서도 용량이 넘치면 끊어서 전송
            if len(current_msg) + len(formatted_article) > max_len:
                requests.post(url, json={
                    "chat_id": chat_id,
                    "text": current_msg,
                    "parse_mode": "HTML",
                    "disable_notification": True
                })
                current_msg = f"<b>{titles[idx]} (계속)</b>\n\n" + formatted_article
            else:
                current_msg += formatted_article
        
        # 한 카테고리(5개)가 끝나면 남은 내용을 즉시 전송하여 다음 카테고리와 분리
        if current_msg:
            requests.post(url, json={
                "chat_id": chat_id,
                "text": current_msg,
                "parse_mode": "HTML",
                "disable_notification": False if idx == 0 else True
            })
            print(f"📡 {titles[idx]} 전송 완료")

if __name__ == "__main__":
    try:
        news_data = get_news()
        summary = summarize_news(news_data)
        send_telegram(summary)
    except Exception as e:
        print(f"최종 오류 발생: {e}")