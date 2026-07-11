---
name: Red Flags Audit
id: red_flags
description: Scan for common Indian-market red flags — leverage, governance, promoter behavior — using the filing excerpts and live ratios.
needs_rag: true
needs_tools: [get_financial_ratios]
---

You are performing a red-flags audit of {{company}} for a value investor,
using ONLY the retrieved filing excerpts and live financial ratios below.
Check specifically for:

1. **Leverage risk** — is debt/equity elevated or rising? Any mention of
   refinancing risk in the excerpts?
2. **Governance/related-party concerns** — anything in the excerpts about
   promoter holding, related-party transactions, auditor changes, or
   governance structure worth flagging?
3. **Earnings quality concerns** — anything suggesting aggressive
   accounting, one-off gains propping up results, or segment concentration
   risk?
4. **Regulatory/sector-specific risk** — sector-specific risks mentioned
   in the excerpts (e.g. taxation, competition, commodity exposure).

Summarize with a short **risk scorecard** (Low/Medium/High for each
category above) and a one-paragraph overall take. If the retrieved
excerpts don't contain enough information for a category, say so rather
than inventing a rating.
