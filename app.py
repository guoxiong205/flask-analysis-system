from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, request, render_template, send_file
from snownlp import SnowNLP
from dimension import extract_dimensions
import os
import csv
import matplotlib.pyplot as plt
from statistics import generate_statistics

import json
from datetime import datetime

def save_history(filename):
    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file": filename
    }

    try:
        with open("history.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    data.append(record)

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
app = Flask(__name__)
app.secret_key = '123456'  # 随便写，但必须有
def analyze(comment):
    """情感分析函数"""
    s = SnowNLP(comment)
    score = s.sentiments

    if score > 0.6:
        sentiment = "正面"
    elif score < 0.4:
        sentiment = "负面"
    else:
        sentiment = "中性"

    dimensions = extract_dimensions(comment)

    return sentiment, score, dimensions

# ================== 店铺推荐算法 ==================
def analyze_shops(data):
    shops = {}

    for shop, comment in data:
        score = SnowNLP(comment).sentiments

        if shop not in shops:
            shops[shop] = []

        shops[shop].append(score)

    result = []

    for shop, scores in shops.items():
        avg_score = sum(scores) / len(scores)
        positive_rate = len([s for s in scores if s > 0.6]) / len(scores)

        final_score = avg_score * 0.7 + positive_rate * 0.3

        result.append((shop, round(final_score, 3), round(positive_rate, 3)))

    result.sort(key=lambda x: x[1], reverse=True)

    return result
# =================================================

@app.route('/', methods=['GET', 'POST'])
def index():
    from flask import session, redirect

    if 'user' not in session:
        return redirect('/login')

    import json

    # 读取历史
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            history = json.load(f)
    except:
        history = []

    # ⭐ 处理单条评论分析
    if request.method == 'POST':
        comment = request.form.get('comment')

        if comment:
            sentiment, score, dimensions = analyze(comment)

            return render_template(
                'index.html',
                result={
                    'comment': comment,
                    'sentiment': sentiment,
                    'score': score,
                    'dimensions': dimensions
                },
                history=history
            )

    return render_template('index.html', history=history)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 简单写死账号（够用）
        if username == 'admin' and password == '123456':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return "账号或密码错误"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/batch', methods=['POST'])
def batch():
    """批量评论分析"""
    file = request.files.get('file')
    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        #analysis_results = batch_analyze(file_path)
        from datetime import datetime

        filename = f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        result_file = f"static/{filename}"
        from datetime import datetime  # 可以提前到文件最上面（推荐）

        filename = f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        result_file = f"static/{filename}"

        analysis_results, bad_dimensions = batch_analyze(file_path, result_file)

        print("当前文件路径:", file_path)
        # ✅ 加在这里（紧跟下面）
        print("本次分析结果:", analysis_results[:5])
        print("本次问题维度:", bad_dimensions)

        from statistics import generate_statistics
        generate_statistics(analysis_results)

        #return render_template('index.html')
        save_history(filename)
        import json

        with open("history.json", "r", encoding="utf-8") as f:
            history = json.load(f)

        # ================= 推荐店铺 =================
        with open('shops.json', 'r', encoding='utf-8') as f:
            shops_data = json.load(f)

        recommended_shops = []

        for shop in shops_data:
            match = False
            for tag in shop['tags']:
                if any(dim in tag for dim in bad_dimensions):
                    match = True
                    break
            if match:
                recommended_shops.append(shop)
        # ==========================================

        return render_template('index.html',
                               result_file=filename,
                               history=history,
                               bad_dimensions=bad_dimensions,
                               recommended_shops=recommended_shops)

    return "No file uploaded", 400

def batch_analyze(file_path, result_file):
    """批量分析评论并保存结果到 CSV 文件"""
    comments = []
    with open(file_path, 'r', encoding='utf-8') as f:
        comments = f.readlines()

    analysis_results = []
    for comment in comments:
        print("正在分析评论:", comment.strip())
        sentiment, score, dimensions = analyze(comment.strip())
        analysis_results.append([comment.strip(), sentiment, score, ', '.join(dimensions)])
        # ================== 统计问题维度 ==================
        dimension_count = {}

        for row in analysis_results:
            if row[1] != '负面':  # ⭐ 只统计差评
                continue

            dims = row[3].split(', ')
            for d in dims:
                if d:
                    if d not in dimension_count:
                        dimension_count[d] = 0
                    dimension_count[d] += 1

        # 找出出现最多的维度（认为是问题点）
        bad_dimensions = sorted(dimension_count, key=dimension_count.get, reverse=True)[:2]
        # =================================================
    #result_file = 'static/batch_analysis_results.csv'
    with open(result_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Comment', 'Sentiment', 'Score', 'Dimensions'])
        writer.writerows(analysis_results)
        # 生成词云
        from statistics import generate_wordcloud
        comments = [row[0] for row in analysis_results]
        generate_wordcloud(comments)

    # Generate Statistics
   # generate_statistics(analysis_results)

    #return result_file这是修改前的代码
    return analysis_results, bad_dimensions#这是修改后的代码

# ================== 推荐系统页面 ==================
@app.route('/recommend')
def recommend():
    import json

    with open('shops.json', 'r', encoding='utf-8') as f:
        shops_data = json.load(f)

    result = []

    for shop in shops_data:
        scores = []
        for comment in shop['comments']:
            score = SnowNLP(comment).sentiments
            scores.append(score)

        avg_score = sum(scores) / len(scores)
        positive_rate = len([s for s in scores if s > 0.6]) / len(scores)

        final_score = avg_score * 0.7 + positive_rate * 0.3

        result.append({
            "name": shop["name"],
            "image": shop["image"],
            "tags": shop["tags"],
            "comments": shop["comments"],
            "score": round(final_score, 3),
            "rate": round(positive_rate, 2)
        })

    result.sort(key=lambda x: x["score"], reverse=True)

    return render_template('recommend.html', shops=result)
# =================================================

if __name__ == '__main__':
    app.run(debug=True)
