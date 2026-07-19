import asyncio
import os
import csv
import random
import smtplib
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from playwright.async_api import async_playwright

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTlV3fKG5HQjME5OYZ--vk7TMwaSkd_OZZMN4aMvEtLNx_wx7jCFhfu-L9eD74rXage674hucpO7dfR/pub?gid=0&single=true&output=csv"

LOGIN_URL     = "https://2pink.org/"
DASHBOARD_URL = "https://2pink.org/dashboard/live-traffic"

USERNAME  = os.environ["USERNAME_2PINK"]
PASSWORD  = os.environ["PASSWORD_2PINK"]
ACCOUNT   = os.environ.get("ACCOUNT", "?")

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "")

ACCOUNT_RANGES = {
    "1": (1, 5),
    "2": (6, 10),
}

MAX_RETRIES = 3
logs = []

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    logs.append(entry)

def fetch_keywords(stt_from, stt_to):
    with urllib.request.urlopen(SHEET_CSV_URL) as response:
        content = response.read().decode("utf-8")
    reader = csv.DictReader(content.splitlines())
    keywords = []
    for row in reader:
        try:
            stt = int(row["stt"])
            if stt_from <= stt <= stt_to:
                keywords.append({
                    "stt": stt,
                    "key": row["Key"].strip(),
                    "url": row["url"].strip()
                })
        except:
            continue
    keywords.sort(key=lambda x: x["stt"])
    return keywords

def send_email(success: bool, keywords: list):
    if not GMAIL_USER or not GMAIL_PASS:
        return

    status = "✅ Thành công" if success else "❌ Thất bại"
    subject = f"Account {ACCOUNT} Cập nhật Key - {status}"

    rows = ""
    for kw in keywords:
        rows += f"<tr><td>{kw['stt']}</td><td>{kw['key']}</td><td>{kw['url']}</td></tr>"

    body = f"""
<h2>Báo cáo cập nhật keyword</h2>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><td><b>Tài khoản</b></td><td>Account {ACCOUNT}</td></tr>
  <tr><td><b>Trạng thái</b></td><td>{status}</td></tr>
  <tr><td><b>Thời gian</b></td><td>{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</td></tr>
</table>
<h3>Danh sách keyword đã cập nhật:</h3>
<table border="1" cellpadding="6" cellspacing="0">
  <tr><th>STT</th><th>Key</th><th>URL</th></tr>
  {rows}
</table>
<h3>Chi tiết log:</h3>
<pre>{"<br>".join(logs)}</pre>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())
        print("📧 Đã gửi email báo cáo!")
    except Exception as e:
        print(f"⚠️ Lỗi gửi email: {e}")

async def update_one(page, row_index, kw):
    log(f"🔄 [{row_index+1}/5] Cập nhật STT {kw['stt']}: {kw['key']}")

    # Click vào LinkButton để mở form sửa
    link_id = f"#ctl00_ContentPlaceHolder1_ListView1_ctrl{row_index}_LinkButton1"
    log(f"🔍 Click: {link_id}")
    await page.click(link_id, timeout=60000)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)

    # Điền keyword
    kw_input = page.locator("#ctl00_ContentPlaceHolder1_txtKeyWord")
    await kw_input.triple_click()
    await kw_input.fill(kw["key"])
    await page.wait_for_timeout(500)

    # Điền URL
    url_input = page.locator("#ctl00_ContentPlaceHolder1_txtStep1")
    await url_input.triple_click()
    await url_input.fill(kw["url"])
    await page.wait_for_timeout(500)

    # Thời gian chờ random 25-115 giây
    wait_input = page.locator("#ctl00_ContentPlaceHolder1_txtWait1")
    rand_time = random.randint(25, 115)
    await wait_input.triple_click()
    await wait_input.fill(str(rand_time))
    await page.wait_for_timeout(500)

    # Bấm Cập nhật Url
    await page.click("#ctl00_ContentPlaceHolder1_btnUpdateUrl")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)

    log(f"✅ [{row_index+1}/5] Xong: {kw['key']} | {rand_time}s")

async def attempt(p, keywords):
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()

    try:
        await page.goto(LOGIN_URL)
        await page.wait_for_load_state("networkidle")
        await page.click("text=Đăng nhập", timeout=60000)
        await page.wait_for_timeout(2000)

        await page.fill("#ctl00_ContentPlaceHolder1_txtUserName", USERNAME)
        await page.fill("#ctl00_ContentPlaceHolder1_txtPass", PASSWORD)
        await page.click("#ctl00_ContentPlaceHolder1_btnDangNhap")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        log("✅ Đã đăng nhập!")

        await page.goto(DASHBOARD_URL)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        log("✅ Đã vào dashboard!")

        for i, kw in enumerate(keywords):
            await update_one(page, i, kw)

        return True

    except Exception as e:
        log(f"❌ Lỗi: {e}")
        return False
    finally:
        await browser.close()

async def run():
    if ACCOUNT not in ACCOUNT_RANGES:
        log(f"❌ Account {ACCOUNT} chưa được cấu hình!")
        return

    stt_from, stt_to = ACCOUNT_RANGES[ACCOUNT]
    log(f"📥 Đọc keywords STT {stt_from}-{stt_to} từ Google Sheet...")
    keywords = fetch_keywords(stt_from, stt_to)
    log(f"✅ Đọc được {len(keywords)} keywords")

    success = False
    async with async_playwright() as p:
        for i in range(1, MAX_RETRIES + 1):
            try:
                if i > 1:
                    log(f"🔄 Thử lại lần {i}/{MAX_RETRIES}...")
                    await asyncio.sleep(10)
                success = await attempt(p, keywords)
                if success:
                    break
            except Exception as e:
                log(f"⚠️ Lần {i} thất bại: {e}")
                if i == MAX_RETRIES:
                    log("❌ Đã thử 3 lần, không thành công!")

    send_email(success, keywords)

asyncio.run(run())
