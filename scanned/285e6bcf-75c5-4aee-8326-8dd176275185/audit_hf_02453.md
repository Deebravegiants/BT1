# [M] Improved executeSwaps() Logic in Symphony

## Summary
Severity: Medium
Contest weight: 0.4346
Dataset id: 13155
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Symphony, there is a core function named executeSwaps() that is designed to execute a series of swap operations based on the provided swap parameters. Our analysis shows its logic may be improved, including enhanced user input validation. In the following, we show the code snippet from the related executeSwaps() routine. When the routine is called with accompany non-zero msg.value, we need to ensure the local variable totalAmountIn matches msg.value, instead of current totalAmountIn = msg.value (line 447). Also, for another variable pathFinalTokenAddress that represents the output token address, we only need to assign it at the first iteration (when i=0) and validate its consistency for remaining iterations (when i!=0).

```solidity
function executeSwaps(
    Params.SwapParam[][] memory swapParams,
    uint minTotalAmountOut,
    bool conveth,
    FeeParams memory feeData
) external payable nonReentrant returns (uint) {
    address tokenG = swapParams[0][0].tokenIn;
    IERC20 token = IERC20(tokenG);
    uint256 totalAmountIn = 0;
    for (uint i = 0; i < swapParams.length; i++) {
        totalAmountIn = swapParams[i][0].amountIn;
        if (msg.value > 0) {
            weth.deposit{value: msg.value}();
            totalAmountIn = msg.value;
        } else {
            if (!token.transferFrom(msg.sender, address(this), totalAmountIn)) revert TransferFromFailedError(msg.sender, address(this), totalAmountIn);
        }
    }
}
```

## Recommendation
Improve the above routine to ensure (1) msg.value, if positive, is consistent with the local variable totalAmountIn and (2) the output token is always consistent in different iterations.
