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

    if not keywords:
        return jsonify({"status": "error", "message": "키워드가 없습니다."}), 400

    if not CLIENT_ID or not CLIENT_SECRET:
        return jsonify({"status": "error", "message": "API 키가 설정되지 않았습니다."}), 500

    # 2. 네이버 쇼핑 인사이트 API 호출 (보내주신 키 용도)
    url = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/json"
    }

    # 요청 본문 (최근 1개월 데이터 예시)
    body = {
        "startDate": "2024-01-01", 
        "endDate": "2024-12-31",
        "timeUnit": "month",
        "category": "50000000", # 기본 패션의류 (필요시 변경 가능)
        "keyword": [{"name": k, "param": [k]} for k in keywords[:5]]
    }

    try:
        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            result_data = response.json()
            parsed_results = []
            # 결과 데이터 정리
            if "results" in result_data:
                for item in result_data["results"]:
                    title = item["title"]
                    ratio = item["data"][-1]["ratio"] if item["data"] else 0
                    parsed_results.append([title, ratio, "분석성공"])

            return jsonify({"status": "success", "data": parsed_results})
        else:
            return jsonify({"status": "error", "message": "네이버 인증 실패 (키 확인 필요)"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
