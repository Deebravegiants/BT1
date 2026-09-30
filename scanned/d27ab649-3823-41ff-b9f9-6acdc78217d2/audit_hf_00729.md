# [H] H-10 | DebtCorrection Uses Incorrect Price For Funding

## Summary
Severity: High
Contest weight: 0.1512
Dataset id: 2280
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the updateDebtCorrection function the pnl realized from funding is added to offset the funding gains which were realized to the account’s margin. However the funding gains which are transferred to the account’s margin are based upon the oraclePrice, whereas the funding gains accounted for in the debt correction are based upon the new position’s entry price. These funding amounts will disagree due to the price differential and will cause a potentially large divergence between the actual debt of the market and the reported debt over time.

## Recommendation
Use the oraclePrice to compute the settled funding amount in the debt correction.
