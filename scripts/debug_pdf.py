#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
除錯用（第二版）：掃描第一份PDF的「全部頁面」，
找出哪些頁面看起來像選擇題（含A.B.C.D或(A)(B)(C)(D)等關鍵字），
並印出那幾頁的原始文字，方便確認實際考科結構與選擇題排版。
"""
import os
import re
import glob

try:
    import pdfplumber
except ImportError:
    raise SystemExit("請先安裝 pdfplumber： pip install pdfplumber --break-system-packages")

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw_pdfs")

MC_HINT = re.compile(r"[（(]\s*[AＡ]\s*[）)]|[AＡ][.、．]")


def main():
    pdf_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.pdf")))
    if not pdf_files:
        print("找不到PDF檔案")
        return

    target = pdf_files[0]
    print(f"===== 除錯目標檔案: {os.path.basename(target)} =====\n")

    with pdfplumber.open(target) as pdf:
        total = len(pdf.pages)
        print(f"總頁數: {total}\n")

        print("----- 各頁面「科目標題」與是否疑似選擇題 掃描結果 -----")
        mc_pages = []
        for idx, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            first_lines = " / ".join(text.split("\n")[:3])
            is_mc = bool(MC_HINT.search(text))
            if is_mc:
                mc_pages.append(idx)
            print(f"第{idx:2d}頁 {'★選擇題' if is_mc else '　　　　'} | 開頭: {first_lines[:60]}")

        print(f"\n疑似選擇題的頁碼: {mc_pages}\n")

        # 印出第一個疑似選擇題頁面的完整原始文字，供比對排版
        if mc_pages:
            p = pdf.pages[mc_pages[0] - 1]
            text = p.extract_text() or ""
            print(f"----- 第 {mc_pages[0]} 頁 完整原始文字（選擇題範例） -----")
            for i, line in enumerate(text.split("\n"), 1):
                print(f"{i:3d}| {line}")
        else:
            print("這份PDF裡完全沒有偵測到選擇題格式的頁面！")


if __name__ == "__main__":
    main()
