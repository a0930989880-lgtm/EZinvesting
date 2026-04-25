import discord
from discord.ext import commands
from discord import app_commands
import yfinance as yf
import pandas as pd
import ta
import os
from openai import OpenAI
import mplfinance as mpf
import json

# ===== 分類股票 =====
stock_categories = {
    "半導體": {},
    "AI": {},
    "散熱": {},
    "光通訊": {}
}

def save_data():
    with open("stocks.json", "w", encoding="utf-8") as f:
        json.dump(stock_categories, f, ensure_ascii=False)

def load_data():
    global stock_categories
    try:
        with open("stocks.json", "r", encoding="utf-8") as f:
            stock_categories = json.load(f)
    except:
        pass

def save_stocks():
    with open("stocks.json", "w", encoding="utf-8") as f:
        json.dump(stock_map, f, ensure_ascii=False)

def load_stocks():
    global stock_map
    try:
        with open("stocks.json", "r", encoding="utf-8") as f:
            stock_map = json.load(f)
    except:
        pass

market_pool = {

# ===== 晶圓代工 / 製造 =====
"台積電": "2330",
"聯電": "2303",
"世界": "5347",
"力積電": "6770",
"台亞": "2340",
"茂矽": "2342",

# ===== IC設計 =====
"聯發科": "2454",
"瑞昱": "2379",
"聯詠": "3034",
"創意": "3443",
"世芯-KY": "3661",
"智原": "3035",
"敦泰": "3545",
"矽統": "2363",
"原相": "3227",
"群聯": "8299",

# ===== 先進封裝 / 封測 =====
"日月光投控": "3711",
"矽品": "2325",
"京元電子": "2449",
"欣銓": "3264",
"頎邦": "6147",
"力成": "6239",
"南茂": "8150",

# ===== 記憶體 =====
"南亞科": "2408",
"華邦電": "2344",
"旺宏": "2337",
"威剛": "3260",

# ===== 半導體設備 =====
"漢唐": "2404",
"帆宣": "6196",
"亞翔": "6139",
"京鼎": "3413",
"弘塑": "3131",
"家登": "3680",
"中砂": "1560",
"萬潤": "6187",
"均豪": "5443",

# ===== 載板 / PCB / 基板 =====
"欣興": "3037",
"南電": "8046",
"景碩": "3189",
"臻鼎-KY": "4958",

# ===== 散熱（AI核心）=====
"奇鋐": "3017",
"雙鴻": "3324",
"健策": "3653",
"泰碩": "3338",

# ===== 光通訊（AI資料中心）=====
"光寶科": "2301",
"智邦": "2345",
"中磊": "5388",
"合勤控": "3704",
"聯亞": "3081",
"上詮": "3363",

# ===== 低軌衛星 =====
"台揚": "2314",
"昇達科": "3491",
"穩懋": "3105",
"啟碁": "6285",

# ===== 矽晶圓 / 上游材料 =====
"環球晶": "6488",
"台勝科": "3532",
"合晶": "6182",

# ===== AI伺服器 / 系統 =====
"鴻海": "2317",
"廣達": "2382",
"緯創": "3231",
"英業達": "2356",
"緯穎": "6669",

# ===== 電源 / AI基礎 =====
"台達電": "2308",
"光寶科": "2301",

# ===== 其他AI關鍵 =====
"信驊": "5274",
"力旺": "3529"
}

def backtest_winrate(df):

    wins = 0
    total = 0

    for i in range(60, len(df) - 5):

        window = df.iloc[:i]

        price = window["Close"].iloc[-1]

        MA20 = window["Close"].rolling(20).mean().iloc[-1]
        MA60 = window["Close"].rolling(60).mean().iloc[-1]
        RSI = ta.momentum.RSIIndicator(window["Close"]).rsi().iloc[-1]

        macd = ta.trend.MACD(window["Close"])
        macd_val = macd.macd().iloc[-1]
        macd_sig = macd.macd_signal().iloc[-1]

        support = window["Low"].tail(30).min()

        # ===== 條件 =====
        cond = (
            RSI < 40 and
            MA20 > MA60 and
            price <= support * 1.03 and
            macd_val > macd_sig
        )

        if cond:
            total += 1

            future_price = df["Close"].iloc[i + 5]

            if future_price > price:
                wins += 1

    if total == 0:
        return 0, 0

    return wins, total

