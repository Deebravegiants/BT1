# [H] H-02 | Incorrect Subtraction Of totalFees

## Summary
Severity: High
Contest weight: 0.2527
Dataset id: 4025
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _getManagerAvailableBalance function calculates the manager's available balance for transferring funds to the vault when depositAssets < totalDebit. It subtracts totalFees (all accrued fees) from the minimum of the manager's balance and allowance.
However, this is illogical because:
• The accrued fees are locked in the vault's balance, not the manager's. The manager's token.balanceOf(manager) does not include these fees.
• Subtracting totalFees underestimates the manager's ability to transfer funds, potentially causing unnecessary reverts with InsufficientManagerFunds.
The manager's available balance should be the full amount it can transfer to the vault, limited only by its balance and allowance. Since fees are held in the vault and claimed separately (claimManagerFees, claimBrktTvlFees), they do not reduce the manager's available balance.
Example:
• Manager balance = 100, allowance = 100, accruedFees = 10 in the vault.
• Current code: available = min(100, 100) - 10 = 90.
• Actual: Manager can transfer up to 100, as the 10 in fees is in the vault.

## Recommendation
Remove the fee subtraction from the _getManagerAvailableBalance function. This accurately reflects the manager's capacity to support the vault.
