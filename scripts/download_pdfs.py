#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下載交通部公路局「檢考驗員試題」近6年(109~115年)歷屆筆試試題PDF
資料來源: https://www.thb.gov.tw/News_Download.aspx?n=223&sms=12823
"""
import os
import time
import requests

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw_pdfs")
os.makedirs(OUT_DIR, exist_ok=True)

# 每筆: (檔案編號, 年度梯次標籤, 下載連結)
EXAM_FILES = [
    ("C-00067", "115-2", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMzAyMTM5L2RlOGU5MTRhLTUxY2YtNDg5Ny04MGRmLTM3OWJkNjQwYjA1ZS5wZGY%3d&n=MTE1LTLlhajnp5HoqabpoYzlj4rnrZTmoYgtMTE1MDczMOS%2fruatoy5wZGY%3d&icon=..pdf"),
    ("C-00066", "115-年度", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjk2ODg0L2MyOTdjNzliLTRhNjEtNGU0NC1iYWJiLTdmNWU2MGEzMWU0My5wZGY%3d&n=MTE15bm05bqm5YWo56eR6Kmm6aGM5Y%2bK562U5qGILnBkZg%3d%3d&icon=..pdf"),
    ("C-00065", "115-1", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjk1MjY4LzZkOGY2ODc2LTc3Y2ItNDRmNi1iZTYyLTMyZjljY2MwZjExMi5wZGY%3d&n=MTE1LTHlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00064", "114-3", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjgzNjA5LzY4ZGQ2Y2NkLWUyYmYtNDUwZi05NzZjLWM3NDkxMzljYjc5Mi5wZGY%3d&n=MTE0LTPlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00063", "114-2", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjc2MDkyLzQ4ODlhYTEwLThhNzctNDEyMy1iOTIyLWE4YjA2OGFiYmI3MC5wZGY%3d&n=MTE0LTLlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00062", "114-年度", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjcxMzIwLzlhYTg5OGEyLWM5NmUtNDczZS1iYjVjLTgxNGRmOGJmZWZkNS5wZGY%3d&n=MTE05YWo56eR6Kmm6aGM5Y%2bK562U5qGILnBkZg%3d%3d&icon=..pdf"),
    ("C-00061", "114-1", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjcwMDIwL2JlMDk5NDk0LTUwYzEtNGQ2NC1hNDI5LWI2MDQ5NDU0ZWIxOC5wZGY%3d&n=MTE0LTHlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00060", "113-4", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjYyOTUyL2ExYjQ0MDJjLWZjN2UtNDA4Ni05NzQzLWYxMzJlNDg0NjZmNC5wZGY%3d&n=MTEzLTTlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00059", "113-3", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjU4MTIzL2ZhMTRjZjNhLTQ4M2QtNGVkNi1hOTUyLTM4M2I0MDJmZjMxOC5wZGY%3d&n=MTEzLTPlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00058", "113-2", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjUxMjk5LzQ5ZjQ3ZDhkLTA4OGItNGExYS04ZTczLTZkMDM0NjlmYzhhYy5wZGY%3d&n=MTEzLTLlhajnp5HoqabpoYzlj4rnrZTmoYgtMTEzMDgwNeS%2fruatoy5wZGY%3d&icon=..pdf"),
    ("C-00057", "113-1", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjQ2MTk5LzQ0MjUwOWFlLWUwNzEtNDc5YS05NDkzLTlhZDUxYjQxNzNmNi5wZGY%3d&n=MTEzLTHlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00056", "113-年度", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjQ1ODAwLzc4ZWMwZGEwLTdkYjUtNDNlMC05YjBjLTAyYmZkOWY2NDgyYy5wZGY%3d&n=MTEz5bm05bqm5qqi5a6a5a2456eR6Kmm6aGM5Y%2bK562U5qGILnBkZg%3d%3d&icon=..pdf"),
    ("C-00054", "112-3", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjMxNDg3LzY1MzUwODE3LTNhNTUtNDNjZi1hYjRjLTAzOWM1NTZlMTU2NS5wZGY%3d&n=MTEyLTPlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00053", "112-2", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjI1MTUwLzQ4MDEyODE5LTcyOTctNGM3YS05M2U0LWY0MDI0ZjYxMmUzYi5wZGY%3d&n=MTEyLTLlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00052", "112-年度", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjE3MTM0Lzg4M2UzNmY1LTY4ZDctNGU0NC1iYjg1LTJmMzQzZTEyYTQ0Yy5wZGY%3d&n=MTEy5bm05bqm5qqi5a6a5a2456eR6Kmm6aGM5ZCr562U5qGILnBkZg%3d%3d&icon=..pdf"),
    ("C-00051", "112-1", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS9VcGxvYWQvNDM2L3JlbGZpbGUvMTI4MjMvMjE1MTEwL2MyZmNiYThhLWE5OTAtNDVkNS1iNWJhLTU1NzA1YWZjNTU5OS5wZGY%3d&n=MTEyLTHlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00050", "111-3", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvMjdDNUQ4MUMtQzAyMi00RDI5LTg4NzAtNjI3NjNFRjU1QThCLnBkZg%3d%3d&n=MTExLTPlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00049", "111-2", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvMjAyNjcxMTgtOTk5Mi00NDAxLUExRDQtMTJEM0VEMTBBMTgxLnBkZg%3d%3d&n=MTExLTLlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00048", "111-年度", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvNDc0NEZFOTctNDJFMC00NkIyLTlGMzktQUUwOUVBNjM1NkNELnBkZg%3d%3d&n=MTEx5bm05rG96LuK5qqi44CB6ICD6amX5ZOh5qqi5a6a5ZCE5a2456eR562G6Kmm6Kmm6aGM5Y%2bK562U5qGILTA1MDLkv67mraMucGRm&icon=..pdf"),
    ("C-00046", "111-1", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvREY4NEI1NUUtMkREMC00NzM3LUFDNkQtNEIxODcxRTM1QUI5LnBkZg%3d%3d&n=MTExLTHlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00045", "110-3", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvNDY4QzhEOTctREVFRC00QTdGLThDMDMtQTU3QUY2RDlBOEJDLnBkZg%3d%3d&n=MTEwLTPlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00044", "110-2", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvOThCNjMyNzAtMUIzMi00OEM1LUE2MDctQzk4OUQwODg0Q0EyLnBkZg%3d%3d&n=MTEwLTLlhajnp5HoqabpoYzlj4rnrZTmoYgucGRmIC5wZGY%3d&icon=..pdf"),
    ("C-00043", "110-年度", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvRTFEQzdGQUMtNTJCRS00NUIyLTk3QTktN0Y0OEZGMEI4QzJDLnBkZg%3d%3d&n=MTEw5bm05rG96LuK5qqi44CB6ICD6amX5ZOh5qqi5a6a5ZCE5a2456eR562G6Kmm6Kmm6aGM5Y%2bK562U5qGIIC5wZGY%3d&icon=..pdf"),
    ("C-00042", "110-1", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvOTg0QkQwNTgtM0YxMy00QTRBLUFDN0MtQjM4QjNEMDFBODMxLnBkZg%3d%3d&n=MTEwLTHlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00041", "109-3", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvRjFDNTdBN0YtOEU3QS00N0ZBLUJFOTktQzlENTdBNzRFNTU5LnBkZg%3d%3d&n=MTA5LTPlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00040", "109-2", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvMThFMkI1ODAtOENDQi00QkMzLUJFMTItNjQyQUEzMDdEOTU5LnBkZg%3d%3d&n=MTA5LTLlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
    ("C-00039", "109-年度", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvNUIyQzRCRjItRDA3Qi00RDE1LTg1OTMtQTNDMDk1NEY2QUM1LnBkZg%3d%3d&n=MTA55bm05rG96LuK5qqi44CB6ICD6amX5ZOh5qqi5a6a5ZCE5a2456eR562G6Kmm6Kmm6aGM5Y%2bK562U5qGIIC5wZGY%3d&icon=..pdf"),
    ("C-00038", "109-1", "https://ws.thb.gov.tw/Download.ashx?u=LzAwMS91cGxvYWQvT2xkRmlsZS9yZXNvdXJjZS91cGxvYWQvRG93bmxvYWQvMkQwRDZBRjQtMTA5Ni00RDY4LThDOUItREI3REI2RUREQTMwLnBkZg%3d%3d&n=MTA5LTHlhajnp5HoqabpoYzlj4rnrZTmoYgucGRm&icon=..pdf"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer": "https://www.thb.gov.tw/News_Download.aspx?n=223&sms=12823",
}


def download_all():
    ok, fail = 0, 0
    for file_no, tag, url in EXAM_FILES:
        fname = f"{tag}_{file_no}.pdf"
        fpath = os.path.join(OUT_DIR, fname)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 1000:
            print(f"[skip] {fname} 已存在")
            ok += 1
            continue
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            if resp.headers.get("Content-Type", "").lower().startswith("application/pdf") or resp.content[:4] == b"%PDF":
                with open(fpath, "wb") as f:
                    f.write(resp.content)
                print(f"[ok]   {fname}  ({len(resp.content)} bytes)")
                ok += 1
            else:
                print(f"[warn] {fname} 回傳內容不是PDF，略過（可能連結已失效，請手動確認）")
                fail += 1
        except Exception as e:
            print(f"[fail] {fname}: {e}")
            fail += 1
        time.sleep(1.5)  # 對政府網站放慢速度，避免被擋
    print(f"\n完成：成功 {ok} 筆，失敗 {fail} 筆，共 {len(EXAM_FILES)} 筆")


if __name__ == "__main__":
    download_all()
