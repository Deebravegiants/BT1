# [H] H-01 | minimumCredit Inaccurately Restricts Backing For Shorts

## Summary
Severity: High
Contest weight: 0.1997
Dataset id: 21096
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The minimumCredit function defines an amount which the available credit capacity cannot go below
depending on the size of the market and the current index price. However this calculation perturbs
the amount that ought to be reserved for shorts.
For example:
• A market has 10 index tokens as short open interest.
• The market size is 10.
• The price of the index token doubles.
• The minimum credit is now a ratio based on the 10 tokens of short open interest, now valued at
twice the price.
This inaccurately represents the amount of backing liquidity that ought to be reserved for the market
as shorts can only ever gain up to their cost-basis and when the price of the index token rises, shorts
are in a loss.

## Recommendation
Account for the long and short open interest separately when computing how much backing liquidity
ought to be reserved.
For example, the GMX V2 system reserves liquidity based upon openInterestInTokens * price for
longs and openInterest (position cost) for shorts.
