# import os
# import re
# import pandas as pd
# from tqdm import tqdm
 
# ================== 配置区 ==================
# BASE_DIR = r"D:\AAanancoda\大数据期末作业\数据"
 
# 分类规则：type + 可选阈值（用于边界科目）
# CATEGORY_RULES = {
# # 投资于人（Human Capital）
# "教育": {"type": "human", "threshold": None},
# "科技": {"type": "human", "threshold": 1.0},      # ≤1亿视为人才/研发
# "科学技术": {"type": "human", "threshold": 1.0},
# "科研": {"type": "human", "threshold": 1.0},
# "社保": {"type": "human", "threshold": None},
# "社会保障": {"type": "human", "threshold": None},
# "就业": {"type": "human", "threshold": None},
# "卫生": {"type": "human", "threshold": None},
# "医疗": {"type": "human", "threshold": None},
# "健康": {"type": "human", "threshold": None},
# "租赁补贴": {"type": "human", "threshold": None},

#     # 投资于物（Physical Capital）
# "交通": {"type": "physical", "threshold": None},
# "运输": {"type": "physical", "threshold": None},
# "城乡": {"type": "physical", "threshold": None},
# "社区": {"type": "physical", "threshold": None},
# "市政": {"type": "physical", "threshold": None},
# "农业": {"type": "physical", "threshold": 5.0},   # >5亿视为基建
# "林业": {"type": "physical", "threshold": 5.0},
# "水利": {"type": "physical", "threshold": 5.0},
# "农林": {"type": "physical", "threshold": 5.0},
# "资源勘探": {"type": "physical", "threshold": None},
# "工业": {"type": "physical", "threshold": None},
# "信息": {"type": "physical", "threshold": None},
# "制造业": {"type": "physical", "threshold": None},
# "住房建设": {"type": "physical", "threshold": None},
# "棚改": {"type": "physical", "threshold": None},
# "保障房": {"type": "physical", "threshold": None},  # 默认计入“物”
# }
 
# 同义词映射（支持地方表述差异）
# SYNONYMS = {
# "教育": ["教育"],
# "科技": ["科技", "科学技术", "科研"],
# "社保": ["社保", "社会保障和就业", "社会救助", "养老", "低保"],
# "卫生": ["卫生", "医疗", "卫生健康", "公共卫生", "医院", "基层医疗"],
# "交通": ["交通", "交通运输", "公路", "高速", "地铁", "铁路", "机场"],
# "城乡": ["城乡", "城乡社区", "市政", "城市更新", "基础设施"],
# "农业": ["农业", "农林水", "水利", "林业", "高标准农田", "农村公路"],
# "住房建设": ["保障房", "棚改", "住房保障", "老旧小区改造", "安居工程"]
# }
 
# 构建最终关键词 → 规则映射
# FINAL_KEYWORD_MAP = {}
# for main_kw, syns in SYNONYMS.items():
# rule = CATEGORY_RULES.get(main_kw, {"type": "physical", "threshold": None})  # 默认归“物”
# for syn in syns:
# FINAL_KEYWORD_MAP[syn] = rule
 
# ================== 核心函数 ==================
# ￼
# def determine_target_year_and_type(file_path):
# """从文件路径解析：城市、目标年份、文件类型"""
# try:
# rel_path = os.path.relpath(file_path, BASE_DIR)
# parts = rel_path.split(os.sep)
# if len(parts) < 3:
# return None, None, None
# city, folder_name, filename = parts[0], parts[1], parts[2]     year_match = re.search(r'(\d{4})', filename)
#     if not year_match:
#         return None, None, None
#     year = int(year_match.group(1))
    
#     if "决算" in folder_name:
#         return city, year, "决算"
#     elif "预算" in folder_name:
#         return city, year, "预算"
#     else:
#         return city, None, "报告"
# except:
#     return None, None, None
# ￼
# def extract_expenditure_amount(line):
# """
# 高精度提取支出金额（单位：亿元）
# 返回 float，无有效金额返回 0.0
# """
# line = line.strip()
# if not line or len(line) < 8:
# return 0.0

#     # 排除明显非支出金额行
# if re.search(r’(同比|增长|下降|完成率|占比|总计|合计|总支出|余额|结余|\d+%)’, line):
# return 0.0

