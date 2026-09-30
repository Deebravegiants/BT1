# [C] C-2 Possible overﬂow

## Summary
Severity: Critical
Contest weight: 0.0925
Dataset id: 10271
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
signerCount is a uint8 variable that can have a maximum value of 255. In there are 256 signers or more, it will overﬂow, causing the condition to function incorrectly signatureCondition.sol#L52. Borg owners will be able to pass the condition when only 1 or 2 signers have approved it.

## Recommendation
We recommend removing the signerCount variable and using _signers.length to initialize numSigners.
