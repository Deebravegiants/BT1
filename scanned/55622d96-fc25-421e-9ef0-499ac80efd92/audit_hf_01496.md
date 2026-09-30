# [H] H-12 Inconsistent shares upgrade

## Summary
Severity: High
Contest weight: 0.0930
Dataset id: 7942
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After shares update in the NFT contract FantiumNFTV3.sol#L638-L640
tournamentDistributionAmount and otherDistributionAmount should be updated for all
distributions for the speciﬁc collection, otherwise, there will be inconsistency in the calculations of the
amount for the claim.

## Recommendation
We recommend saving the share value in the distribution event and using it in the calculations of the claim
amount.
