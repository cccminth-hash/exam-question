#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 data/question_bank.json 隨機抽題，產生正式格式的PDF考卷 + 答案卷。
使用方式:
    python generate_exam.py --num 50 --title "汽車檢驗員模擬考 第1回"
輸出:
    data/exams/exam_YYYYMMDD_HHMMSS.pdf        (只有題目，給學生用)
    data/exams/exam_YYYYMMDD_HHMMSS_answer.pdf (含答案，給老師用)
"""
import os
import json
import random
import argparse
import datetime

try:
    from weasyprint import HTML
except ImportError:
    raise SystemExit("請先安裝 weasyprint： pip install weasyprint --break-system-packages")

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
BANK_PATH = os.path.join(BASE_DIR, "data", "question_bank.json")
OUT_DIR = os.path.join(BASE_DIR, "data", "exams")

CSS = """
@font-face {
  font-family: 'NotoCJK';
  src: local('Noto Sans CJK TC');
}
body { font-family: 'NotoCJK', 'Noto Sans TC', sans-serif; font-size: 13pt; line-height: 1.6; }
h1 { font-size: 18pt; text-align: center; }
.meta { text-align: center; color: #555; margin-bottom: 20px; }
.q { margin-bottom: 14px; }
.q .num { font-weight: bold; }
.opts { margin-left: 1.5em; }
.opts span { display: inline-block; margin-right: 1.5em; }
.answer-key { column-count: 4; }
.footer { margin-top: 30px; font-size: 10pt; color: #888; text-align: center; }
"""


def load_bank():
    with open(BANK_PATH, encoding="utf-8") as f:
        data = json.load(f)
    # 過濾掉需要人工確認、選項或答案不完整的題目
    clean = [
        q for q in data
        if not q.get("needs_review")
        and q.get("answer") in ("A", "B", "C", "D")
        and all(q.get("options", {}).get(k) for k in "ABCD")
        and q.get("question")
    ]
    return clean


def build_html(title, questions, with_answer):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    body = [f"<h1>{title}</h1>", f"<div class='meta'>共 {len(questions)} 題 ｜ 產生時間 {now}</div>"]
    for i, q in enumerate(questions, 1):
        body.append("<div class='q'>")
        body.append(f"<span class='num'>{i}.</span> {q['question']}")
        body.append("<div class='opts'>")
        for k in "ABCD":
            body.append(f"<span>({k}) {q['options'][k]}</span>")
        body.append("</div>")
        if with_answer:
            body.append(f"<div style='color:#c00;'>正確答案：{q['answer']}　（原始出處：{q['source']}）</div>")
        body.append("</div>")
    body.append("<div class='footer'>本考卷由題庫系統隨機產生，題目來源為交通部公路局歷屆檢考驗員試題</div>")
    return f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(body)}</body></html>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--num", type=int, default=50, help="抽題數量")
    ap.add_argument("--title", type=str, default="汽車檢驗員資格檢定模擬考", help="考卷標題")
    ap.add_argument("--seed", type=int, default=None, help="亂數種子，固定後可重現同一份考卷")
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    bank = load_bank()
    if not bank:
        raise SystemExit("題庫是空的，請先執行 extract_questions.py 並確認 question_bank.json 有內容")

    if args.seed is not None:
        random.seed(args.seed)

    n = min(args.num, len(bank))
    picked = random.sample(bank, n)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    exam_path = os.path.join(OUT_DIR, f"exam_{ts}.pdf")
    answer_path = os.path.join(OUT_DIR, f"exam_{ts}_answer.pdf")

    HTML(string=build_html(args.title, picked, with_answer=False)).write_pdf(exam_path)
    HTML(string=build_html(args.title + "（教師解答版）", picked, with_answer=True)).write_pdf(answer_path)

    print(f"已產生考卷: {exam_path}")
    print(f"已產生解答: {answer_path}")
    print(f"共抽 {n} 題（題庫總量 {len(bank)} 題）")


if __name__ == "__main__":
    main()
