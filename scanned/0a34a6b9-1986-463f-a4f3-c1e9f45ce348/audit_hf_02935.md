# [C] ClearingHouseLiq::_assertLiquidationAmount() may increase basis points due to negative quoteBalance.amount + insurance

## Summary
Severity: Critical
Contest weight: 0.5464
Dataset id: 16285
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If the position is a spread, it may be liquidated as one up to the minimum absolute value of the spot and perp positions. If the spot is short, the liquidatee + insurance need to have enough quote to buy back the spot position. This check is performed in ClearingHouseLiq::_assertLiquidationAmount():
```solidity
basisAmount = MathHelper.max(
    -((quoteBalance.amount + insurance).div(liquidationPrice) + 1),
    basisAmount
);
```
Note that quoteBalance.amount + insurance may be negative, which would mean that abs(basisAmount) could be increased, leading to incorrect states.

## Recommendation
Add if (quoteBalance.amount + insurance <= 0) basisAmount = 0 or similar.
