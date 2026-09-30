# [M] BalancedVault sophisticated active users may deposit or withdraw at the last minute before the new oracle version to escape loss or snatch profits

## Summary
Severity: Medium
Contest weight: 0.1486
Dataset id: 19697
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PNL of a position is settled every time a new price is posted.
The BalancedVault is designed to be split 50/50 between long and short, but the actual effective position sizes can be different. Therefore, every new price comes with a profit or loss.
When there is a significant amount of profit added to the holdings by the update, a sophisticated user can monitor the price update very closely, maybe even frontrun the price update transaction and deposit to the BalancedVault, and exit right after the update.
By doing so, the user would be able to take a portion of the profit.
Vice versa, if there is an upcoming price movement that causes a loss to the BalancedVault, the user would be able to escape the loss.
The root cause for this issue is that the strategy is asynchronous, but the vault is synchronous.
The pending PNL of the asynchronous strategy is predictable, which creates an opportunity for active users to use this knowledge against inactive users.
We are not including the Vault in this release as it needs a rewrite mainly due to issue M2.

## Recommendation
No recommendation available
