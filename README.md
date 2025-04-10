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

## 將 Windsurf 對話串整理成通用提示詞

請幫我建立一個網頁爬蟲程式，用於抓取以下網站的廠商資訊：

目標網站：[網站URL]

需求說明：
1. 我需要從主頁面抓取所有廠商的名稱
2. 點進每個廠商的詳細頁面，抓取其官方網站URL
3. 只需儲存廠商名稱和官方網站URL，不需要其他資訊
4. 當一頁處理完畢後，自動前往下一頁繼續抓取，直到所有頁面都處理完
5. 將結果保存為CSV和Excel格式

頁面結構說明：
- 主頁面上的廠商列表位於 [HTML元素位置，例如：<ul class="product">]
- 每個廠商的連結格式為 [連結格式，例如：visitorExhibitorDetail.asp?comNo=xxx]
- 廠商官網通常在詳細頁面的 [位置描述，例如：標示為"公司網址："的欄位]

其他要求：
- 加入適當的延遲，避免過度請求伺服器
- 處理可能的錯誤情況，確保程式不會因單一錯誤而中斷
- 定期保存已抓取的數據，以防程式意外中斷
- 使用Python和相關庫（如requests, BeautifulSoup, pandas等）