# [C] MKTU-3 | Unclaimable Collateral

## Summary
Severity: Critical
Contest weight: 0.1394
Dataset id: 18156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When users attempt to claim their collateral, the adjustedClaimableAmount is asserted to be < the claimedAmount, otherwise the tx reverts. However if a user has not claimed any of their collateral the claimed amount will be 0 and therefore the adjustedClaimableAmount cannot be strictly less than the claimedAmount. Therefore users are unable to claim their collateral.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/MKTU_3.ts

## Recommendation
Modify the if statement to revert in the case where adjustedClaimableAmount < claimedAmount.
