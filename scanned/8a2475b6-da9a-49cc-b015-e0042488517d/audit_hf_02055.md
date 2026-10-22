# [M] Improved Logic of ConveyorV2Router01::getAmountIn()

## Summary
Severity: Medium
Contest weight: 0.3827
Dataset id: 11685
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In ConveyorV2Router01, the getAmountIn() routine is defined to calculate the required input amount of an asset when given an output amount of the other asset. During the analysis of this function, we notice that the calculation of amountIn is routed to ConveyorV2Library.getAmountOut()(line 195) which is not correct.
```solidity
function getAmountIn(
    uint256 amountOut,
    uint256 reserveIn,
    uint256 reserveOut
) public pure override returns (uint256 amountIn) {
    return ConveyorV2Library.getAmountOut(amountOut, reserveIn, reserveOut);
}
```

## Recommendation
Correct the above getAmountIn() routine by calling the right helper function, i.e., ConveyorV2Library.getAmountIn().
