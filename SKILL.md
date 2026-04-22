---
name: agentmap
description: >
  Look up VeriGlow Agent Map for any website URL to discover its data functions,
  internal APIs, browser automation recipes, and agent reliability reports.
  Use when you need to extract structured data from a website, call a website's
  hidden API, or automate browser interactions with a web page.
license: MIT
compatibility: Works with Claude Code, OpenClaw, Cursor, and compatible AI agents
metadata:
  author: VeriGlow
  version: "0.2.0"
  openclaw:
    emoji: "🗺️"
    homepage: "https://veri-glow.com"
    requires:
      bins:
        - curl
---

# VeriGlow Agent Map

VeriGlow Agent Map is a registry of Agent-readable documentation for websites. Each "map" tells you exactly how to extract structured data from a specific web page — including hidden APIs, request parameters, response schemas, browser automation recipes, and real-world agent reports.

## When to Use This Skill

Use Agent Map when you need to:
- Get structured data from a website (financial data, government data, e-commerce, etc.)
- Discover hidden/internal APIs behind a web page
- Automate browser interactions with a specific site
- Check if other agents have successfully used a data source

## How to Query Agent Map

To look up a map for any URL, visit:

```
https://agentmap.veri-glow.com/{target-url-without-protocol}
```

For example, to find the map for `https://www.sse.com.cn/market/bonddata/overview/day/`:

```
https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/day/
```

You can also fetch the page content programmatically:

```bash
curl https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/day/
```

## What a Map Contains

Each Agent Map page has three sections:

### 1. Available Data
Documents every data function the page exposes:
- **API endpoint** (method, URL, parameters)
- **Request example** (curl command you can run directly)
- **Response schema** (column names, types, examples)
- **Caveats** (rate limits, IP restrictions, data freshness)

### 2. Page Internals
For browser automation fallback:
- **JS controller objects** and trigger methods
- **DOM selectors** for data tables and input fields
- **Rendering method** (server-side vs client-side)
- **Auth and anti-scraping** status
- **Complete action steps** (Playwright/Puppeteer recipe)

### 3. Agent Reports
Real-world usage reports from agents who have called this data source:
- Success/failure status and response times
- Edge cases discovered (half-day trading, IP blocks, etc.)
- Recommended workarounds

## Example: SSE Bond Trading Data

Here is a complete example of using an Agent Map to get Shanghai Stock Exchange bond trading data.

### Direct API Call (Preferred)

```bash
curl "https://query.sse.com.cn/commonQuery.do?sqlId=COMMON_SSEBOND_SCSJ_SCTJ_CJSJ_ZQLXCJTJ_CX_L&START_DATE=2025-02-11&END_DATE=2025-02-11" \
  -H "Referer: https://www.sse.com.cn/market/bonddata/overview/day/"
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| sqlId | string | Yes | Fixed value: `COMMON_SSEBOND_SCSJ_SCTJ_CJSJ_ZQLXCJTJ_CX_L` |
| START_DATE | string | Yes | Start date in `YYYY-MM-DD` format |
| END_DATE | string | Yes | End date in `YYYY-MM-DD` format |
| Referer header | string | Yes | Must be `https://www.sse.com.cn/market/bonddata/overview/day/` |

**Returns:** JSON with 17 rows × 4 columns:

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| 债券品种 | string | 国债 | Bond type category |
| 成交笔数 | number | 15,234 | Number of trades |
| 成交面额(亿元) | number | 2,068.77 | Face value traded (100M RMB) |
| 成交金额(亿元) | number | 2,087.45 | Trading amount (100M RMB) |

**Bond types (17 categories):** 国债, 地方政府债, 企业债, 公司债, 可转换债, 可分离债, 资产支持证券, 国际机构债, 政策性金融债, 同业存单, and more.

**Caveats:**
- Non-trading days (weekends, holidays) return all-zero rows
- Data availability: T+1, updated ~1 hour after market close (15:30 CST)
- Overseas IP may get 403 — use a CN-based proxy if needed

### Browser Automation Fallback

If the direct API is blocked, use these action steps:

```javascript
// Step 1: Set date
document.querySelector('.js_date input').value = '2025-02-11'

// Step 2: Trigger query (wait 3s for AJAX response)
overviewDay.setOverviewDayParams()

// Step 3: Extract table
const table = document.querySelector('.table-responsive table')
const headers = [...table.querySelectorAll('thead th')].map(th => th.textContent.trim())
const rows = [...table.querySelectorAll('tbody tr')].map(tr =>
  [...tr.querySelectorAll('td')].map(td => td.textContent.trim())
)
```

