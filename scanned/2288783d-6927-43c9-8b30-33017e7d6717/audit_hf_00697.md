# [C] C-02 | mergeAccount Abused For Proﬁt

## Summary
Severity: Critical
Contest weight: 0.1516
Dataset id: 2248
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling mergeAccount() the check to verify the size of the fromPositon and toPosition calls sameSide(). sameSide() will always return true if either size is 0. This will then set entry price to the toPosition to 0, since the fromPositon was deleted in settleOrder(). Now the toPosition instantly has a positive PnL if the position is a long.

## Proof of Concept
https://github.com/GuardianAudits/snx-bfp-1/blob/POC_BFP/markets/bfp-market/test/integration/modules/guardian/pocs/mergeEmptyPosition.test.ts

## Recommendation
Revert if the fromPositon has 0 size in mergeAccount().
