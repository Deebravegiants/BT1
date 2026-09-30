# [M] Possible Front-Running For Reduced Return

## Summary
Severity: Medium
Contest weight: 0.1735
Dataset id: 12640
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the OpenSwap contract, we notice that the swap operation respects the minAmountOut threshold that specifies the expected minimal token amount out of this trade of selling AmountIn. We'd like to point out that such trading provides a certain protection against price slippage but may not be sufficient against sophisticated front-running attacks that could just meet the minAmountOut requirement while still lead to a smaller return for trading users.
We emphasize that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or implementing a TWAP or time-weighted average price reference (similar in Perpetual Protocol). Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search efforts for an effective defense.

## Recommendation
Develop effective mitigation to the above front-running attack to better protect the interests of trading users.
