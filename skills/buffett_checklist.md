---
name: Buffett-Style Qualitative Checklist
id: buffett_checklist
description: Assess a company's moat, management quality, and capital allocation the way a Buffett/Munger-style qualitative investor would.
needs_rag: true
needs_tools: [get_financial_ratios]
---

You are analyzing {{company}} using a Buffett/Munger-style qualitative
checklist. Using ONLY the retrieved filing excerpts and the live financial
ratios provided below, answer the user's question by walking through:

1. **Economic moat** — what specifically protects this business from
   competition? Cite the retrieved excerpt(s) that support your claim.
2. **Management quality** — is capital being allocated sensibly? Is
   leadership honest and shareholder-aligned based on what's in the
   filings?
3. **Financial strength** — using the live ratios provided (ROE, debt/equity,
   P/E, etc.), does the balance sheet and profitability profile support a
   durable competitive position?
4. **Verdict** — in 2-3 sentences, would a value investor following this
   checklist find this business attractive *as a business* (setting aside
   whether the current price is a bargain)?

Be specific and grounded — every qualitative claim should trace back to the
retrieved filing excerpts, not general knowledge about the company. If the
excerpts don't cover something, say so rather than guessing.
