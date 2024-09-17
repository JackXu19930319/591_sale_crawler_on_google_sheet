
# 如何取得 Google API 的 `credentials.json`

Google API 服務需要透過 OAuth 2.0 認證來授權應用程式使用 Google 的資源。以下是如何取得 `credentials.json` 檔案的步驟。

## 步驟 1：建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)，並使用 Google 帳戶登入。
2. 在頂部工具列中，點擊左上角的 **選擇專案**。
3. 點擊 **新建專案**，然後為你的專案命名，並選擇一個組織（如果有）。
4. 點擊 **建立** 完成專案的建立。

## 步驟 2：啟用 Google API

1. 在 Cloud Console 左側的選單中，點擊 **API 和服務** > **啟用 API 和服務**。
2. 搜尋並選擇你需要的 API，點擊 **啟用**。例如，如果你要使用 Google Drive API，搜尋 "Google Drive API" 並啟用它。

## 步驟 3：建立 OAuth 2.0 認證

1. 在左側選單中，點擊 **憑證**。
2. 點擊上方的 **建立憑證** > **OAuth 用戶端 ID**。
   - 如果你還未設定 OAuth 同意畫面，系統會提示你完成此步驟。點擊 **設定同意畫面** 並填寫必要的資訊。
3. 在 **應用類型** 中，選擇 **桌面應用程式** 或 **網頁應用程式**（視你的應用而定）。
4. 為此 OAuth 用戶端命名，然後點擊 **建立**。
5. 下載 `credentials.json` 檔案，並將其保存在你的專案根目錄。

## 步驟 4：使用 `credentials.json`

下載完成後，你應該將 `credentials.json` 檔案儲存在你的專案目錄中，並確保你程式碼能夠引用此檔案來執行 OAuth 認證。例如，對於 Python 程式碼，可以這樣使用：

```python
from google.oauth2 import service_account

# 使用 credentials.json 建立服務
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json'
)

# 授權並使用 Google API
```

---

# 如何取得 LINE Notify Token

LINE Notify 提供一種簡單的方式，讓開發者或應用程式能夠發送通知到 LINE 群組或個人。以下步驟將教你如何取得 LINE Notify Token。

## 步驟 1：登入 LINE Notify 平台

1. 前往 [LINE Notify 官方網站](https://notify-bot.line.me/)，並點擊右上角的 **登入** 按鈕。
2. 使用你的 LINE 帳戶進行登入，登入後你將被導向到 LINE Notify 的主頁。

## 步驟 2：生成個人存取權杖（Token）

1. 在首頁，點擊右上角的 **個人** 圖標，然後選擇 **我的頁面**。
2. 在 **我的頁面** 中，找到 **個人存取權杖** 區域，點擊 **生成存取權杖** 按鈕。
3. 為你的存取權杖命名，這個名稱可以是與你應用程式相關的名稱，便於識別。
4. 選擇通知的接收對象：
    - **1 對 1 聊天**：通知將發送給你個人帳戶。
    - **群組**：如果你希望將通知發送到某個 LINE 群組，點擊 **選擇群組** 並選擇你有權限管理的群組。
5. 點擊 **生成存取權杖** 按鈕。
6. 系統會生成一個存取權杖（Token），**請務必複製並儲存這個 Token**，因為此頁面只會顯示一次。

## 步驟 3：使用你的 LINE Notify Token

你可以使用剛生成的 Token 來發送通知至 LINE，例如透過簡單的 HTTP POST 請求來發送訊息：

### 範例：使用 cURL 發送通知

```bash
curl -X POST https://notify-api.line.me/api/notify \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-F "message=這是一個測試訊息"
```

### 範例：使用 Python 發送通知

```python
import requests

url = "https://notify-api.line.me/api/notify"
token = "YOUR_ACCESS_TOKEN"
headers = {
    "Authorization": f"Bearer {token}"
}

data = {
    "message": "這是一個測試訊息"
}

response = requests.post(url, headers=headers, data=data)
print(response.status_code)
```

---

# 如何取得 Google Sheet ID 並設置標題與分享權限

這篇教學將指導你如何取得 Google Sheet 的 ID，設置指定的表格標題，並將分享權限設定為 Google API 服務帳戶（例如 `credentials.json` 中的服務郵件帳號）。

## 步驟 1：建立 Google Sheet 並取得 Sheet ID

1. 前往 [Google Sheets](https://docs.google.com/spreadsheets/)。
2. 點擊左上角的 **空白**，建立一個新的 Google Sheet。
3. 在瀏覽器網址列中，URL 的格式類似於：

   ```
   https://docs.google.com/spreadsheets/d/`<SHEET_ID>`/edit#gid=0
   ```

4. 複製其中的 `SHEET_ID`，這是 Google Sheet 的唯一識別碼。

## 步驟 2：使用 Google Sheets API 設置表格標題

要設置 Google Sheet 的表格標題，你可以使用 Google Sheets API。以下是使用 Python 的範例，將欄位標題設置為：

```
house ID, LINK, 價錢, 坪數, 樓層, 區域, 房型, 單價, 社區名, 巷弄, 類型
```

### 使用 Python 設置 Google Sheet 標題

1. 安裝 Google API Python 客戶端：

   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. 建立 `credentials.json`，並將其放在你的專案目錄中。

3. 使用以下 Python 代碼來設置 Google Sheet 的標題：

   ```python
   from googleapiclient.discovery import build
   from google.oauth2.service_account import Credentials

   # 授權並初始化 Google Sheets API
   SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
   SERVICE_ACCOUNT_FILE = 'credentials.json'  # 替換為你的 credentials.json 文件路徑

   credentials = Credentials.from_service_account_file(
       SERVICE_ACCOUNT_FILE, scopes=SCOPES)
   service = build('sheets', 'v4', credentials=credentials)

   # 你的 Google Sheet ID
   SPREADSHEET_ID = 'YOUR_SHEET_ID'  # 替換為你取得的 Google Sheet ID

   # 設置欄位標題
   values = [
       ["house ID", "LINK", "價錢", "坪數", "樓層", "區域", "房型", "單價", "社區名", "巷弄", "類型"]
   ]
   body = {
       'values': values
   }

   # 更新 Google Sheet 標題
   result = service.spreadsheets().values().update(
       spreadsheetId=SPREADSHEET_ID,
       range='A1',  # 從 A1 欄位開始
       valueInputOption='RAW',
       body=body
   ).execute()

   print(f'{result.get("updatedCells")} cells updated.')
   ```

4. 將 `SPREADSHEET_ID` 替換為你的 Google Sheet ID，並確保 `credentials.json` 具有正確的路徑。

## 步驟 3：設置 Google Sheet 分享權限給 Google API 服務帳戶

1. 在 Google Sheet 中，點擊右上角的 **分享** 按鈕。
2. 在分享視窗中，將 **Google API 服務帳戶郵件**（這可以在 `credentials.json` 中找到，格式類似 `service-account-name@project-id.iam.gserviceaccount.com`）輸入進去。
3. 將權限設置為 **編輯者**，然後點擊 **發送**。

現在，Google API 服務帳戶將擁有該 Google Sheet 的編輯權限，你的應用程式即可讀取或修改該 Sheet。
