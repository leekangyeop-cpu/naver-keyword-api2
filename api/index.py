from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Naver Blog Search API",
        "endpoints": ["/api/analyze"]
    })

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        keywords = data.get("keywords", [])
    except Exception as e:
        return jsonify({"status": "error", "message": f"Invalid JSON: {str(e)}"}), 400
    
    if not keywords:
        return jsonify({"status": "error", "message": "No keywords provided"}), 400
    
    if not CLIENT_ID or not CLIENT_SECRET:
        return jsonify({
            "status": "error", 
            "message": "API keys not configured",
            "client_id_exists": bool(CLIENT_ID),
            "client_secret_exists": bool(CLIENT_SECRET)
        }), 500
    
    results = []
    
    for keyword in keywords[:10]:
        try:
            headers = {
                "X-Naver-Client-Id": CLIENT_ID,
                "X-Naver-Client-Secret": CLIENT_SECRET
            }
            
            # 블로그 검색 API (간단하고 안정적)
            response = requests.get(
                "https://openapi.naver.com/v1/search/blog.json",
                headers=headers,
                params={"query": keyword, "display": 1},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                total = result.get("total", 0)
                results.append([
                    keyword,
                    total,
                    "블로그 검색수"
                ])
            else:
                results.append([
                    keyword,
                    0,
                    f"오류 {response.status_code}"
                ])
                
        except Exception as e:
            results.append([
                keyword,
                0,
                f"에러: {str(e)[:20]}"
            ])
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    return jsonify({"status": "success", "data": results})

handler = app
```

**Commit changes**

---

## 🧪 테스트

### 브라우저에서 직접 테스트
```
https://naver-keyword-api2.vercel.app/
