# [H] MJR-2 Lack of claim validation

## Summary
Severity: High
Contest weight: 0.0401
Dataset id: 6948
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At lines: ClaimManagement.sol#L112 ClaimManagement.sol#L145 ClaimManagement.sol#L176 the claim is taken by coverPool, nonce, _index, however caller may send incorrect indexes to the method. At the line ClaimManagement.sol#L114 even the flow with invalid claim will pass the require condition and go to claim.state = ClaimState.Validated; resetCoverPoolClaimFee(coverPool); this is unexpected behavior and potentially can lead to the contract misfunctioning.

## Recommendation
Add require(index < coverPoolClaims[coverPool][_nonce].length, "bad indexes");