def plot_kline(df):

    df = df.copy()

    df["MA5"] = df["Close"].rolling(5).mean()
    df["MA10"] = df["Close"].rolling(10).mean()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()

    style = mpf.make_mpf_style(
        base_mpf_style='nightclouds',
        rc={'font.size': 8}
    )

    mpf.plot(
        df,
        type='candle',
        mav=(5,10,20,60),
        volume=True,
        style=style,
        figsize=(10,6),
        tight_layout=True,
        savefig="chart.png"
    )

# ===== Token =====
import os
token = os.getenv("TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== 股票 =====
stock_map =  {
    "台積電": "2330","聯電": "2303","世界先進": "5347","力積電": "6770",
    "聯發科": "2454","創意": "3443","世芯-KY": "3661",
    "緯穎": "6669",
    "萬潤": "6187",
    "奇鋐": "3017","雙鴻": "3324","健策": "3653",
    "聯亞": "3081",
    "欣興": "3037","南電": "8046","景碩": "3189","臻鼎-KY": "4958",
    "南亞科": "2408","華邦電": "2344",
    "台達電": "2308","信驊": "5274"
}

# =========================
# autocomplete（搜尋框）
# =========================
async def stock_autocomplete(interaction, current):
    return [
        app_commands.Choice(name=f"{k} ({v})", value=v)
        for k, v in stock_map.items()
        if current.lower() in k.lower()
    ]

# =========================
# 抓資料
# =========================
def get_df(code):
    try:
        # 先試上市
        df = yf.Ticker(f"{code}.TW").history(period="3mo")

        # 如果沒資料 → 試上櫃
        if df.empty:
            df = yf.Ticker(f"{code}.TWO").history(period="3mo")

        return df if not df.empty else None

    except:
        return None

# =========================
# UI + GPT分析
# =========================
def build_embed(df, code):

    price = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]

    change = price - prev
    percent = change / prev * 100

    arrow = "🔺" if change >= 0 else "🔻"
    color = 0x00ff00 if change >= 0 else 0xff0000

    # ===== 技術 =====
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA60"] = df["Close"].rolling(60).mean()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

    # ===== 成交量 & MACD =====
    df["Volume_MA20"] = df["Volume"].rolling(20).mean()
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    latest = df.iloc[-1]

    trend = "多頭" if latest["MA20"] > latest["MA60"] else "空頭"
    support = df["Low"].tail(30).min()
    resistance = df["High"].tail(30).max()

    name = next((k for k, v in stock_map.items() if v == code), code)

    # ===== AI評分系統 =====
    score = 0
    reasons = []

    # RSI
    if latest["RSI"] > 70:
        score -= 2
        reasons.append("RSI過熱")
    elif latest["RSI"] < 30:
        score += 2
        reasons.append("RSI超賣")

    # 均線
    if latest["MA20"] > latest["MA60"]:
        score += 2
        reasons.append("多頭排列")
    else:
        score -= 1
        reasons.append("空頭結構")

    # 價格位置
    if price <= support * 1.03:
        score += 2
        reasons.append("接近支撐")
    elif price >= resistance * 0.97:
        score -= 2
        reasons.append("接近壓力")

    # 成交量爆量
    if latest["Volume"] > latest["Volume_MA20"] * 1.5:
        if change > 0:
            score += 2
            reasons.append("放量上漲")
        else:
            score -= 2
            reasons.append("放量下跌")

    # MACD
    if latest["MACD"] > latest["MACD_signal"]:
        score += 1
        reasons.append("MACD多頭")
    else:
        score -= 1
        reasons.append("MACD空頭")

    # 回踩均線
    if latest["MA20"] > latest["MA60"] and price < latest["MA20"]:
        score += 1
        reasons.append("回踩均線")

    # 跌破支撐
    if price < support:
        score -= 3
        reasons.append("跌破支撐")

    # ===== AI結論 =====
    if score >= 5:
        ai_text = f"🚀 強多，可積極關注進場。\n依據：{', '.join(reasons)}。\n建議分批布局，停損設支撐下方。"
    elif score >= 3:
        ai_text = f"📈 偏多，具進場機會。\n依據：{', '.join(reasons)}。\n建議等待回檔或量縮再進場。"
    elif score >= 1:
        ai_text = f"🟡 中性偏多。\n依據：{', '.join(reasons)}。\n觀察支撐是否守穩。"
    elif score <= -4:
        ai_text = f"❌ 偏空風險高。\n依據：{', '.join(reasons)}。\n建議觀望或等待止跌。"
    elif score <= -2:
        ai_text = f"📉 偏弱，不建議進場。\n依據：{', '.join(reasons)}。"
    else:
        ai_text = f"⚖️ 盤整格局。\n依據：{', '.join(reasons)}。\n等待方向明確。"

    # ===== UI =====
    embed = discord.Embed(
        title=f"{'🟢📈' if change>=0 else '🔴📉'} {name} ({code})",
        color=color
    )

    embed.description = "━━━━━━━━━━━━━━━━━━"

    embed.add_field(
        name="💰 現價",
        value=f"```yaml\n{price:.2f}\n{arrow} {change:.2f} ({percent:.2f}%)\n```",
        inline=True
    )

    embed.add_field(
        name="📊 技術",
        value=f"```yaml\n趨勢: {trend}\nRSI: {latest['RSI']:.1f}\n```",
        inline=True
    )

    embed.add_field(
        name="📉 壓力 / 支撐",
        value=f"```yaml\n支撐: {support:.2f}\n壓力: {resistance:.2f}\n```",
        inline=False
    )

    embed.add_field(
        name="🤖 AI進場分析",
        value=f"```diff\n+ {ai_text}\n```",
        inline=False
    )

    return embed

