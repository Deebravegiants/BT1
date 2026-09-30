# [M] ERTR-1 | Missing Validation

## Summary
Severity: Medium
Contest weight: 0.0934
Dataset id: 16900
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When creating a deposit, there is no validation that the longToken or the shortToken are valid for the supplied market. If WBTC is accidentally used as the long token in an ETH/USDC market, the user would lose their WBTC in the depositStore. Furthermore, there is no validation that either the long token amount or short token amount is non-zero. This check should be added to prevent the keeper from executing trivial deposits. Additionally, when creating an order, there is no validation that the initial collateral token is valid for the provided market, which can lead to invalid orders stored in the orderStore.

## Recommendation
Implement the above mentioned validations.
