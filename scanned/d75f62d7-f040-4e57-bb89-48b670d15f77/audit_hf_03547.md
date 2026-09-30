# [M] GLPM-6 | Lists With Different Lengths

## Summary
Severity: Medium
Contest weight: 0.0870
Dataset id: 19349
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The externalCallTargets and externalCallDataList are used to call an external protocol with user-passed data. However, externalCallDataList may have a different length than externalCallTargets, potentially causing an out-of-bounds error or the incorrect data being used for a particular target. Similarly, refundTokens and refundReceivers may be different lengths, potentially causing an out-of-bounds error or funds being sent to an unintended receiver.

## Recommendation
Add validation such that externalCallTargets and externalCallDataList are the same length and that refundTokens and refundReceivers are the same length: require(externalCallTargets.length == externalCallDataList.length) require(refundTokens.length == refundReceivers.length)
