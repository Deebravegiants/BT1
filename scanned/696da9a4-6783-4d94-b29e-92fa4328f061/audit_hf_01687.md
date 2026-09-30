# [M] M-2 Exchange rate vulnerability

## Summary
Severity: Medium
Contest weight: 0.0693
Dataset id: 9230
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An exchange rate bug for new pools and empty pools (without borrowers and suppliers) for CToken contracts without the 'internalCash' variable.
Flow:
1. Create cToken
2. Mint cToken by user1 (1,000,000)
3. Redeem cToken by user1 (999,999.999999)
4. Transfer underlying (1,000,000) from user1 to market
5. Mint cToken by user2 (1,000,000)
6. Redeem cToken by user1 (user1 receive extra tokens)

## Recommendation
We recommend checking the exchange rate before the ﬁrst mint or using the 'internalCash' value for all CToken contracts.
