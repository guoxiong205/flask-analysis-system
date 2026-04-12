import csv
from snownlp import SnowNLP
from dimension import extract_dimensions

def batch_analyze(file_path):
    comments = []
    with open(file_path, 'r', encoding='utf-8') as f:
        comments = f.readlines()

    analysis_results = []
    for comment in comments:
        sentiment, score, dimensions = analyze(comment.strip())
        analysis_results.append([comment.strip(), sentiment, score, ', '.join(dimensions)])

    result_file = 'batch_analysis_results.csv'
    with open(result_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Comment', 'Sentiment', 'Score', 'Dimensions'])
        writer.writerows(analysis_results)

    return result_file

def analyze(comment):
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