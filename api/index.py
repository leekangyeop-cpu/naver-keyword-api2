from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Vercel 환경변수에서 키를 가져옵니다
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

@app.route('/api/analyze', methods=['POST'])
def analyze_shopping_trend():
    # 1. 구글 시트에서 보낸 키워드 받기
    data = request.get_json()
    keywords = data.get("keywords", []) # 예: ["원피스", "청바지"]
    category_code = data.get("category_code", "50000000") # 기본: 패션의류

    if not keywords:
        return jsonify({"status": "error", "message": "키워드가 없습니다."}), 400
    
    if not CLIENT_ID or not CLIENT_SECRET:
        return jsonify({"status": "error", "message": "Vercel 환경변수 설정이 안 되어 있습니다."}), 500

    # 2. 네이버 쇼핑 인사이트 API 호출 준비
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

    # 요청 본문 만들기 (최근 1년 데이터)
    body = {
        "startDate": "2024-01-01", 
        "endDate": "2024-12-31", # 필요에 따라 날짜 자동화 가능
        "timeUnit": "month",
        "category": category_code,
        "keyword": [{"name": k, "param": [k]} for k in keywords[:5]] # 최대 5개 그룹
    }

    try:
        # 3. 네이버에 데이터 요청
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            result_data = response.json()
            # 결과 정리
            parsed_results = []
            if "results" in result_data:
                for item in result_data["results"]:
                    title = item["title"]
                    data_points = item["data"]
                    if data_points:
                        # 가장 최근 달의 지수
                        last_ratio = data_points[-1]["ratio"]
                        parsed_results.append([title, last_ratio, "분석성공"])
                    else:
                        parsed_results.append([title, 0, "데이터없음"])
            
            return jsonify({"status": "success", "data": parsed_results})
        else:
            return jsonify({"status": "error", "message": f"네이버 오류: {response.status_code}", "detail": response.text}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel 구동용 핸들러
handler = app
