# [M] M-01 | Insufficient Gas Estimated

## Summary
Severity: Medium
Contest weight: 0.0869
Dataset id: 2001
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the requestClaim function the checks.numNFTs and checks.numCollectors values are used to compute the gas that should be provided to the lzReceive function on the L2. However the checks.numCollectors value only includes the number of collector claims that need to be veriﬁed on the L1, which does not include claims where the collector is the claimer. These claims will still have to be iterated over in the lzReceive function though, and thus should be accounted for in the gas estimation.

## Recommendation
Consider basing the gas estimation in the _lzOptions function on the conﬁgs.length instead as this more closely represents the iterations that must be made in the lzReceive function.
