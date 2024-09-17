import os
import random
import sqlite3
import time

import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import urllib.parse


def init_db():
    # 初始化資料庫，創建表格
    conn = sqlite3.connect('house_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS houses (
            house_id TEXT PRIMARY KEY,
            link TEXT,
            price TEXT,
            area TEXT,
            floor TEXT,
            region TEXT,
            room TEXT,
            unit_price TEXT,
            community TEXT,
            address TEXT,
            kind TEXT
        )
    ''')
    conn.commit()
    return conn


def insert_house_to_db(conn, house_data):
    # 將新房屋數據插入資料庫
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO houses (house_id, link, price, area, floor, region, room, unit_price, community, address, kind)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        house_data["house ID"], house_data["LINK"], house_data["價錢"], house_data["坪數"],
        house_data["樓層"], house_data["區域"], house_data["房型"], house_data["單價"],
        house_data["社區名"], house_data["巷弄"], house_data["類型"]
    ))
    conn.commit()


def get_all_house_ids(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT house_id FROM houses")  # 從資料庫中選擇所有 house_id
    house_ids = cursor.fetchall()  # 取得所有結果
    return [house_id[0] for house_id in house_ids]  # 提取出所有 house_id


def line_notify(msg_str, token):
    try:
        # HTTP 標頭參數與資料
        headers = {"Authorization": "Bearer " + token}
        data = {
            'message': msg_str
        }
        # 以 requests 發送 POST 請求
        requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, data=data)
        print('傳送訊息： %s' % (msg_str))
        # print(mail.send_mail(msg_str))
    except Exception as e:
        print(str(e))
        pass
        # logger.error(logger.get_caller(__file__), line_notify.__name__, str(e))


def extract_house_data(json_data):
    house_data_list = [
        {
            "house ID": house["houseid"],
            "LINK": house.get("community_link", ""),
            "價錢": house["price"],
            "坪數": house["mainarea"],
            "樓層": house["floor"],
            "區域": house["region_name"],
            "房型": house["room"],
            "單價": house["unitprice"],
            "社區名": house["community_name"],
            "巷弄": house["address"],
            "類型": house["kind_name"]
        }
        for house in json_data["data"]["house_list"]
        if house.get("houseid")
    ]
    return house_data_list


# 建立連接到 Google Sheet 的函數
def connect_to_gsheet(sheet_name):
    # 定義範圍和憑證
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    # 授權並連接到 Google Sheets
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_name).sheet1  # 打開第一張表單
    return sheet


# 從 Google Sheets 中獲取現有的 house_id
def get_existing_house_ids(sheet):
    existing_data = sheet.get_all_records()  # 獲取所有資料
    existing_house_ids = [str(row["house ID"]) for row in existing_data if "house ID" in row]  # 提取所有 house_id
    return set(existing_house_ids)  # 使用 set 確保 house_id 唯一


# 將新資料匯入 Google Sheets 並跳過已存在的 house_id
def insert_data_if_not_exists(json_data):
    sheet = connect_to_gsheet(sheet_name)  # 連接到 Google Sheets
    print(f'connected to {sheet_name}')
    existing_house_ids = get_existing_house_ids(sheet)  # 獲取已存在的 house_id
    conn = init_db()  # 初始化 SQLite 資料庫
    existing_house_ids_sql = get_all_house_ids(conn)

    for house in json_data["data"]["house_list"]:
        if house.get("houseid") and str(house["houseid"]) not in existing_house_ids and house.get("houseid") not in existing_house_ids_sql:
            prod_url = f'https://sale.591.com.tw/home/house/detail/2/{str(house["houseid"])}.html'
            try:
                house_data = {
                    "house ID": str(house["houseid"]),
                    "LINK": prod_url,
                    "價錢": house["price"],
                    "坪數": house["area"],
                    "樓層": house["floor"],
                    "區域": house["region_name"],
                    "房型": house["room"],
                    "單價": house["unitprice"],
                    "社區名": house["community_name"],
                    "巷弄": house["address"],
                    "類型": house["kind_name"]
                }
                sheet.insert_row(list(house_data.values()), 2)
                insert_house_to_db(conn, house_data)
                if house.get('area', None) is not None:
                    build_purpose = house['area']
                else:
                    build_purpose = house.get('shape_name', '')
                msg = f"""
{house['title']}
連結：{prod_url}
${house['price']}
{house['mainarea']} 坪, {house['floor']}, {house['region_name']}
{house['address']}, {house['community_name']}
{house['kind_name']}, {build_purpose}
                """
                line_notify(msg, line_token)
            except Exception as e:
                print(f'url: {prod_url}, error: {e}')


def parse_url_to_json(url):
    # 解析 URL
    parsed_url = urllib.parse.urlparse(url)

    # 解析查詢參數
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # 遍歷參數並過濾出非空的 key-value
    parsed_dict = {
        key: value[0]
        for key, value in query_params.items()
        if value[0] != ""  # 只保留值非空的參數
    }

    # 新增 timestamp 參數
    parsed_dict["timestamp"] = int(time.time())  # 獲取當前 UNIX 時間戳
    parsed_dict['order'] = 'posttime_desc'
    # _v_=456c1961b8
    # parsed_dict['_v_'] = '456c1961b8'
    # recom_community=1
    # parsed_dict['recom_community'] = '1'
    # type=2
    parsed_dict['type'] = '2'

    # 將字典轉換為 JSON 格式
    # json_data = json.dumps(parsed_dict, ensure_ascii=False, indent=4)

    return parsed_dict


def get_591(data):
    # print(data)
    # 初始化 requests session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68', })
    res = session.get('https://sale.591.com.tw/')
    time.sleep(1)

    # 使用 BeautifulSoup 解析頁面並找到 csrf-token
    soup = BeautifulSoup(res.text, 'html.parser')
    XCSRFTOKEN = soup.find('meta', attrs={'name': 'csrf-token'})['content']
    session.headers.update({'X-CSRF-TOKEN': XCSRFTOKEN})

    # 設置 cookies 和搜尋參數
    session.cookies.set('urlJumpIp', '8', domain='.591.com.tw')
    # 爬取頁數設定，每頁 30 筆資料
    # total_page = 999
    firstRow = 0
    for page in range(1, max_pages + 1):
        data['firstRow'] = firstRow
        print(f'page: {page}')
        res = session.get('https://bff-house.591.com.tw/v1/sale/list', params=data)
        h_data = res.json()
        total = int(h_data['data']['total'])
        print(f'total: {total}')
        insert_data_if_not_exists(h_data)
        firstRow += 30
        if firstRow >= total:
            break
        print(f'休息{delay}秒')
        time.sleep(delay)


def countdown(minutes):
    for remaining in range(int(minutes), 0, -1):
        print(f"還有 {remaining} 分鐘...")
        time.sleep(60)  # 每分鐘倒數一次


if __name__ == '__main__':
    # 1. 設定 line token
    # 2. 設定 Google Sheet 名稱(id)
    # 3. 將token json檔案改名為 credentials.json
    # 4. 設定爬蟲網址 url 將條件設定好後複製上面網址貼上即可
    # 5. 將google api 服務帳號的email加入到google sheet分享名單

    # 這邊可以讓你設定token 以及google sheet名稱 以及爬蟲網址 以及休息時間
    all_delay_limit = int(os.environ.get('ALL_DELAY_LIMIT', 10))  # 整個程式最小休息時間（分鐘）
    all_delay_max = int(os.environ.get('ALL_DELAY_MAX', 20))  # 整個程式最大休息時間（分鐘）
    max_pages = int(os.environ.get("MAX_PAGES", 3))  # 最大爬取頁數(不指定可以999)
    line_token = os.environ.get("YOUR_LINE_TOKEN", "")
    sheet_name = os.environ.get("YOUR_GOOGLE_SHEET_ID", "")
    url = os.environ.get("YOUR_591_URL", 'https://sale.591.com.tw/?shType=list&regionid=17&role=1&publish_day=3&totalRows=9&firstRow=0')
    # 以下不用動///////////////////////////////////////////
    try:
        conn = init_db()  # 初始化 SQLite 資料庫
        conn.close()
        delay = int(random.uniform(60, 65))  # 隨機延遲時間 X-Y 秒
        data_json = parse_url_to_json(url)
        while True:  # 永久迴圈，讓 get_591 不斷執行
            get_591(data_json)  # 呼叫 get_591 函數

            # 產生隨機的延遲時間，單位為秒
            delay_minutes = int(random.uniform(all_delay_limit, all_delay_max))  # 隨機延遲 100 到 160 分鐘之間
            delay_seconds = delay_minutes * 60  # 將分鐘轉換為秒
            print(f"休息 {delay_minutes:.2f} 分鐘 ({delay_seconds:.2f} 秒)")
            countdown(delay_minutes)
    except Exception as e:
        print(str(e))
    input("按下任意鍵停止程式...")
