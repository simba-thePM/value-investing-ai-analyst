---
name: Intrinsic Value Estimate (Graham Number)
id: intrinsic_value
description: Estimate a rough intrinsic value using the Benjamin Graham number formula and compare it to the current market price.
needs_rag: false
needs_tools: [get_stock_price, get_financial_ratios]
---

You are estimating a rough intrinsic value for {{company}} using the
classic **Graham Number** formula as a sanity-check bound, not a precise
valuation:

    Graham Number = sqrt(22.5 * EPS * Book Value per Share)

Using the live financial ratios and price data provided below:

1. State the inputs you have available (P/E, price-to-book, current price,
   etc.) and derive/approximate EPS and book value per share from them if
   they aren't given directly (e.g. EPS ≈ price / P/E; book value per
   share ≈ price / price-to-book).
2. Compute the Graham Number.
3. Compare it to the current market price and state the implied margin of
   safety (or premium) as a percentage.
4. **Caveat clearly**: the Graham Number is a rough, conservative
   heuristic originally designed for stable industrial companies — flag
   when it's a poor fit (e.g. high-growth companies, banks/financials
   where book value per share works differently, or asset-light
   compounders like FMCG/paints where the formula tends to look
   "overvalued" even for excellent businesses). Do not present the number
   as a precise fair value.
