from google import genai
import requests
import os

def get_english_expressions():
    print("영어 표현 생성 중...")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    prompt = """
    당신은 테크 분야 전문 영어 강사입니다. 아래 비율에 맞춰 실무 활용도가 높은 영어 표현 10개를 선정해 주세요.

    [표현 구성 비율]
    1. 일상 회화 (3개): 친구나 동료와 가볍게 나눌 수 있는 자연스러운 표현
    2. 비즈니스 회화 (5개): 회의, 보고, 메일 작성 시 유용한 격식 있는 표현
    3. IT/기술 표현 (2개): 임베디드 SW 개발, AI 연구, 디스플레이 공학 등 기술적 상황에서 쓰이는 표현

    [출력 형식 가이드]
    - 반드시 각 표현 사이에는 공백 라인을 넣어 가독성을 높일 것.
    - 형식:
      <b>번호. [영어 표현]</b>
      뜻: [한국어 의미]
      💡 <b>Usage:</b> [이 표현이 쓰이는 상황 설명 또는 예문 한 문장]

    [주의 사항]
    - 텔레그램 HTML 모드를 사용할 것이므로 <b> 태그를 적절히 활용하여 제목을 강조하세요.
    - 앞 뒤로 불필요한 설명이나 문구를 넣지 말고, 오직 표현 리스트만 출력하세요.
    - 각 표현은 명확하고 간결하게 작성하세요.
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