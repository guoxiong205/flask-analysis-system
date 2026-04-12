import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ⭐ 解决中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False    # 负号显示

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
    # 🎯 1. 画饼图（单独一张）
    # =========================
    plt.figure()  # ⭐ 新建画布

    plt.pie(
        sentiment_counts.values(),
        labels=sentiment_counts.keys(),
        autopct='%1.1f%%',
        startangle=90
    )

    plt.title('情感分布')
    plt.savefig('static/sentiment_pie_chart.png')
    plt.close()  # ⭐ 关闭画布

    # =========================
    # 🎯 2. 画柱状图（单独一张）
    # =========================
    plt.figure()  # ⭐ 再开一个新画布

    plt.bar(
        dimension_counts.keys(),
        dimension_counts.values()
    )

    plt.title('评价维度分布')
    plt.xlabel('维度')
    plt.ylabel('数量')

    plt.savefig('static/dimension_bar_chart.png')
    plt.close()  # ⭐ 关闭
    # 👇👇👇 写在这里（函数外面！）

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