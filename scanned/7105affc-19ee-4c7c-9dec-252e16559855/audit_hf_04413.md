# [M] M-08 | GLV Read-only Reentrancy Risk

## Summary
Severity: Medium
Contest weight: 0.1352
Dataset id: 21889
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the executeGlvWithdrawal function the withdrawal is performed with _processMarketWithdrawal before burning the glvWithdrawal.glvTokenAmount() from the glvVault. As a result any withdrawals which use shouldUnwrapNative token as true and receive weth will have the opportunity to exploit any systems which attempt to read the value of a GLV. This is because during this transfer of native tokens to the receiver address the GLV supply has not yet been reduced, but the amount of GM tokens in GLV has been reduced. The receiver then gains control over the transaction execution if it is a contract with a receive function. For example, any protocols attempting to use GLV as collateral can errantly count this collateral as being insufficient and allow incorrect liquidations since the GLV price is incorrectly reduced during this external transfer of native tokens.

## Recommendation
Burn the GLV tokens before executing the withdrawal with the ExecuteWithdrawalUtils.executeWithdrawal function, but after the marketTokenAmount is computed with the _getMarketTokenAmount function.
