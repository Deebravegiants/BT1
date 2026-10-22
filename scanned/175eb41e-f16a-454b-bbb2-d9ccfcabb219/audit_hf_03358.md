# [M] GLOBAL-8 | Lack of Slippage Protection When Swapping

## Summary
Severity: Medium
Contest weight: 0.0685
Dataset id: 18212
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The following places lack slippage protection and may lead to loss of assets for a user:
1) DecreasePositionCollateralUtils.sol Line 392 and Line 434 use 0 as the minOutputAmount which may unexpectedly reduce the proﬁt for a trader.
2) ExecuteDepositUtils.sol Line 432 which may reduce the amount of market tokens the user obtains although risk may be limited by specifying minMarketTokens.

## Recommendation
Consider adding the functionality to specify the minimum output amounts and/or further document this behavior.
