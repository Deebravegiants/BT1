# [M] DIEM-11 | Rounded Funds Stuck in Diem Contract

## Summary
Severity: Medium
Contest weight: 0.0663
Dataset id: 124
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function convertFrom18AndRoundDown rounds down by subtracting a value determined by return x - (x % assetDecimals). This deducted amount is then left in the IVXDiem contract. While the amount being locked in the contract is not large, there is no way to access these funds, and each time convertFrom18AndRoundDown is called in the IVXDiem contract, funds will be locked.

## Recommendation
Excess funds that remain after conversions should be claimable by the owner of the portfolio or by the protocol.
