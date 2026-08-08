#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將 data/raw_pdfs/ 內的歷屆試題PDF解析成結構化題庫 JSON。

實際格式（依 debug_pdf.py 掃描結果確認）：
- 是非題： （Ｏ）1. 敘述文字...   → O=對, X=錯
- 選擇題： （4）11. 題目文字 (1)選項一(2)選項二(3)選項三(4)選項四
  括號內的數字/字母就是正確答案的選項編號

國文作文、公文寫作、英文術語對照等非選擇題內容，
無法轉換成考卷格式，程式會自動略過。

輸出: data/question_bank.json （統一轉成 A/B/C/D 四個選項的格式，
      是非題會轉成 A=正確（是） / B=錯誤（否） 兩個選項）
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

FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")
FULLWIDTH_LETTERS = str.maketrans("ＯｏＸｘ", "OoXx")
TRUE_CHARS = {"O", "o", "○", "Ο", "0"}
FALSE_CHARS = {"X", "x", "×"}

# 題目起始樣式："（4）11. 題目..." 或 "(O)1.題目..." 全形/半形括號都接受
Q_START = re.compile(
    r"^[\(（]\s*(?P<ans>[1-4OoXx×○])\s*[\)）]\s*(?P<num>\d{1,3})[.、]\s*(?P<rest>.+)$"
)

# 選擇題選項樣式：(1)xxx(2)xxx(3)xxx(4)xxx
OPT_INLINE = re.compile(
    r"[\(（]\s*1\s*[\)）]\s*(?P<o1>.*?)\s*"
    r"[\(（]\s*2\s*[\)）]\s*(?P<o2>.*?)\s*"
    r"[\(（]\s*3\s*[\)）]\s*(?P<o3>.*?)\s*"
    r"[\(（]\s*4\s*[\)）]\s*(?P<o4>.*)$"
)

SUBJECT_LINE = re.compile(r"(?P<subj>[\u4e00-\u9fffA-Za-z]+?)筆試試題")


def normalize(line):
    return line.translate(FULLWIDTH_DIGITS).translate(FULLWIDTH_LETTERS)


def extract_subject(line, current):
    m = SUBJECT_LINE.search(line)
    if m:
        subj = m.group("subj")
        # 去掉開頭常見的機關名稱贅字
        subj = re.sub(r"^.*研習班", "", subj)
        subj = re.sub(r"^.*梯次", "", subj)
        return subj.strip() or current
    return current


def parse_pdf(pdf_path, source_tag):
    questions, review = [], []
    current_subject = "未分類"
    idx = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            raw_lines = [l.strip() for l in text.split("\n") if l.strip()]

            buf = []

            def flush(buf_lines):
                nonlocal idx
                if not buf_lines:
                    return
                line0 = normalize(buf_lines[0])
                m = Q_START.match(line0)
                if not m:
                    return
                idx += 1
                ans_raw = m.group("ans")
                joined = normalize(" ".join(buf_lines))
                rest = joined[joined.index(m.group("rest")):] if m.group("rest") in joined else joined

                item_id = f"{source_tag}-{idx:03d}"

                if ans_raw in TRUE_CHARS or ans_raw in FALSE_CHARS:
                    # 是非題 -> 轉成 A/B 兩選項
                    question_text = rest.strip(" .。:：")
                    options = {"A": "正確（是）", "B": "錯誤（否）", "C": "", "D": ""}
                    answer = "A" if ans_raw in TRUE_CHARS else "B"
                    needs_review = not question_text
                    q_type = "true_false"
                else:
                    opt_m = OPT_INLINE.search(rest)
                    if opt_m:
                        question_text = rest[: opt_m.start()].strip(" .。:：")
                        options = {
                            "A": opt_m.group("o1").strip(),
                            "B": opt_m.group("o2").strip(),
                            "C": opt_m.group("o3").strip(),
                            "D": opt_m.group("o4").strip(),
                        }
                        ans_num = ans_raw
                        answer = {"1": "A", "2": "B", "3": "C", "4": "D"}.get(ans_num, "")
                        needs_review = not (question_text and all(options.values()) and answer)
                    else:
                        question_text = rest.strip()
                        options = {"A": "", "B": "", "C": "", "D": ""}
                        answer = ""
                        needs_review = True
                    q_type = "multiple_choice"

                item = {
                    "id": item_id,
                    "source": source_tag,
                    "type": q_type,
                    "question": question_text,
                    "options": options,
                    "answer": answer,
                    "subject": current_subject,
                    "needs_review": needs_review,
                }
                (review if needs_review else questions).append(item)

            for line in raw_lines:
                current_subject = extract_subject(line, current_subject)
                norm = normalize(line)
                if Q_START.match(norm):
                    if buf:
                        flush(buf)
                    buf = [line]
                else:
                    if buf:
                        buf.append(line)
            if buf:
                flush(buf)

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
        source_tag = fname.split("_")[0]
        print(f"解析中: {fname}")
        try:
            qs, rv = parse_pdf(pdf_path, source_tag)
        except Exception as e:
            print(f"  [跳過] 無法解析: {e}")
            continue
        print(f"  -> 成功 {len(qs)} 題，需人工確認 {len(rv)} 題")
        all_q.extend(qs)
        all_review.extend(rv)

    with open(OUT_BANK, "w", encoding="utf-8") as f:
        json.dump(all_q, f, ensure_ascii=False, indent=2)
    with open(OUT_REVIEW, "w", encoding="utf-8") as f:
        json.dump(all_review, f, ensure_ascii=False, indent=2)

    print(f"\n共輸出 {len(all_q)} 題到 question_bank.json")
    print(f"另有 {len(all_review)} 題需人工確認，見 needs_review.json")
    print("提醒：國文作文/公文寫作/英文術語對照等非選擇題內容已自動略過。")
    print("是非題已自動轉換成 A=正確（是）/ B=錯誤（否）的兩選項格式。")


if __name__ == "__main__":
    main()
