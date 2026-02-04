import requests

# ==========================================
# 딱 두 가지만 입력하세요
# ==========================================
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
# ==========================================

def test_connection():
    print("🚀 텔레그램 서버와 연결 시도 중...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "Hello! 텔레그램 통신 테스트 성공입니다. ✅"
    }
    
    try:
        response = requests.post(url, json=payload)
        # HTTP 응답 코드가 200이 아니면 예외 발생
        response.raise_for_status() 
        
        print("✅ 성공: 텔레그램 메시지가 발송되었습니다!")
        print(f"응답 결과: {response.json()}")
        
    except requests.exceptions.HTTPError as err:
        print(f"❌ 실패: HTTP 에러 발생 ({err})")
        print("힌트: 토큰이나 ID가 틀렸을 가능성이 높습니다.")
    except Exception as e:
        print(f"❌ 실패: 기타 에러 발생 ({e})")

if __name__ == "__main__":
    test_connection()