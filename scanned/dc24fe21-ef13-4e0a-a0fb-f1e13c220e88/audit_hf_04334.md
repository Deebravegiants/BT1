# [M] M-10 | Virtual Liquidity Lower Than Expected

## Summary
Severity: Medium
Contest weight: 0.3822
Dataset id: 21490
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the slide operation is triggered, the virtualLiquidityF is calculated based on the total collateral and the reserves removed from the FLOOR, using the lower and upper sqrtPrice of the entire range. In case the slide is executed when the active tick is in the FLOOR range, virtualLiquidityF will still use the upper sqrtPrice of the range, instead of the current price. This issue will cause the virtualLiquidityF to appear smaller than expected.

## Recommendation
Consider using the correct limit price in the formula:
```solidity
(uint160 sqrtPriceA,,,,,,) = BPOOL.pool().slot0();
uint256 virtualLiquidityF = uint256(
    LiquidityAmounts.getLiquidityForAmount1(
        floor.sqrtPriceL, sqrtPriceA < floor.sqrtPriceU ? sqrtPriceA : floor.sqrtPriceU,
        CREDT.totalCreditIssued() + reservesF
    )
);
```
