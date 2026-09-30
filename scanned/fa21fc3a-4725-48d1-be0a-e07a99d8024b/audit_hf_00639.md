# [M] M-01 | Arbitrary NFTLP Code Can Be Used

## Summary
Severity: Medium
Contest weight: 0.0510
Dataset id: 2156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ImpermaxFactory contract allows for the creation of lending pools with a completely arbitrary NFTLP address. Consequently, a malicious user may create a lending pool with a malicious tokenized position which could lead to loss of user data and assets.

## Recommendation
Validate that the NFTLP's passed into the ImpermaxFactory functions have been deployed through the respective tokenized position factory contracts.
