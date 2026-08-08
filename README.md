# 汽車檢驗員 考照題庫系統

自動蒐集交通部公路局近6年（109~115年）「檢考驗員試題」歷屆筆試考題，
建立結構化題庫，並提供：
1. 自動出題（隨機產生PDF考卷 + 教師解答版）
2. 線上刷題網站（GitHub Pages，手機/電腦皆可用）

## 檔案結構

```
exam-bank/
├── scripts/
│   ├── download_pdfs.py      下載28份官方歷屆考題PDF
│   ├── extract_questions.py  解析PDF → 結構化題庫 question_bank.json
│   └── generate_exam.py      隨機抽題 → 產生PDF考卷+解答
├── data/
│   ├── raw_pdfs/              (自動產生) 下載的原始PDF
│   ├── question_bank.json     (自動產生) 結構化題庫
│   ├── needs_review.json      (自動產生) 解析信心不足、需人工確認的題目
│   └── exams/                 (自動產生) 產生的考卷PDF
├── web/
│   ├── index.html             學生刷題網頁（GitHub Pages會發布這個資料夾）
│   └── question_bank.json     (自動複製) 給網頁用的題庫
├── .github/workflows/
│   └── build_bank.yml         每週一自動：下載→解析→出題→更新網站
└── requirements.txt
```

## 建置步驟（手機Safari也可操作，比照之前monitor-agent的方式）

1. 到 github.com 建立一個新的 Public repository，命名例如 `exam-question-bank`。
2. 用網頁編輯器（Add file → Create new file）把上面每一個檔案，依照相同的
   資料夾路徑與檔名，逐一貼上內容建立（例如路徑輸入
   `scripts/download_pdfs.py`，貼上對應內容）。
3. 全部檔案建立完成後，到 repo 的 **Settings → Pages**：
   - Source 選擇 **GitHub Actions**（不要選 Deploy from a branch）。
4. 到 **Actions** 分頁：
   - 如果看到「set up a workflow yourself」的引導畫面，直接略過，
     因為 workflow 檔案已經在 `.github/workflows/build_bank.yml` 建立好了。
   - 找到「更新題庫並發布刷題網站」這個 workflow，點右側的
     **Run workflow** 按鈕手動執行一次（記得先在手機Safari開啟
     「桌面版網站」/Request Desktop Website，才看得到這個按鈕）。
5. 等待約2~5分鐘執行完成後：
   - `data/question_bank.json` 會自動更新並提交回 repo。
   - 網站會自動部署到 `https://<你的帳號>.github.io/exam-question-bank/`，
     這個網址就是給學生刷題用的連結。

之後每週一台灣時間08:00會自動重新檢查一次官方網站是否有新考題並更新，
不需要每次手動操作。

## 重要：第一次執行後請務必做的事

政府PDF每年排版可能有些微差異，`extract_questions.py` 的解析規則是用
常見格式寫的，**不保證100%正確**。第一次執行完，請：

1. 打開 `data/question_bank.json`，抽查幾題確認「題目/選項/答案」對應正確。
2. 打開 `data/needs_review.json`，這裡是程式判斷「不確定」的題目，
   可以手動修正後複製回 `question_bank.json`，或直接刪除不用。
3. 若發現某一年度PDF完全解析失敗（例如掃描檔沒有文字層），
   需要另外用OCR處理，可以再回來請我幫忙加強。

## 本機（Windows）也可以直接跑

```bash
pip install -r requirements.txt
python scripts/download_pdfs.py
python scripts/extract_questions.py
python scripts/generate_exam.py --num 50 --title "汽車檢驗員模擬考 第1回"
```

考卷會產生在 `data/exams/`，一份給學生（只有題目），一份標示`_answer`
給老師（含正確答案與出處年度）。

## 給學生的使用方式

把 GitHub Pages 網址（例如
`https://cccminth-hash.github.io/exam-question-bank/`）分享給學生，
手機直接開網頁即可刷題，可選10/20/50題或全部題庫，支援「即時看答案」
或「模擬考模式（考完才看結果）」，答對率、練習紀錄會存在學生自己手機的
瀏覽器裡，不會上傳到伺服器。
