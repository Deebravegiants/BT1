# [H] H-08 | Reentrancy In SuperPool

## Summary
Severity: High
Contest weight: 0.2531
Dataset id: 2551
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The last three actions in the withdrawal flow of the SuperPool are:
• Burning the share tokens
• Transferring the funds to the user
• Reducing the lastTotalAssets value
Therefore if the attacker reenters on receiving the tokens the total amount of shares is already reduced, but the total amount of assets is not.
The first action in withdraw/deposit is accruing interest calculated based on the saved lastTotalAssets value and the current total amount. Therefore the given difference on reentering (as lastTotalAssets is not reduced yet) is seen as interest and the owner of the pool receives fees on this interest.
This enables the following attack path:
• SuperPool owner deposits tokens into the own pool
• SuperPool owner withdraws the tokens and reenters on receiving them over and over again
• Every time the difference is seen as interest and the owner receives fees
• Owner withdraws the gained fees
• The owner repeats this process over and over again till the SuperPool is drained completely

## Recommendation
• safeTransfer should be the last action in this flow.
• Use a reentrancy guard on critical functions.
