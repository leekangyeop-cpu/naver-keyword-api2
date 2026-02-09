from flask import Flask, request, jsonify
import time
import hmac
import hashlib
import base64
import requests
import os

app = Flask(__name__)

# 환경변수
NAVER_API_KEY = os.environ.get("NAVER_API_KEY", "")
NAVER_SECRET_KEY = os.environ.get("NAVER_SECRET_KEY", "")
NAVER_CUSTOMER_ID = os.environ.get("NAVER_CUSTOMER_ID", "")

def generate_signature(timestamp, method, uri):
    message = f"{timestamp}.{method}.{uri}"
    signature = hmac.new(
        NAVER_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

@app.route('/')
def home():
    return jsonify({
        "status": "ok", 
        "message": "Naver Keyword API",
        "endpoints": ["/api/analyze"]
    })

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        keywords = data.get("keywords", [])
    except:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400
    
    if not keywords:
        return jsonify({"status": "error", "message": "No keywords"}), 400
    
    if not all([NAVER_API_KEY, NAVER_SECRET_KEY, NAVER_CUSTOMER_ID]):
        return jsonify({"status": "error", "message": "API keys missing"}), 500
    
    base_url = "https://api.naver.com"
    uri = "/keywordstool"
    results = []
    
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i+5]
        timestamp = str(int(time.time() * 1000))
        
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Timestamp": timestamp,
            "X-API-KEY": NAVER_API_KEY,
            "X-Customer": NAVER_CUSTOMER_ID,
            "X-Signature": generate_signature(timestamp, "GET", uri)
        }
        
        try:
            hint_keywords = ",".join([k.strip().replace(" ", "") for k in batch])
            res = requests.get(
                base_url + uri,
                headers=headers,
                params={"hintKeywords": hint_keywords, "showDetail": "1"}
            )
            
            if res.status_code == 200:
                for item in res.json().get("keywordList", []):
                    if item["relKeyword"].replace(" ", "") in [k.replace(" ", "") for k in batch]:
                        pc = int(str(item.get("monthlyPcQcCnt", "0")).replace("<", ""))
                        mo = int(str(item.get("monthlyMobileQcCnt", "0")).replace("<", ""))
                        results.append([
                            item["relKeyword"],
                            pc,
                            mo,
                            pc + mo,
                            item.get("compIdx", "N/A")
                        ])
        except Exception as e:
            print(f"Error: {e}")
    
    results.sort(key=lambda x: x[3], reverse=True)
    return jsonify({"status": "success", "data": results})
```

**Commit changes** 클릭!

---

### 3️⃣ Vercel에 새로 배포

1. [vercel.com/dashboard](https://vercel.com/dashboard) 접속
2. **Add New** → **Project**
3. **Import Git Repository** → `naver-api` 선택
4. **그냥 Deploy 클릭!** (설정 건드리지 마세요)

배포 진행 중 화면이 보일 겁니다. **초록색 체크 표시** 뜰 때까지 기다리세요 (1~2분).

---

### 4️⃣ 환경변수 설정

배포 완료 후:

1. 프로젝트 클릭 → **Settings** 탭
2. 왼쪽 메뉴 → **Environment Variables**
3. 다음 3개 추가:

| Name | Value |
|------|-------|
| `NAVER_API_KEY` | 실제 API 키 |
| `NAVER_SECRET_KEY` | 실제 Secret 키 |
| `NAVER_CUSTOMER_ID` | 실제 고객 ID |

4. **Save** 클릭
5. **Deployments** 탭 → 최신 배포 옆 **⋯** → **Redeploy**

---

### 5️⃣ 테스트

배포된 URL (예: `https://naver-api-xxx.vercel.app`) 복사 후:

**브라우저에서:**
```
https://naver-api-xxx.vercel.app/
