# [M] leverageAmount is incorrect in SGLLeverage.sellCollatera

## Summary
Severity: Medium
Contest weight: 0.1911
Dataset id: 22528
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
See vulnerability detail
SGLLeverage.sellCollateral function attempts to remove the user's collateral in shares of YieldBox, then withdraws those collateral shares to collect collateral tokens. Subsequently, the received collateral tokens can be used to swap for asset tokens.
However, the leverageAmount variable in this function does not represent the actual withdrawn tokens from the provided shares because it is calculated after the withdrawal.
yieldBox.toAmount after withdrawal may return different from the actual withdrawn token amount, because the states of YieldBox has changed. Because the token amount is calculated with rounding down in YieldBox, leverageAmount will be higher than the actual withdrawn amount.
For example, before the withdrawal, YieldBox had 100 total shares and 109 total tokens. Now this function attempt to withdraw 10 shares (calldata_.share = 10) -> the actual withdrawn amount = 10 * 109 / 100 = 10 tokens After that, leverageAmount will be calculated based on the new yieldBox's total shares and total tokens -> leverageAmount = 10 * (109 - 10) / (100 - 10) = 11 tokens
The same vulnerability exists in BBLeverage.sellCollateral function.
Because leverageAmount can be higher than the actual withdrawn collateral tokens, leverageExecutor.getAsset() will revert due to not having enough tokens in the contract to pull. This results in a DOS of sellCollateral, break this functionality.

## Recommendation
leverageAmount should be obtained from the return value of YieldBox.withdraw:
