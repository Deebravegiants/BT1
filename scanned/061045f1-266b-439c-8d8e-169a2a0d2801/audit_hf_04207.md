# [H] H-05 | minimumCredit Reserves Not Validated Upon Position Increase

## Summary
Severity: High
Contest weight: 0.1819
Dataset id: 21100
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Traders are allowed to open and settle orders even when the existing market positions cannot be
adequately supported by the liquidity backing the BFP market. Even if the existing minimumCredit is
too large for the backing creditCapacity, traders can continue to increase the market size and
therefore increase the uncovered gap between the minimumCredit and the lacking creditCapacity.
As a result the BFP market can easily become insolvent in the event that traders continue to open
positions without consideration for the backing liquidity. This leads to a market state where sUSD
collateral withdrawals are DoS'd as well as any settlement for positions in a profit.

## Recommendation
Validate that orders that would create new positions or increase existing positions do not invalidate
the minimumCredit validation for the market.
