# [M] M-04 | Positions Are Lost When lendingPair Is Changed

## Summary
Severity: Medium
Contest weight: 0.1184
Dataset id: 22175
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a new position is [initialized](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/lvf/LeverageManager.sol#L271), its lendingPair is set to the lending pair for the pod configured by the owner of the contract. However, adding and removing leverage always use the most recent lendingPair for the pod of the position instead of the pair at the time of it creation. This results in positions being lost when the owner changes the pair by calling [setLendingPair](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/lvf/LeverageManagerAccessControl.sol#L14-L19) because _removeLeverage will make the custodian remove collateral from the new pair where it doesn't have any.

## Recommendation
Use positionProps.lendingPair instead of the latest lending pair when adding/removing leverage.
