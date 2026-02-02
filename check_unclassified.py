import pandas as pd

# 👇 修改为你的实际 CSV 路径
CSV_PATH = "d:\\999-桌面\\homework\\homework\\output\\investment_analysis.csv"

try:
    df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
except FileNotFoundError:
    print(f"❌ 文件未找到: {CSV_PATH}")
    exit(1)

# 筛选“未明确方向”的行
unclassified = df[df['匹配关键词'] == '未明确方向']

if unclassified.empty:
    print("✅ 没有发现'未明确方向'的记录！")
else:
    print(f"🔍 共找到 {len(unclassified)} 条'未明确方向'记录：\n")

    # 打印前 30 条（避免刷屏），显示关键字段
    for idx, row in unclassified.head(30).iterrows():
        print(f"[{row['区域']}] {row['城市']} | {row['年份']} | {row['文件类型']}")
        print(f"  💰 金额: {row['金额（万元）']:,.0f} 万元")
        print(f"  📄 原文: {row['原文片段']}")
        print("-" * 80)

    if len(unclassified) > 500:
        print(f"... 还有 {len(unclassified) - 30} 条未显示")