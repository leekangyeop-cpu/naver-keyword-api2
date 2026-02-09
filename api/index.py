from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Naver DataLab Shopping Insight API",
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
    
    if not all([CLIENT_ID, CLIENT_SECRET]):
        return jsonify({"status": "error", "message": "API keys missing"}), 500
    
    # 최근 3개월 날짜 설정
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # 데이터랩 API 요청 URL
    url = "https://openapi.naver.com/v1/datalab/shopping/categories"
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }
    
    results = []
    
    # 각 키워드별로 처리
    for keyword in keywords[:5]:  # 최대 5개까지
        body = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "timeUnit": "month",
            "category": [
                {
                    "name": keyword,
                    "param": ["50000000"]  # 전체 카테고리
                }
            ],
            "device": "pc",
            "ages": ["20", "30", "40"],
            "gender": "f"
        }
        
        try:
            res = requests.post(url, headers=headers, json=body)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("results") and len(data["results"]) > 0:
                    # 최근 데이터의 검색 비율
                    ratio_data = data["results"][0].get("data", [])
                    if ratio_data:
                        latest = ratio_data[-1]  # 가장 최근 데이터
                        ratio = latest.get("ratio", 0)
                        results.append([
                            keyword,
                            ratio,
                            "쇼핑 검색 비율",
                            latest.get("period", "")
                        ])
            else:
                print(f"API Error {res.status_code}: {res.text}")
                
        except Exception as e:
            print(f"Exception: {str(e)}")
    
    # 비율 기준 내림차순 정렬
    results.sort(key=lambda x: x[1], reverse=True)
    
    return jsonify({"status": "success", "data": results})

handler = app
```

**Commit changes** 클릭!

---

### 2️⃣ Vercel 환경변수 설정

Vercel 대시보드:
1. **Settings** → **Environment Variables**
2. 다음 2개 추가:

#### 첫 번째 변수
```
Key: CLIENT_ID
Value: eX9u6nzuYFHGo86cUuya
```
**Save** 클릭!

#### 두 번째 변수
```
Key: CLIENT_SECRET  
Value: (네이버 개발자센터에서 "보기" 버튼 눌러서 복사)
