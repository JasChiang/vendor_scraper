# Vendor Scraper for PetsShow Taipei

這個爬蟲程式用於抓取台北寵物用品展的廠商名稱以及廠商官網網址。

## 功能

- 抓取廠商名稱
- 抓取廠商詳細頁面連結
- 從廠商詳細頁面抓取官網網址
- 自動分頁抓取，直到所有頁面都處理完畢
- 將結果保存為 CSV 和 Excel 格式

## 安裝需求

```bash
pip install -r requirements.txt
```

## 使用方法

1. 確保已安裝所有依賴套件
2. 執行爬蟲程式：

```bash
python vendor_scraper.py
```

3. 程式會自動創建 `output` 目錄並將結果保存在：
   - `output/vendors_data.csv`
   - `output/vendors_data.xlsx`

## 注意事項

- 程式會在每個頁面之間添加延遲，以避免過度請求伺服器
- 如果程式執行中斷，已抓取的數據會被保存
- 每抓取一頁後，會自動保存當前結果
