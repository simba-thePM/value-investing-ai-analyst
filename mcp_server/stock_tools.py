"""
MCP server exposing live Indian stock market data as tools.

Run standalone for testing:
    python mcp_server/stock_tools.py

This uses the official MCP Python SDK (`mcp` package) with the FastMCP
convenience wrapper. It exposes two tools:

  - get_stock_price(ticker): latest price + day change for an NSE-listed stock
  - get_financial_ratios(ticker): P/E, ROE, debt/equity, market cap, etc.

Tickers should be NSE symbols with the ".NS" suffix, e.g. "TCS.NS",
"HDFCBANK.NS", "ASIANPAINT.NS", "ITC.NS", "TITAN.NS".

Data source: yfinance (free, unofficial Yahoo Finance wrapper). Good enough
for a portfolio demo; swap for a paid/official NSE feed for production use.
"""

from mcp.server.fastmcp import FastMCP
import yfinance as yf

mcp = FastMCP("indian-stock-tools")

# Friendly-name -> NSE ticker map so the LLM/user doesn't need to remember
# Yahoo Finance's suffix convention.
KNOWN_TICKERS = {
    "tcs": "TCS.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfcbank": "HDFCBANK.NS",
    "asian paints": "ASIANPAINT.NS",
    "asianpaint": "ASIANPAINT.NS",
    "itc": "ITC.NS",
    "titan": "TITAN.NS",
}


def _resolve_ticker(name_or_ticker: str) -> str:
    key = name_or_ticker.strip().lower()
    if key in KNOWN_TICKERS:
        return KNOWN_TICKERS[key]
    # Assume caller already passed a valid Yahoo Finance ticker.
    return name_or_ticker.strip().upper()


@mcp.tool()
def get_stock_price(company: str) -> dict:
    """Get the latest stock price and day change for an Indian (NSE-listed) company.

    Args:
        company: Company name (e.g. "TCS", "Asian Paints") or a Yahoo Finance
                 ticker (e.g. "TCS.NS").

    Returns:
        dict with ticker, currency, last_price, previous_close, day_change_pct.
    """
    ticker = _resolve_ticker(company)
    t = yf.Ticker(ticker)
    info = t.fast_info
    last = info.get("last_price")
    prev = info.get("previous_close")
    change_pct = None
    if last is not None and prev:
        change_pct = round((last - prev) / prev * 100, 2)
    return {
        "ticker": ticker,
        "currency": info.get("currency", "INR"),
        "last_price": last,
        "previous_close": prev,
        "day_change_pct": change_pct,
    }


@mcp.tool()
def get_financial_ratios(company: str) -> dict:
    """Get key fundamental ratios for an Indian (NSE-listed) company.

    Args:
        company: Company name (e.g. "TCS", "Asian Paints") or a Yahoo Finance
                 ticker (e.g. "TCS.NS").

    Returns:
        dict with pe_ratio, price_to_book, return_on_equity, debt_to_equity,
        market_cap, dividend_yield, and 52-week high/low.
    """
    ticker = _resolve_ticker(company)
    t = yf.Ticker(ticker)
    info = t.info  # slower, full fundamentals payload

    def pct(x):
        return round(x * 100, 2) if isinstance(x, (int, float)) else None

    return {
        "ticker": ticker,
        "pe_ratio": info.get("trailingPE"),
        "price_to_book": info.get("priceToBook"),
        "return_on_equity_pct": pct(info.get("returnOnEquity")),
        "debt_to_equity": info.get("debtToEquity"),
        "market_cap_inr": info.get("marketCap"),
        "dividend_yield_pct": pct(info.get("dividendYield")),
        "week52_high": info.get("fiftyTwoWeekHigh"),
        "week52_low": info.get("fiftyTwoWeekLow"),
    }


if __name__ == "__main__":
    mcp.run()
