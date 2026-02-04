from google import genai
import requests
import os

def get_english_expressions():
    print("영어 표현 생성 중...")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    prompt = """
    당신은 전문 영어 강사입니다. 글로벌 테크 기업의 엔지니어가 쓰기 좋은 유용한 영어 표현 10개를 선정해 주세요.
    
    [작성 규칙]
    1. 구성: [영어 문장] - [뜻] - [간단한 상황 설명이나 예문]
    2. 내용: 7개는 비즈니스 회화, 3개는 IT/기술 관련 표현으로 구성할 것.
    3. 형식: 텔레그램에서 읽기 좋게 번호를 매기고 이모지를 활용할 것.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return "🇺🇸 오늘의 테크 영어 표현 (10)\n\n" + response.text
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def send_telegram(text):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("ENGLISH_CHAT_ID") # 영어 전용 방 ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    requests.post(url, json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    })

if __name__ == "__main__":
    content = get_english_expressions()
    if content:
        send_telegram(content)
        print("✅ 영어 표현 전송 완료")