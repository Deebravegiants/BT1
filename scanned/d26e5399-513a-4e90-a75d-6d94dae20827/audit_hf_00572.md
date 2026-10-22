# [H] H-03 | Wrong Vault Beneﬁts From Funding Fee Claims

## Summary
Severity: High
Contest weight: 0.1112
Dataset id: 2034
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Long tokens can collect both long and short funding fees. Because short funding fees come in the form of USDC, those funding fees will be credited to the USDC vault instead of the vault that actually has the position. Leading to a loss of yield for users who have deposited into the BTC vault.

## Recommendation
When claiming the short funding fees for a long position swap the claimed USDC for the correct long token. This will ensure that the funding fees go to the correct vault. It is also important that this value while pending is also credited to the correct vault.
