import os
import re
import textract
import fitz  # PyMuPDF
from docx import Document

# ================== 配置 ==================
BASE_DIR = "d:\\999-桌面\\homework\\homework\\reports"

# ===== 清洗函数（修复空格）=====
def clean_pdf_text(text):
    text = re.sub(r'(\d)\s+(?=\d)', r'\1', text)
    text = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', text)
    text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', text)
    text = re.sub(r'(\d)\s*亿\s*元', r'\1亿元', text)
    text = re.sub(r'(\d)\s*万\s*元', r'\1万元', text)
    text = re.sub(r'(\d)\s*元', r'\1元', text)
    text = re.sub(r'交\s*通\s*运\s*输', '交通运输', text)
    text = re.sub(r'社\s*会\s*保\s*障', '社会保障', text)
    return text

import os
import sys

def extract_doc_like_file(filepath):
    """
    智能提取 .doc / .docx 文件，自动处理“假 .docx”问题
    """
    # 读取文件头判断真实类型
    with open(filepath, 'rb') as f:
        header = f.read(8)

    # DOC 文件头: D0 CF 11 E0 A1 B1 1A E1
    # DOCX 是 ZIP，开头是 PK\x03\x04...
    if header.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
        # 真实是 .doc，即使扩展名是 .docx
        try:
            raw = textract.process(filepath, method='antiword', encoding='utf-8')
            return raw.decode('utf-8', errors='ignore')
        except Exception as e:
            # fallback to default
            raw = textract.process(filepath, encoding='utf-8')
            return raw.decode('utf-8', errors='ignore')
    else:
        # 可能是真正的 .docx 或其他
        raw = textract.process(filepath, encoding='utf-8')
        return raw.decode('utf-8', errors='ignore')

# ===== 提取文本主函数 =====
def extract_text(filepath):
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    text = ""

    try:
        if ext == '.pdf':
            doc = fitz.open(filepath)
            for page in doc:
                txt = page.get_text("text")
                text += txt + "\n"
            doc.close()
            text = clean_pdf_text(text)

        elif ext in ['.doc', '.docx']:
            # 使用智能提取
            text = extract_doc_like_file(filepath)

        else:
            return None

    except Exception as e:
        print(f"⚠️ 提取失败: {filepath} | {e}")
        return None

    return text

# ===== 主转换逻辑 =====
def main():
    total = 0
    skipped = 0
    converted = 0

    for root, dirs, files in os.walk(BASE_DIR):
        for filename in files:
            if filename.startswith('.'):
                continue
            if not filename.lower().endswith(('.doc', '.docx', '.pdf')):
                continue
            if '工作报告' in filename:
                continue

            src_path = os.path.join(root, filename)
            txt_path = os.path.splitext(src_path)[0] + '.txt'

            total += 1

            if os.path.exists(txt_path):
                skipped += 1
                continue

            print(f"📄 正在转换: {src_path},并去除所有空格")
            text = extract_text(src_path)

            if text is not None:
                text = text.replace(' ','')
                with open(txt_path, 'w', encoding='utf-8-sig') as f:
                    f.write(text)
                converted += 1
            else:
                print(f"❌ 转换失败: {src_path}")

    print("\n✅ 转换完成!")
    print(f"  总文件数: {total}")
    print(f"  已跳过（已存在）: {skipped}")
    print(f"  新转换: {converted}")

if __name__ == "__main__":
    main()