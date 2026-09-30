# [H] H-03 | Rebalance Extractable Value

## Summary
Severity: High
Contest weight: 0.2536
Dataset id: 2252
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _submitLeverageUpdate function the acceptablePrice value is determined by applying a standard slippage amount to the result of the ﬁllPrice. However the result of the ﬁllPrice function itself can be manipulated such that it returns a higher ﬁllPrice and thus allows for signiﬁcant extractable value by sandwiching the TLX vault’s order. Consider the following scenario:
• A malicious actor observes that a signiﬁcant amount of PnL has built up for the TLX vault and that a rebalance will be triggered by even a small deposit.
• The malicious actor creates a large long order to push the skew of the market higher.
• The malicious actor triggers a small deposit with the mintFor function, triggering a rebalance.
• The rebalance order is assigned a high acceptablePrice which can be signiﬁcantly more than the fair market value of the index asset due to the inﬂated price impact.
• The malicious actor subsequently closes their position directly after the rebalance order is executed, receiving positive impact at the expense of the leveraged token vault holders.

## Recommendation
There is no trivial ﬁx. One potential approach is to reduce the single large rebalance into multiple partial rebalances, minimizing the window for exploit.
