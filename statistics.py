import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ⭐ 使用本地字体文件（关键修复点）
#font_path = "simhei.ttf"
#my_font = fm.FontProperties(fname=font_path)
import os

font_path = os.path.join(os.path.dirname(__file__), "simhei.ttf")
my_font = fm.FontProperties(fname=font_path)

plt.rcParams['axes.unicode_minus'] = False  # 负号显示

def generate_statistics(analysis_results):

    # ===== 情感统计 =====
    sentiment_counts = {'正面': 0, '负面': 0, '中性': 0}

    # ===== 维度统计 =====
    dimension_counts = {
        '服务': 0,
        '价格': 0,
        '环境': 0,
        '菜品': 0
    }

    for result in analysis_results:
        sentiment = result[1]
        dimension = result[3]

        # 情感统计
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

        # 维度统计
        for d in dimension.split(', '):
            if d in dimension_counts:
                dimension_counts[d] += 1

    # =========================
    # 🎯 1. 画饼图
    # =========================
    plt.figure()

    plt.pie(
        sentiment_counts.values(),
        labels=sentiment_counts.keys(),
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontproperties': my_font}  # ⭐关键！
    )

    plt.title('情感分布', fontproperties=my_font)
    plt.savefig('static/sentiment_pie_chart.png')
    plt.close()

    # =========================
    # 🎯 2. 画柱状图
    # =========================
    plt.figure()

    plt.bar(
        dimension_counts.keys(),
        dimension_counts.values()
    )

    plt.title('评价维度分布', fontproperties=my_font)
    plt.xlabel('维度', fontproperties=my_font)
    plt.ylabel('数量', fontproperties=my_font)

    plt.savefig('static/dimension_bar_chart.png')
    plt.close()


# =========================
# 🎯 词云（保持原逻辑）
# =========================
from wordcloud import WordCloud

def generate_wordcloud(comments):
    text = " ".join(comments)

    wc = WordCloud(
        font_path="simhei.ttf",
        width=800,
        height=400,
        background_color="white"
    ).generate(text)

    wc.to_file("static/wordcloud.png")