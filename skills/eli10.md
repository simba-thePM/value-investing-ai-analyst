---
name: Explain Like I'm 10
id: eli10
description: Explain the company and the investment case in very simple, jargon-free language.
needs_rag: true
needs_tools: [get_stock_price]
---

Explain {{company}} to someone with zero finance background, using the
retrieved filing excerpts below for factual grounding. Use simple analogies
a 10-year-old could follow:

1. What does this company actually *do*, in one or two plain sentences?
2. Why might it be a good or risky business, using a simple analogy
   (e.g. "it's like the only toy shop in town that everyone trusts")?
3. What is one number from the live data below (like the stock price) and
   what does it mean in plain terms?

Avoid jargon (no "moat", "ROE", "P/E" without explaining them in plain
words first). Keep it under 150 words.
