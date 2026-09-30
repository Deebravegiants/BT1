# [M] Nonfunctional Slippage Control

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 11975
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The DYP Earn Vault has a built-in integration with Compound. With the integration, users-deposited
funds are forwarded to Compound for respective cTokens held by the DYP Earn Vault. Users may withdraw
their cTokens back to their deposit and interest from Compound. Note the withdrawal operation has a
0.3% withdrawal fee in respective token: 25% of withdrawal fee is used to buy back the protocol token
from Uniswap and 75% distributed pro-rata among active vault users. The protocol setup assumes
Compound and Uniswap have the appropriate amount of liquidity available for the whole setup to work
properly.
In the following, we examine the Vault::handleFee() routine that is designed to process the
withdrawal fee. After proper calculation of withdrawal fee, this routine converts the fee from the
deposited token to the platform token via swapExactTokensForTokens in Uniswap (line 1269). It comes
to our attention that the routine attempts to limit possible slippage by computing minimum amount
after conversion in amountOutMin (line 1266).
function handleFee(uint feeAmount) private {
    uint buyBackFeeAmount = feeAmount.mul(FEE_PERCENT_TO_BUYBACK_X_100).div(ONE_HUNDRED_X_100);
    uint remainingFeeAmount = feeAmount.sub(buyBackFeeAmount);
    // handle distribution
    distributeTokenDivs(remainingFeeAmount);
    // handle buyback
    // --- swap token to platform token here! ----
    IERC20(TRUSTED_DEPOSIT_TOKEN_ADDRESS).safeApprove(address(uniswapRouterV2), 0);
    IERC20(TRUSTED_DEPOSIT_TOKEN_ADDRESS).safeApprove(address(uniswapRouterV2), feeAmount);
    uint oldPlatformTokenBalance = IERC20(TRUSTED_PLATFORM_TOKEN_ADDRESS).balanceOf(address(this));
    address[] memory path = new address[](3);
    path[0] = TRUSTED_DEPOSIT_TOKEN_ADDRESS;
    path[1] = uniswapRouterV2.WETH();
    path[2] = TRUSTED_PLATFORM_TOKEN_ADDRESS;
    uint estimatedAmountOut = uniswapRouterV2.getAmountsOut(buyBackFeeAmount, path)[2];
    uint amountOutMin = estimatedAmountOut.mul(ONE_HUNDRED_X_100.sub(SLIPPAGE_TOLERANCE_X_100)).div(ONE_HUNDRED_X_100);
    uniswapRouterV2.swapExactTokensForTokens(
        buyBackFeeAmount,
        amountOutMin,
        path,
        address(this),
        block.timestamp
    );
    uint newPlatformTokenBalance = IERC20(TRUSTED_PLATFORM_TOKEN_ADDRESS).balanceOf(address(this));
    uint platformTokensReceived = newPlatformTokenBalance.sub(oldPlatformTokenBalance);
    IERC20(TRUSTED_PLATFORM_TOKEN_ADDRESS).safeTransfer(BURN_ADDRESS, platformTokensReceived);
    // ---- end swap token to platform tokens
}
```
We point out that the computation of amountOutMin is performed via getAmountsOut() in the same
Uniswap, which means the minimum amount after conversion is always satisfied. In other words,
current slippage control is not functional. A proper slippage control may require manual input or
a separate pricing oracle to compare and restrict potential deviation from Uniswap. Note that both
Vault and VaultWETH contracts share the same issue.

## Recommendation
Properly apply slippage control to avoid unnecessary conversion loss from potential price manipulation in Uniswap.
