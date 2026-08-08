#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
除錯用：印出第一份PDF的原始文字內容（前80行），
幫助確認實際排版格式，以便修正 extract_questions.py 的解析規則。
"""
import os
import glob

try:
    import pdfplumber
except ImportError:
    raise SystemExit("請先安裝 pdfplumber： pip install pdfplumber --break-system-packages")

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw_pdfs")


def main():
    pdf_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.pdf")))
    if not pdf_files:
        print("找不到PDF檔案")
        return

    target = pdf_files[0]
    print(f"===== 除錯目標檔案: {os.path.basename(target)} =====\n")

    with pdfplumber.open(target) as pdf:
        print(f"總頁數: {len(pdf.pages)}\n")
        for page_num, page in enumerate(pdf.pages[:2], 1):  # 只看前2頁
            text = page.extract_text() or "(此頁擷取不到文字，可能是掃描檔或圖片型PDF)"
            print(f"----- 第 {page_num} 頁 原始文字 -----")
            lines = text.split("\n")
            for i, line in enumerate(lines[:60], 1):
                print(f"{i:3d}| {line}")
            print()


if __name__ == "__main__":
    main()
