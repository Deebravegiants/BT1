# [M] M-03 | Sanctions Can Be Avoided

## Summary
Severity: Medium
Contest weight: 0.0472
Dataset id: 2003
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently checkClaims only validates sanctions against the claimer: if (isSanctioned(claimer)) return (claimNonce, false); However, there's is no validation that the actual owner of the NFT is not sanctioned in the case that the claimer is a delegate.

## Recommendation
Consider adding sanctions validation on the NFT owner, otherwise clearly document this behavior.
