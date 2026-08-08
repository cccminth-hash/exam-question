#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將 data/raw_pdfs/ 內的歷屆試題PDF解析成結構化題庫 JSON。

輸出: data/question_bank.json
格式:
[
  {
    "id": "115-1-003",
    "source": "115-1",
    "question": "題目文字...",
    "options": {"A": "選項一", "B": "選項二", "C": "選項三", "D": "選項四"},
    "answer": "B",
    "subject": "汽車檢驗員",       # 由檔名/內容關鍵字粗略分類，可手動修正
    "needs_review": false
  },
  ...
]

注意：政府PDF排版每年可能略有不同，本腳本使用多組正則規則盡量涵蓋常見格式，
解析失敗或信心不足的題目會被標記 needs_review=true，並額外輸出到
data/needs_review.json，方便人工校對後再併回主題庫。
"""
import os
import re
import json
import glob

try:
    import pdfplumber
except ImportError:
    raise SystemExit("請先安裝 pdfplumber： pip install pdfplumber --break-system-packages")

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw_pdfs")
OUT_BANK = os.path.join(os.path.dirname(__file__), "..", "data", "question_bank.json")
OUT_REVIEW = os.path.join(os.path.dirname(__file__), "..", "data", "needs_review.json")

FULLWIDTH_LETTERS = {"Ａ": "A", "Ｂ": "B", "Ｃ": "C", "Ｄ": "D"}

# 題目起始樣式，例如: "1.(2)題目..." 或 "1.（2）題目..." 或 "1、(2)題目..."
Q_START = re.compile(
    r"(?P<num>\d{1,3})[.、]\s*[\(（]\s*(?P<answer>[1-4ＡＢＣＤABCD])\s*[\)）]\s*(?P<rest>.+)"
)
# 選項樣式: (A)xxx (B)xxx (C)xxx (D)xxx 可能同行或分行
OPT_INLINE = re.compile(
    r"[\(（]?[AＡ][\)）.．、]\s*(?P<a>.*?)\s*[\(（][BＢ][\)）.．、]\s*(?P<b>.*?)\s*"
    r"[\(（][CＣ][\)）.．、]\s*(?P<c>.*?)\s*[\(（][DＤ][\)）.．、]\s*(?P<d>.*)"
)
ANS_NUM_MAP = {"1": "A", "2": "B", "3": "C", "4": "D"}


def normalize_answer(a):
    a = a.strip()
    if a in ANS_NUM_MAP:
        return ANS_NUM_MAP[a]
    if a in FULLWIDTH_LETTERS:
        return FULLWIDTH_LETTERS[a]
    if a.upper() in "ABCD":
        return a.upper()
    return a


def guess_subject(text):
    if "檢驗" in text:
        return "汽車檢驗相關法規/實務"
    if "考驗" in text or "駕駛" in text:
        return "駕駛考驗相關法規/實務"
    return "未分類"


def extract_text(pdf_path):
    lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            lines.extend(t.split("\n"))
    return lines


def parse_lines(lines, source_tag):
    """逐行掃描，遇到新題號就切一題；同一題的後續行併入直到下一題號出現。"""
    questions = []
    review = []
    buf = []

    def flush(buf_lines, idx):
        if not buf_lines:
            return
        joined = " ".join(buf_lines)
        m = Q_START.match(buf_lines[0])
        if not m:
            return
        answer = normalize_answer(m.group("answer"))
        rest = joined[joined.index(m.group("rest")):] if m.group("rest") in joined else joined

        opt_match = OPT_INLINE.search(rest)
        if opt_match:
            question_text = rest[: opt_match.start()].strip(" .。:：")
            options = {
                "A": opt_match.group("a").strip(),
                "B": opt_match.group("b").strip(),
                "C": opt_match.group("c").strip(),
                "D": opt_match.group("d").strip(),
            }
            needs_review = not (question_text and all(options.values()))
        else:
            question_text = rest.strip()
            options = {"A": "", "B": "", "C": "", "D": ""}
            needs_review = True

        item = {
            "id": f"{source_tag}-{idx:03d}",
            "source": source_tag,
            "question": question_text,
            "options": options,
            "answer": answer if answer in "ABCD" else "",
            "subject": guess_subject(question_text),
            "needs_review": needs_review or answer not in "ABCD",
        }
        (review if item["needs_review"] else questions).append(item)

    idx = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if Q_START.match(line):
            if buf:
                idx += 1
                flush(buf, idx)
            buf = [line]
        else:
            if buf:
                buf.append(line)
    if buf:
        idx += 1
        flush(buf, idx)

    return questions, review


def main():
    os.makedirs(os.path.dirname(OUT_BANK), exist_ok=True)
    all_q, all_review = [], []

    pdf_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.pdf")))
    if not pdf_files:
        print("找不到PDF，請先執行 download_pdfs.py")
        return

    for pdf_path in pdf_files:
        fname = os.path.basename(pdf_path)
        source_tag = fname.split("_")[0]  # 例如 115-1
        print(f"解析中: {fname}")
        try:
            lines = extract_text(pdf_path)
        except Exception as e:
            print(f"  [跳過] 無法讀取: {e}")
            continue
        qs, rv = parse_lines(lines, source_tag)
        print(f"  -> 成功 {len(qs)} 題，需人工確認 {len(rv)} 題")
        all_q.extend(qs)
        all_review.extend(rv)

    with open(OUT_BANK, "w", encoding="utf-8") as f:
        json.dump(all_q, f, ensure_ascii=False, indent=2)
    with open(OUT_REVIEW, "w", encoding="utf-8") as f:
        json.dump(all_review, f, ensure_ascii=False, indent=2)

    print(f"\n共輸出 {len(all_q)} 題到 question_bank.json")
    print(f"另有 {len(all_review)} 題需人工確認，見 needs_review.json")
    print("提醒：政府PDF每年排版可能略有出入，第一次執行後請務必抽查")
    print("question_bank.json 內容是否正確，尤其是選項與答案是否對應。")


if __name__ == "__main__":
    main()
