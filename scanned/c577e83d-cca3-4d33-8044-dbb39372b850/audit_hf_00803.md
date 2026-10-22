# [M] M-04 | Pausing The PositionManager Disables addToken

## Summary
Severity: Medium
Contest weight: 0.1298
Dataset id: 2539
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The addToken function is paused when the PositionManager is paused. This prevents borrowers from adding new tokens as collateral to their position, which could result in the borrowers not being able to keep their position healthy.
Here is an example of such a scenario:
• A borrower opens a position with a collateral token (for example a BasePool or SuperPool share token) and borrows funds
• Something bad happens in the system and the PositionManager as well as the pool of the collateral token is paused
• The collateral of the borrower losses value
• As the pool is paused the borrower is not able to get more tokens and increase the collateral of the position
• Also as the addToken function is paused the borrower is not able to add a new collateral token to the position
The same could happen with another token that is for any reason not available at the given moment.

## Recommendation
Remove the whenNotPaused modifier from the addToken function.
