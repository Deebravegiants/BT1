# [H] MKTU-2 | Unclaimable Funding Fees

## Summary
Severity: High
Contest weight: 0.1344
Dataset id: 18510
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getExpectedMinTokenBalance function, the collateralForLongs and collateralForShorts is
included in the resulting expectedMinBalance.
Therefore users who are paid out funding fees will be unable to claim them until the users who are
paying the funding fees update their position. There is no requirement for users to frequently update
their position and therefore funding fees can go a long time without being claimable for users.

## Recommendation
Adjust getExpectedMinTokenBalance such that funding fees that will be paid from user’s collateral
can be immediately claimed without affecting the validation.