# =========================
# 啟動
# =========================
@bot.event
async def on_ready():
    load_data()

    print(f"✅ {bot.user}")
    synced = await bot.tree.sync()
    print(f"同步 {len(synced)} 個指令")

# =========================
# 查詢股票（完整版）
# =========================
@bot.tree.command(name="查詢股票")
@app_commands.autocomplete(code=stock_autocomplete)
async def stock(interaction: discord.Interaction, code: str):

    await interaction.response.defer()

    df = get_df(code)

    if df is None:
        await interaction.followup.send("❌ 查不到資料")
        return

    # 🔥 畫K線圖
    plot_kline(df)

    # 🔥 建立UI
    embed = build_embed(df, code)

    # 🔥 圖片附加
    file = discord.File("chart.png", filename="chart.png")
    embed.set_image(url="attachment://chart.png")

    # 🔥 回傳
    await interaction.followup.send(embed=embed, file=file)

@bot.tree.command(name="ai_pick")
async def ai_pick_entry(interaction: discord.Interaction):

    await interaction.response.defer()

    results = []

    # ===== 掃描分類 =====
    for cat_name, cat in stock_categories.items():
        for name, code in cat.items():

            df = get_df(code)
            if df is None or len(df) < 60:
                continue

            try:
                # ===== 指標 =====
                df["MA20"] = df["Close"].rolling(20).mean()
                df["MA60"] = df["Close"].rolling(60).mean()
                df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
                df["Volume_MA20"] = df["Volume"].rolling(20).mean()

                macd = ta.trend.MACD(df["Close"])
                df["MACD"] = macd.macd()
                df["MACD_signal"] = macd.macd_signal()

                latest = df.iloc[-1]

                price = latest["Close"]
                support = df["Low"].tail(30).min()
                resistance = df["High"].tail(30).max()

                score = 0
                reason = []

                # ===== 評分 =====
                if latest["RSI"] < 40:
                    score += 2
                    reason.append("RSI低檔")
                elif latest["RSI"] > 70:
                    score -= 2

                if latest["MA20"] > latest["MA60"]:
                    score += 2
                    reason.append("多頭趨勢")

                if price <= support * 1.03:
                    score += 2
                    reason.append("接近支撐")

                if latest["Volume"] > latest["Volume_MA20"] * 1.5:
                    score += 2
                    reason.append("放量")

                if latest["MACD"] > latest["MACD_signal"]:
                    score += 1
                    reason.append("MACD翻多")

                # ===== 勝率 =====
                wins, total = backtest_winrate(df)
                winrate = (wins / total * 100) if total > 0 else 0

                # ===== 策略 =====
                entry = round(support * 1.02, 2)
                stop = round(support * 0.97, 2)
                target = round(resistance * 0.98, 2)

                results.append({
                    "name": name,
                    "code": code,
                    "score": score,
                    "price": price,
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "reason": ", ".join(reason),
                    "winrate": round(winrate, 1)
                })

            except:
                continue

    # ===== 排序 =====
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    if not results:
        await interaction.followup.send("❌ 沒有符合條件的股票")
        return

    # ===== UI =====
    embed = discord.Embed(
        title="🤖 AI進場選股",
        description="📊 技術面 + 動能 + 支撐策略 + 回測勝率",
        color=0x00ff00
    )

    for i, r in enumerate(results, 1):
        embed.add_field(
            name=f"{i}. {r['name']} ({r['code']}) ⭐{r['score']}",
            value=(
                f"💰 現價：{r['price']:.2f}\n"
                f"🎯 進場：{r['entry']}\n"
                f"🛑 停損：{r['stop']}\n"
                f"🎯 目標：{r['target']}\n"
                f"📊 勝率：{r['winrate']}%\n"
                f"📌 條件：{r['reason']}"
            ),
            inline=False
        )

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="scan")
async def ai_scan(interaction: discord.Interaction):

    await interaction.response.defer()

    results = []

    for name, code in market_pool.items():

        df = get_df(code)
        if df is None or len(df) < 60:
            continue

        try:
            # ===== 指標 =====
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA60"] = df["Close"].rolling(60).mean()
            df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
            df["Volume_MA20"] = df["Volume"].rolling(20).mean()

            macd = ta.trend.MACD(df["Close"])
            df["MACD"] = macd.macd()
            df["MACD_signal"] = macd.macd_signal()

            latest = df.iloc[-1]

            price = latest["Close"]
            support = df["Low"].tail(30).min()
            resistance = df["High"].tail(30).max()

            score = 0

            # ===== AI條件 =====
            if latest["RSI"] < 40:
                score += 2
            if latest["MA20"] > latest["MA60"]:
                score += 2
            if price <= support * 1.03:
                score += 2
            if latest["Volume"] > latest["Volume_MA20"] * 1.5:
                score += 2
            if latest["MACD"] > latest["MACD_signal"]:
                score += 1

            # ===== 勝率 =====
            wins, total = backtest_winrate(df)
            winrate = (wins / total * 100) if total > 0 else 0

            # ===== 過濾條件（超重要🔥）=====
            if score >= 4 and winrate >= 55:

                results.append({
                    "name": name,
                    "code": code,
                    "score": score,
                    "price": price,
                    "winrate": round(winrate,1)
                })

        except:
            continue

    # ===== 排序 =====
    results = sorted(results, key=lambda x: (x["score"], x["winrate"]), reverse=True)[:10]

    if not results:
        await interaction.followup.send("❌ 今天沒有強勢股")
        return

    # ===== UI =====
    embed = discord.Embed(
        title="🚀 全市場 AI選股",
        description="📊 高分 + 高勝率 篩選",
        color=0x00ff00
    )

    text = ""

    for i, r in enumerate(results, 1):
        text += (
            f"{i}. **{r['name']} ({r['code']})**\n"
            f"💰 {r['price']:.2f} ｜ ⭐{r['score']} ｜ 📊 {r['winrate']}%\n\n"
        )

    embed.add_field(name="📈 今日強勢股", value=text, inline=False)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="add_stock", description="新增股票")
