# [H] H-03 | getLiquidityForReserve DoS

## Summary
Severity: High
Contest weight: 0.5470
Dataset id: 21456
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getLiquidityForReserves function there is no validation that the lower price and upper price provided to the getLiquidityForAmount1 function are not equal. This is possible either with an anchor range that has no width or when the active price is exactly that of the lower tick price for a range.
This behavior results in a DoS of several key functionalities of the system when these edge cases are hit.

## Recommendation
Implement the following validation such that the upperPrice can never be less than or equal to the lower price:
```solidity
function getLiquidityForReserves(
uint160 _sqrtPriceL,
uint160 _sqrtPriceU,
uint256 *reserves
) public view returns (uint128 liquidity*) {
(uint160 sqrtPriceA,,,,,,) = pool.slot0();
uint160 upperPrice = min(_sqrtPriceU, sqrtPriceA);
if (upperPrice <= _sqrtPriceL) { return 0; }
liquidity_ = LiquidityAmounts.getLiquidityForAmount1(
_sqrtPriceL,
upperPrice,
_reserves
);
}
```