#     # 1. 优先匹配“XX亿元”或“XX亿”
# match = re.search(r’([\d,]+.?\d*)\s亿(?:元)?’, line)
# if match:
# try:
# num_str = match.group(1).replace(’,’, ‘’)
# num = float(num_str)
# if 0.1 <= num <= 2000:  # 合理财政支出范围
# return num
# except (ValueError, TypeError):
# pass

#     # 2. 匹配“XX万元”且 ≥1亿（即 ≥10000万元）
# match = re.search(r’(\d{5,})\s万元’, line)  # 至少5位数字
# if match:
# try:
# num_wan = int(match.group(1))
# num_yi = num_wan / 10000.0
# if 1.0 <= num_yi <= 2000:
# return num_yi
# except (ValueError, TypeError):
# pass

#     # 3. 关键词 + 行尾数字（保守策略）
# if re.search(r’(?:教育|科技|科学|社保|卫生|医疗|交通|运输|城乡|社区|市政|农业|林业|水利|农林|工业|信息|住房|棚改|保障房)’, line):
# match = re.search(r’(\d+.?\d*)\s* $ ‘, line)
# if match:
# try:
# num = float(match.group(1))
# if 1.0 <= num <= 1000:  # 假设单位为亿元
# return num
# except (ValueError, TypeError):
# pass

#     return 0.0

# def classify_expenditure(text):
# """从文本中分类汇总支出"""
# human_total = 0.0
# physical_total = 0.0
# lines = text.split(’\n’)

#     for line in lines:
# amount = extract_expenditure_amount(line)
# if amount == 0.0:
# continue

#         # 匹配支出科目
# matched = False
# for keyword, rule in FINAL_KEYWORD_MAP.items():
# if keyword in line:
# # 应用阈值规则
# threshold = rule["threshold"]
# if threshold is not None:
# if (keyword in ["农业", "林业", "水利", "农林"] and amount > threshold) or 
# (keyword in ["科技", "科学技术", "科研"] and amount <= threshold):
# pass  # 符合条件
# else:
# continue  # 不符合条件，跳过             # 累加
#             if rule["type"] == "human":
#                 human_total += amount
#             else:
#                 physical_total += amount
#             matched = True
#             break  # 一行只计一次
# ￼
#     return round(human_total, 2), round(physical_total, 2)
 
# ================== 主流程 ==================
# results = []
# txt_files = []
 
# 收集所有 .txt 文件
# for root, _, files in os.walk(BASE_DIR):
# for f in files:
# if f.endswith(".txt"):
# txt_files.append(os.path.join(root, f))

# print(f"🔍 共发现 {len(txt_files)} 个 TXT 文件，开始处理…")

# for file_path in tqdm(txt_files, desc="处理文件"):
# try:
# city, year, file_type = determine_target_year_and_type(file_path)
# if year is None or file_type == "报告":
# continue  # 跳过政府工作报告

#         with open(file_path, "r", encoding="utf-8") as f:
# content = f.read()

#         human, physical = classify_expenditure(content)
# if human > 0 or physical > 0:
# results.append({
# "城市": city,
# "年份": year,
# "数据来源": file_type,
# "投资于人_亿元": human,
# "投资于物_亿元": physical
# })
# except Exception as e:
# print(f"\n❌ 处理失败: {file_path} | 错误: {str(e)[:120]}")
 
# ================== 后处理：去重 + 排序（兼容旧版 pandas） ==================
# if not results:
# print("⚠️ 未提取到任何有效数据，请检查 TXT 文件内容。")
# else:
# df = pd.DataFrame(results) # 添加临时排序列：决算=0，预算=1
# df["排序优先级"] = df["数据来源"].map({"决算": 0, "预算": 1})
# df = df.sort_values(["城市", "年份", "排序优先级"])
# df = df.drop_duplicates(subset=["城市", "年份"], keep="first")
# df = df.drop(columns=["排序优先级"])  # 删除临时列

# df = df.sort_values(["城市", "年份"]).reset_index(drop=True)
# ￼
#     # 保存结果
# output_path = os.path.join(BASE_DIR, "..", "investment_analysis.xlsx")
# df.to_excel(output_path, index=False, engine="openpyxl")

#     print(f"\n✅ 处理完成！共提取 {len(df)} 条有效记录")
# print(f"📊 结果已保存至: {output_path}")
# print("\n前5行预览:")
# print(df.head().to_string(index=False)) 