async def add_stock(interaction: discord.Interaction, name: str, code: str):

    stock_map[name] = code
    save_stocks()   # 🔥 這裡

    await interaction.response.send_message(
        f"✅ 已新增：{name} ({code})"
    )


@bot.tree.command(name="list_stock", description="查看股票清單")
async def list_stock(interaction: discord.Interaction):

    text = ""

    for name, code in stock_map.items():
        text += f"{name} ({code})\n"

    await interaction.response.send_message(
        f"📊 股票列表\n{text}"
    )

@bot.tree.command(name="remove_stock", description="刪除股票")
async def remove_stock(interaction: discord.Interaction, name: str):

    if name in stock_map:
        del stock_map[name]
        save_stocks()   # 🔥 這裡

        await interaction.response.send_message(f"🗑️ 已刪除 {name}")
    else:
        await interaction.response.send_message("❌ 找不到這檔股票")

@bot.tree.command(name="add_cat", description="新增分類股票")
async def add_cat(interaction: discord.Interaction, category: str, name: str, code: str):

    if category not in stock_categories:
        stock_categories[category] = {}

    stock_categories[category][name] = code

    save_data()

    await interaction.response.send_message(
        f"✅ 已新增：[{category}] {name} ({code})"
    )

@bot.tree.command(name="list_cat", description="查看分類股票")
async def list_cat(interaction: discord.Interaction, category: str):

    if category not in stock_categories:
        await interaction.response.send_message("❌ 沒有這個分類")
        return

    text = ""

    for name, code in stock_categories[category].items():
        text += f"{name} ({code})\n"

    if text == "":
        text = "（空）"

    await interaction.response.send_message(
        f"📂 {category}\n{text}"
    )

@bot.tree.command(name="list_all_cat", description="查看所有分類")
async def list_all_cat(interaction: discord.Interaction):

    text = ""

    for cat, stocks in stock_categories.items():
        text += f"📂 {cat}（{len(stocks)}檔）\n"

    await interaction.response.send_message(text)

@bot.event
async def on_disconnect():
    print("⚠️ 斷線，嘗試重連")


bot.run(token)