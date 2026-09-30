# [H] H-05 | DOS Of updateLPAndStrategyFund

## Summary
Severity: High
Contest weight: 0.2966
Dataset id: 2216
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LP_WITHDRAW and SP_WITHDRAW inside ProtocolVaultLedger.handleOpFromVault() should only be allowed if the user has enough withdrawable shares. This is handled by _checkWithdraw() - it ensures the amount to be withdrawn added to the current frozen amount doesn't surpass the share balance of the account. After that, the amount to be withdrawn is added towards frozenShares so checkWithdrawal will continue to work properly for further withdrawal requests. The withdrawal request will be handled by _handleLpWithdraw() and the amount to be withdrawn will be subtracted by the user's pendingShares and frozenShares. After some time, settleAccounts() will update the user's actual shares by setting them to pendingShares. This creates a window between _handleLpWithdraw() and settleAccounts() where frozenShares is decreased, but account.shares is not updated. Any withdrawal request in that window will successfully performed if it doesn't exceed the user's shares because _checkWithdraw() won't stop it. This will result in an increase in frozenShares, potentially doubling the current value. The withdrawal request inside this window will be processed inside _handleLpWithdraw() for the next period. The amount to be withdrawn will be subtracted from pendingShares again, however this time pendingShares will not cover it causing a revert and DOS of the updateLPAndStrategyFund function.

## Recommendation
One possible solution may be to disallow withdrawal requests in that window.
