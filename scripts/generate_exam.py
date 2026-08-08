name: build-exam-bank
on:
  workflow_dispatch:
    inputs:
      exam_count:
        description: "本次要出的考卷題數"
        required: false
        default: "50"
      exam_title:
        description: "考卷標題"
        required: false
        default: "汽車檢驗員資格檢定模擬考"
  schedule:
    - cron: "0 0 * * 1"
permissions:
  contents: write
  pages: write
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: sudo apt-get update && sudo apt-get install -y fonts-noto-cjk
      - run: pip install --upgrade pip
      - run: pip install requests pdfplumber weasyprint
      - run: python scripts/download_pdfs.py
      - run: python scripts/extract_questions.py
      - run: python scripts/generate_exam.py --num "${{ github.event.inputs.exam_count || '50' }}" --title "${{ github.event.inputs.exam_title || '汽車檢驗員資格檢定模擬考' }}" || echo "出題失敗，先跳過"
      - run: cp data/question_bank.json web/question_bank.json
      - run: git config user.name "exam-bank-bot"
      - run: git config user.email "actions@users.noreply.github.com"
      - run: git add data/question_bank.json data/needs_review.json web/question_bank.json data/exams
      - run: git commit -m "auto update" || echo "nothing to commit"
      - run: git push
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: web
      - uses: actions/deploy-pages@v4
