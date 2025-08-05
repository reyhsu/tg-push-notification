# Telegram 廣告推播機器人

這是一個 Telegram 機器人，它可以監聽一個指定的來源頻道，並將所有發布到該頻道的訊息自動轉發到多個目標頻道或群組。

## 設定步驟

1.  **取得 Bot Token:**
    *   在 Telegram 上與 [@BotFather](https://t.me/BotFather) 對話。
    *   輸入 `/newbot` 來建立一個新的機器人。
    *   遵照指示，你將會得到一個 `BOT_TOKEN`。

2.  **取得頻道/群組 ID:**
    *   將你剛剛建立的機器人加入你的**來源頻道/群組**以及所有**目標頻道/群組**。
    *   **重要:** 必須將機器人設為管理員，並給予其發布訊息的權限。
    *   在你的來源頻道/群組發布一則任意訊息。
    *   開啟瀏覽器，訪問 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` (將 `<YOUR_BOT_TOKEN>` 替換成你的 Token)。
    *   你會看到一段 JSON 資料。在 `result` 陣列中，找到 `message` -> `chat` -> `id` (สำหรับ群組) 或 `channel_post` -> `chat` -> `id` (สำหรับ頻道)。這個 `id` 就是你的來源 ID。
    *   用同樣的方法取得所有目標的 ID。

3.  **停用群組隱私模式 (如果使用群組):**
    *   如果你的來源或目標是**群組 (Group)**，你必須停用機器人的隱私模式，否則它將無法接收到群組中的一般訊息。
    *   在 Telegram 中，開啟與 [@BotFather](https://t.me/BotFather) 的對話。
    *   發送 `/mybots` 並選擇你的機器人。
    *   選擇 **Bot Settings** -> **Group Privacy**。
    *   點擊 **Turn off** 按鈕。確保最終狀態為 `Privacy: DISABLED`。

4.  **設定環境變數:**
    *   在專案根目錄下，複製範本檔案：
        ```bash
        cp .env.example .env
        ```
    *   編輯 `.env` 檔案，填入你先前取得的 `BOT_TOKEN` 和 `SOURCE_CHANNEL_ID`。
        *   `SOURCE_CHANNEL_ID` 是您將要下達指令的來源群組/頻道 ID。

## 如何執行

確定你已經安裝了 Docker 和 Docker Compose。

在專案根目錄下，執行以下指令來建立並在背景啟動機器人：

```bash
docker-compose up -d --build
```

## 如何使用

設定並啟動機器人後，您可以透過在**來源頻道/群組**中下達特定指令來管理目標群組並轉發訊息。

### 管理目標群組

*   **新增群組:**
    *   **指令:** `/add <Group_ID> <Group_Name>`
    *   **說明:** 新增一個要轉發訊息的目標群組。`Group_ID` 必須是數字，`Group_Name` 可以包含空格。
    *   **範例:** `/add -1001234567890 我的第一個群組`

*   **移除群組:**
    *   **指令:** `/remove <Group_ID>`
    *   **說明:** 從目標清單中移除一個群組。
    *   **範例:** `/remove -1001234567890`

*   **列出群組:**
    *   **指令:** `/list`
    *   **說明:** 顯示所有已儲存的目標群組及其名稱和 ID。

*   **顯示幫助:**
    *   **指令:** `/help`
    *   **說明:** 顯示所有可用的指令及其用法。

### 轉發訊息

轉發訊息是透過**回覆 (Reply)** 你想要轉發的訊息來達成的。

*   **轉發到指定群組:**
    *   **操作:** 在來源群組中，**回覆**您想轉發的訊息，並輸入以下指令。
    *   **指令:** `/send <Group_Name_1>,<Group_Name_2>,...`
    *   **說明:** 將您回覆的訊息僅發送到指定的目標群組。可以提供一個或多個 Group Name，並以逗號分隔。群組名稱不區分大小寫。
    *   **範例 (單一目標):** 回覆一則訊息並輸入 `/send My Awesome Group`
    *   **範例 (多個目標):** 回覆一則訊息並輸入 `/send My Awesome Group,Another Group`

*   **廣播到所有群組:**
    *   **操作:** 在來源群組中，**回覆**您想轉發的訊息，並輸入以下指令。
    *   **指令:** `/broadcast`
    *   **說明:** 將您回覆的訊息發送到所有已儲存的目標群組。

## 停止機器人

```bash
docker-compose down
```
