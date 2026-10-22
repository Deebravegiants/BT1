# [M] Interface inconsistencies

## Summary
Severity: Medium
Contest weight: 0.1236
Dataset id: 5024
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The following inconsistencies have been found around interfaces:
• ISet's definition of the claim() function returns a uint256 while the actual implementation returns uint128
• ISet's definition of the redemptions() function has different returns values than the actual Redemption struct: There's no delay variable and the shares variable has a different data type.
• IPToken defines an external function called inactiveTransitionTime() which is not implemented in the actual PToken contract.
• The interfaces folder contains the interfaces of IDripDecayModel and ICostModel despite the fact that cozy-models-v2 is a dependency of the repository and could make use of the original interfaces without duplication.

## Recommendation
Ensure that the interfaces are actually implemented in an accurate manner. When possible, have the implementation inherit the interface to have the compiler enforce this. Also avoid duplicating interfaces when possible as this creates the chance that not all interfaces are properly adjusted on changes and inconsistencies are created.
