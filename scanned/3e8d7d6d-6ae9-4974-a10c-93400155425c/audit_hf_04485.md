# [C] C-05 | Settled Trading Positions Can Be Closed

## Summary
Severity: Critical
Contest weight: 0.1245
Dataset id: 22048
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The modifyTraderPosition function does not check if the given position is already settled. This enables an attack vector to steal funds by closing an already settled position. As the collateral & the owned tokens of the position are not set to 0 during the settlement process.

## Recommendation
Always use the validateNotSettled validation in the modifyTraderPosition function as no trader activity should occur after an epoch end besides settlement. If a trader wishes to close their position, they should use the EpochSettlementModule to do so. Thus the epoch.settled case handling can be removed from the swapTokensExactOut and swapTokensExactIn swap functions as they will no longer be callable after the epoch has been settled.
