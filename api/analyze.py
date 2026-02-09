from flask import Flask, request, jsonify
import time
import hmac
import hashlib
import base64
import requests
import os

app = Flask(__name__)

# 환경변수 (Vercel에서 설정)
NAVER_API_KEY = os.environ.get("NAVER_API_KEY", "")
NAVER_SECRET_KEY = os.environ.get("NAVER_SECRET_KEY", "")
NAVER_CUSTOMER_ID = os.environ.get("NAVER_CUSTOMER_ID", "")

def generate_signature(timestamp, method, uri):
    """네이버 API 서명 생성"""
    message = f"{timestamp}.{method}.{uri}"
    signature = hmac.new(
        NAVER_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_keywords():
    # CORS 처리
    if request.method == 'OPTIONS':
        return '', 204
    
    # 요청 데이터 받기
    try:
        data = request.get_json()
        keywords = data.get("keywords", [])
    except:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    
    if not keywords:
        return jsonify({"status": "error", "message": "No keywords provided"}), 400
    
    # API 키 확인
    if not all([NAVER_API_KEY, NAVER_SECRET_KEY, NAVER_CUSTOMER_ID]):
        return jsonify({"status": "error", "message": "API keys not configured"}), 500
    
    base_url = "https://api.naver.com"
    uri = "/keywordstool"
    method = "GET"
    
    results = []
    
    # 5개씩 끊어서 요청 (네이버 API 제한)
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        timestamp = str(int(time.time() * 1000))
        
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Timestamp": timestamp,
            "X-API-KEY": NAVER_API_KEY,
            "X-Customer": NAVER_CUSTOMER_ID,
            "X-Signature": generate_signature(timestamp, method, uri)
        }
        
        try:
            # 쉼표로 키워드 합치기
            hint_keywords = ",".join([k.strip().replace(" ", "") for k in batch])
            res = requests.get(
                base_url + uri, 
                headers=headers, 
                params={"hintKeywords": hint_keywords, "showDetail": "1"}
            )
            
            if res.status_code == 200:
                keyword_list = res.json().get("keywordList", [])
                for item in keyword_list:
                    # 요청한 키워드와 일치하는 것만
                    if item["relKeyword"].replace(" ", "") in [k.replace(" ", "") for k in batch]:
                        pc = int(str(item.get("monthlyPcQcCnt", "0")).replace("<", ""))
                        mo = int(str(item.get("monthlyMobileQcCnt", "0")).replace("<", ""))
                        total = pc + mo
                        results.append([
                            item["relKeyword"],
                            pc,
                            mo,
                            total,
                            item.get("compIdx", "N/A")
                        ])
            else:
                print(f"Naver API Error {res.status_code}: {res.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
    
    # 전체 검색수 기준 내림차순 정렬
    results.sort(key=lambda x: x[3], reverse=True)
    
    return jsonify({"status": "success", "data": results})

# Health check
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Naver Keyword API is running"})
```

**Commit** 클릭!

---

## ⚙️ 3단계: Vercel 배포

### 1️⃣ Vercel 연결

1. [vercel.com](https://vercel.com) 로그인
2. **Add New** → **Project**
3. GitHub에서 `naver-keyword-api` 선택
4. **Import** 클릭
5. **Deploy** 클릭 (아무 설정 안 해도 OK!)

### 2️⃣ 환경변수 설정

배포 완료 후:
1. 프로젝트 페이지 → **Settings** → **Environment Variables**
2. 다음 3개 추가:
```
NAVER_API_KEY = 여기에_실제_값
NAVER_SECRET_KEY = 여기에_실제_값
NAVER_CUSTOMER_ID = 여기에_실제_값
