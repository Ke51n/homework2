import os
# 清理所有的txt文件，用于重新生成

BASE_DIR = "d:\\999-桌面\\homework\\homework\\reports"

def main():
    txt_files = []
    print(list(os.walk(BASE_DIR)))
    for root, dirs, files in os.walk(BASE_DIR):
        print(files)
        for file in files:
            if file.lower().endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    
    if not txt_files:
        print("✅ 没有找到任何 .txt 文件。")
        return

    print(f"🔍 发现 {len(txt_files)} 个 .txt 文件：\n")
    for f in sorted(txt_files):
        print(f"  - {f}")

    print("\n⚠️ 注意：以下操作将永久删除上述所有 .txt 文件！")
    input("按 Enter 键确认删除，或直接关闭窗口取消...")

    # 执行删除
    for f in txt_files:
        try:
            os.remove(f)
            print(f"🗑️ 已删除: {f}")
        except Exception as e:
            print(f"❌ 删除失败: {f} | {e}")

    print("\n✅ 清理完成！")

if __name__ == "__main__":
    main()