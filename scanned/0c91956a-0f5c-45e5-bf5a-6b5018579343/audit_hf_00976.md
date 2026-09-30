# [H] Liquidation of unhealthy accounts can be prevented at low cost

## Summary
Severity: High
Contest weight: 0.7224
Dataset id: 3040
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Liquidation of unhealthy accounts can be halted even though they should still be liquidat-
able.

Liquidator.bid() is the entry point for bidding on liquidation auctions. Since this
finding is primarily concerned with halting the liquidation, the other part of the function is omitted
for simplicity.
It's important to acknowledge that setting endAuction_ = true would call Liquidator._endAuction() if Liquidator._settleAuction() returns true.

```solidity

## Recommendation
```solidity
