# [H] Wrong design of `swap

## Summary
Severity: High
Contest weight: 0.5465
Dataset id: 1236
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current formula to calculate the `amountOut` for a swap is:
```solidity
function calculateSwap(
    uint256 amountIn,
    uint256 reserveIn,
    uint256 reserveOut
) public pure returns (uint256 amountOut) {
    // x * Y * X
    uint256 numerator = amountIn * reserveIn * reserveOut;

    // (x + X) ^ 2
    uint256 denominator = pow(amountIn + reserveIn);

    amountOut = numerator / denominator;
}
```
We believe the design (the formula) is wrong and it will result in unexpected and unfavorable outputs.

Specifically, if the `amountIn` is larger than the `reserveIn`, the `amountOut` starts to decrease.

## Recommendation
No recommendation
