# [M] Oracle fees should be payed upfront to protect the protocol from failed performeUpkeep() calls

## Summary
Severity: Medium
Contest weight: 0.0859
Dataset id: 11137
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the moment oracle fees are payed after the trades have been finalized, either in registerTrade(), openTradeMarketCallback() or closeTradeMarketCallback(). There are some edge cases in which the trade does not get finalized, but the automation/upkeep is still performed, so the protocol incurs these losses. For example, if there is not a trade in openTradeMarketCallback(), fees will not be charged (this may happen if the user cancels the pending market open order after the timeout, but chainlink triggers the upkeep after closing).

## Recommendation
Make the user pay oracle fees when they open the trades.
