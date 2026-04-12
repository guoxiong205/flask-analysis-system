def extract_dimensions(comment):
    """从评论中提取维度"""
    # 定义维度关键词
    service_keywords = ['服务', '态度', '上菜', '服务员']
    price_keywords = ['价格', '贵', '便宜', '性价比']
    environment_keywords = ['环境', '氛围', '干净', '装修']
    food_keywords = ['菜', '味道', '好吃', '难吃']

    result = []

    # 判断评论中是否包含相关维度的关键词
    if any(word in comment for word in service_keywords):
        result.append("服务")
    if any(word in comment for word in price_keywords):
        result.append("价格")
    if any(word in comment for word in environment_keywords):
        result.append("环境")
    if any(word in comment for word in food_keywords):
        result.append("菜品")

    return result