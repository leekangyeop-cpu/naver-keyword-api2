from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "Naver API"})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    keywords = data.get("keywords", [])
    
    if not keywords:
        return jsonify({"status": "error", "message": "No keywords"}), 400
    
    if not CLIENT_ID or not CLIENT_SECRET:
        return jsonify({"status": "error", "message": "Keys missing"}), 500
    
    results = []
    
    for keyword in keywords[:5]:
        try:
            headers = {
                "X-Naver-Client-Id": CLIENT_ID,
                "X-Naver-Client-Secret": CLIENT_SECRET
            }
            
            res = requests.get(
                "https://openapi.naver.com/v1/search/blog.json",
                headers=headers,
                params={"query": keyword, "display": 1}
            )
            
            if res.status_code == 200:
                total = res.json().get("total", 0)
                results.append([keyword, total, "OK"])
            else:
                results.append([keyword, 0, "Error"])
        except:
            results.append([keyword, 0, "Fail"])
    
    results.sort(key=lambda x: x[1], reverse=True)
    return jsonify({"status": "success", "data": results})

handler = app
```

**Commit new file**

---

### 3️⃣ 1분 대기 후 테스트

브라우저:
```
https://naver-keyword-api2.vercel.app/
