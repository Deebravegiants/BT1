# [M] M-4 The lack of support of fee on transfer tokens in DefaultTimeLock

## Summary
Severity: Medium
Contest weight: 0.0759
Dataset id: 7328
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The agreement creation precedes the token transfer. If a fee on transfer tokens is used, then the amount of tokens transferred may be reduced (due to transfer fees) and become less than the amount specified in the agreement for claiming. This issue is labeled as medium since the resulted inconsistency can block the claim function until the balance of the timelock surpasses the quantity of tokens noted in the agreement.

## Recommendation
We recommend reworking the TimeLock architecture to pull assets by transferFrom in the createAgreement. Additionally, it will help addressing previous finding.