## Reporting Issues

When you encounter problems with a map, report them so the data can be improved:

```bash
curl -s -X POST "https://agentmap.veri-glow.com/api/request-map" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "www.sse.com.cn/market/stockdata/marketvalue/main",
    "type": "incomplete",
    "detail": "Missing date query parameter: SEARCH_DATE (YYYY-MM-DD format), LIST_BOARD, NEGO_VALUE_DESC",
    "user_query": "what the user asked"
  }'
```

**Issue types:**
| type | When to use |
|------|------------|
| `missing` | URL not indexed in AgentMap at all (404) |
| `incomplete` | Map exists but parameters, response fields, or caveats are missing |
| `incorrect` | Map data is wrong (endpoint changed, parameters renamed, etc.) |

**When to report `incomplete`:** If you had to reverse-engineer the page (read JS source, guess parameter names) to make the API work, the map is incomplete. Report what you discovered so future agents don't repeat the work.

## Best Practices

1. **Always prefer direct API calls** over browser automation — they are faster and more reliable
2. **Check the Agent Reports section** before calling a new data source — other agents may have documented edge cases
3. **Respect rate limits** — if a map documents rate limiting, throttle your requests accordingly
4. **Handle IP restrictions** — some Chinese government/financial data sources block overseas IPs; use a CN proxy when noted
5. **Verify data freshness** — check the "Data availability" note for each source (e.g., T+1 means data is from the previous trading day)
6. **Report issues** — if a map is missing, incomplete, or incorrect, report it via the API above

## Example: FRED Economic Data

Here is an example of using Agent Map to get US 10-Year Treasury yield data from FRED.

### Direct API Call

```bash
curl "https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&observation_start=2025-03-01&observation_end=2026-03-14&api_key=YOUR_API_KEY&file_type=json"
```

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| series_id | string | Yes | FRED series ID (e.g. GDP, DGS10, CPIAUCSL, FEDFUNDS) |
| api_key | string | Yes | Free API key from https://fred.stlouisfed.org/docs/api/api_key.html |
| file_type | string | Yes | Always `json` |
| observation_start | string | No | Start date `YYYY-MM-DD` |
| observation_end | string | No | End date `YYYY-MM-DD` |
| frequency | string | No | Aggregation: `d`, `w`, `m`, `q`, `a` |
| units | string | No | Transform: `lin` (levels), `pch` (% change), `log` |

**Returns:** JSON with `observations` array of date-value pairs:

```json
{
  "observations": [
    {"date": "2025-03-03", "value": "4.24"},
    {"date": "2025-03-04", "value": "4.18"},
    {"date": "2025-03-05", "value": "4.26"}
  ]
}
```

**Key FRED Series:** GDP, CPIAUCSL (CPI), FEDFUNDS (Fed Funds Rate), DGS10 (10Y Treasury), DGS2 (2Y Treasury), T10Y2Y (10Y-2Y Spread), UNRATE (Unemployment), M2SL (M2 Money Supply), DEXUSEU (USD/EUR), VIXCLS (VIX).

**Caveats:**
- Free API key required — register at https://fred.stlouisfed.org/docs/api/api_key.html
- Rate limit: ~120 requests/minute
- Daily series return `'.'` for weekends/holidays (not null)
- No IP restrictions

## Available Maps (65 data sources)

Currently indexed: **55 Shanghai Stock Exchange pages** + 6 FRED endpoints + 4 international APIs.

### Shanghai Stock Exchange (上海证券交易所) — 55 maps

**Stock Data (股票数据):**

