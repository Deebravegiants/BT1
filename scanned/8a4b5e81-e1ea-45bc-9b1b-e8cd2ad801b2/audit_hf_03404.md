# [H] BOU-1 | Tight Stop Loss Abuse

## Summary
Severity: High
Contest weight: 0.1972
Dataset id: 18512
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For stop-losses, the triggerPrice is used to represent the price of the asset instead of just using it as
a trigger for execution. In traditional markets, the stop-loss price is not the guaranteed execution
price especially in times of heavy volatility.
Users can open a long and place a SL ever so slightly below the current price. If they get stopped out
then they will lose out on fees. However, with high leverage, the upside gain is immense with little
risk. Such a high reward will come at the expense of the pool, hurting LPers and the market as a
whole.
Ultimately, this allows sophisticated traders to have a superior strategy than that of traditional stop
loss orders where they are treated like mere triggers – hurting the profitability of LPers.

## Recommendation
Use the latest price (secondaryPrice) when executing a stop loss order rather than giving the user
their exact triggerPrice.