| Source | URL | Functions |
|--------|-----|-----------|
| [Market Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/view/) | `www.sse.com.cn/market/view/` | 1 |
| [Statistics Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/statistic/) | `www.sse.com.cn/market/stockdata/statistic/` | 1 |
| [Stock Weekly Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/overview/weekly/) | `www.sse.com.cn/market/stockdata/overview/weekly/` | 1 |
| [Stock Monthly Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/overview/monthly/) | `www.sse.com.cn/market/stockdata/overview/monthly/` | 1 |
| [IPO First-Day Performance](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/firstday/) | `www.sse.com.cn/market/stockdata/firstday/` | 1 |
| [IPO (Initial Public Offering)](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/raise/ipo/) | `www.sse.com.cn/market/stockdata/raise/ipo/` | 1 |
| [Secondary Offering](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/raise/additional/) | `www.sse.com.cn/market/stockdata/raise/additional/` | 1 |
| [Rights Issue](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/raise/allotment/) | `www.sse.com.cn/market/stockdata/raise/allotment/` | 1 |
| [Share Capital Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/structure/overview/) | `www.sse.com.cn/market/stockdata/structure/overview/` | 3 |
| [Share Capital Ranking](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/structure/rank/) | `www.sse.com.cn/market/stockdata/structure/rank/` | 1 |
| [Cash Dividends](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/dividends/dividend/) | `www.sse.com.cn/market/stockdata/dividends/dividend/` | 1 |
| [Bonus Shares](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/dividends/bonus/) | `www.sse.com.cn/market/stockdata/dividends/bonus/` | 1 |
| [Shanghai Market P/E Ratio](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/price/sh/) | `www.sse.com.cn/market/stockdata/price/sh/` | 1 |
| [Main Board Market Cap Ranking](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/marketvalue/main/) | `www.sse.com.cn/market/stockdata/marketvalue/main/` | 1 |
| [STAR Market Market Cap Ranking](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/marketvalue/star/) | `www.sse.com.cn/market/stockdata/marketvalue/star/` | 1 |
| [Main Board Trading Activity](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/activity/main/) | `www.sse.com.cn/market/stockdata/activity/main/` | 1 |
| [STAR Market Trading Activity](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/activity/star/) | `www.sse.com.cn/market/stockdata/activity/star/` | 1 |
| [Preferred Share Statistics](https://agentmap.veri-glow.com/www.sse.com.cn/market/stockdata/pshare/) | `www.sse.com.cn/market/stockdata/pshare/` | 1 |

**Index Data (指数):**

| Source | URL | Functions |
|--------|-----|-----------|
| [Key Index & Sample Performance](https://agentmap.veri-glow.com/www.sse.com.cn/market/sseindex/overview/focus/) | `www.sse.com.cn/market/sseindex/overview/focus/` | 1 |
| [Index Basic Information](https://agentmap.veri-glow.com/www.sse.com.cn/market/sseindex/indexlist/basic/) | `www.sse.com.cn/market/sseindex/indexlist/basic/` | 4 |
| [Index Quotation](https://agentmap.veri-glow.com/www.sse.com.cn/market/sseindex/quotation/) | `www.sse.com.cn/market/sseindex/quotation/` | 1 |

**Fund Data (基金数据):**

| Source | URL | Functions |
|--------|-----|-----------|
| [Fund Daily Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/funddata/overview/day/) | `www.sse.com.cn/market/funddata/overview/day/` | 1 |
| [Fund Weekly Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/funddata/overview/weekly/) | `www.sse.com.cn/market/funddata/overview/weekly/` | 1 |
| [Fund Monthly Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/funddata/overview/monthly/) | `www.sse.com.cn/market/funddata/overview/monthly/` | 1 |
| [Fund Annual Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/funddata/overview/yearly/) | `www.sse.com.cn/market/funddata/overview/yearly/` | 1 |
| [Public REITs Scale](https://agentmap.veri-glow.com/www.sse.com.cn/market/funddata/volumn/reits/) | `www.sse.com.cn/market/funddata/volumn/reits/` | 1 |
| [LOF Scale](https://agentmap.veri-glow.com/www.sse.com.cn/market/funddata/volumn/lofvolumn/) | `www.sse.com.cn/market/funddata/volumn/lofvolumn/` | 2 |
| [Graded LOF Fund Scale](https://agentmap.veri-glow.com/www.sse.com.cn/market/funddata/volumn/fjlofvolumn/) | `www.sse.com.cn/market/funddata/volumn/fjlofvolumn/` | 1 |

**Bond Data (债券数据):**

| Source | URL | Functions |
|--------|-----|-----------|
| [Bond Daily Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/day/) | `www.sse.com.cn/market/bonddata/overview/day/` | 1 |
| [Bond Weekly Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/weekly/) | `www.sse.com.cn/market/bonddata/overview/weekly/` | 1 |
| [Bond Monthly Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/monthly/) | `www.sse.com.cn/market/bonddata/overview/monthly/` | 1 |
| [Bond Annual Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/overview/yearly/) | `www.sse.com.cn/market/bonddata/overview/yearly/` | 1 |
| [Bond Statistics](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/statistic/) | `www.sse.com.cn/market/bonddata/statistic/` | 1 |
| [Convertible Bond Trading](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/dxkzzcj/) | `www.sse.com.cn/market/bonddata/dxkzzcj/` | 1 |
| [Exchangeable Bond Conversion](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/exchangeable/) | `www.sse.com.cn/market/bonddata/exchangeable/` | 2 |
| [Bond Yield Statistics](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/profit/) | `www.sse.com.cn/market/bonddata/profit/` | 1 |
| [Bond Clean & Dirty Price](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/netfull/) | `www.sse.com.cn/market/bonddata/netfull/` | 1 |
| [Active Bond Varieties](https://agentmap.veri-glow.com/www.sse.com.cn/market/bonddata/livelybond/) | `www.sse.com.cn/market/bonddata/livelybond/` | 1 |

**Other Data (其他数据):**

| Source | URL | Functions |
|--------|-----|-----------|
| [Margin Trading Summary](https://agentmap.veri-glow.com/www.sse.com.cn/market/othersdata/margin/sum/) | `www.sse.com.cn/market/othersdata/margin/sum/` | 1 |
| [Margin Trading Detail](https://agentmap.veri-glow.com/www.sse.com.cn/market/othersdata/margin/detail/) | `www.sse.com.cn/market/othersdata/margin/detail/` | 2 |
| [Securities Lending Overview](https://agentmap.veri-glow.com/www.sse.com.cn/market/othersdata/refinancing/lend/) | `www.sse.com.cn/market/othersdata/refinancing/lend/` | 1 |
| [Strategic Placement Lending (Main)](https://agentmap.veri-glow.com/www.sse.com.cn/market/othersdata/zlpskcjxx/main/) | `www.sse.com.cn/market/othersdata/zlpskcjxx/main/` | 1 |
| [Strategic Placement Lending (STAR)](https://agentmap.veri-glow.com/www.sse.com.cn/market/othersdata/zlpskcjxx/star/) | `www.sse.com.cn/market/othersdata/zlpskcjxx/star/` | 1 |
| [Asset Management Share Transfer](https://agentmap.veri-glow.com/www.sse.com.cn/market/othersdata/asset/) | `www.sse.com.cn/market/othersdata/asset/` | 1 |
| [Member List](https://agentmap.veri-glow.com/www.sse.com.cn/market/othersdata/memberdata/memberlist/) | `www.sse.com.cn/market/othersdata/memberdata/memberlist/` | 1 |
| ...and 10 more member/business qualification pages | | |

### FRED (Federal Reserve Economic Data) — 6 maps

| Source | URL | Functions |
|--------|-----|-----------|
| [Time Series Data](https://agentmap.veri-glow.com/fred.stlouisfed.org/series/observations/) | `fred.stlouisfed.org/series/observations/` | 1 |
| [Search Series](https://agentmap.veri-glow.com/fred.stlouisfed.org/series/search/) | `fred.stlouisfed.org/series/search/` | 1 |
| [Series Metadata](https://agentmap.veri-glow.com/fred.stlouisfed.org/series/) | `fred.stlouisfed.org/series/` | 1 |
| [Browse by Category](https://agentmap.veri-glow.com/fred.stlouisfed.org/category/series/) | `fred.stlouisfed.org/category/series/` | 1 |
| [Release Calendar](https://agentmap.veri-glow.com/fred.stlouisfed.org/releases/) | `fred.stlouisfed.org/releases/` | 1 |
| [Discover by Tag](https://agentmap.veri-glow.com/fred.stlouisfed.org/tags/series/) | `fred.stlouisfed.org/tags/series/` | 1 |

### International APIs — 4 maps

| Source | URL | Functions |
|--------|-----|-----------|
| [Cryptocurrency Market Data](https://agentmap.veri-glow.com/coinpaprika.com/coin/btc-bitcoin/) | `coinpaprika.com/coin/btc-bitcoin/` | 1 |
| [Weather Forecast API](https://agentmap.veri-glow.com/open-meteo.com/en/docs/) | `open-meteo.com/en/docs/` | 1 |
| [Hacker News Top Stories](https://agentmap.veri-glow.com/news.ycombinator.com/) | `news.ycombinator.com/` | 2 |

More maps are being added continuously. Visit [veri-glow.com](https://veri-glow.com) to browse all 65 maps or request a new one.
