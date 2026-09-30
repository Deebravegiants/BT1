# [M] M-12 | Fees Missing In Required Collateral Calc

## Summary
Severity: Medium
Contest weight: 0.0597
Dataset id: 22068
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the required collateral for a trade position the uniswap fee to close the position is not included. Therefore the trader might not be able to close the position with the deposited collateral as the fee was not accounted for. The same could happen for liquidity positions which are converted to trade positions when they are closed.

## Recommendation
Include the uniswap fees in the required collateral calculations.
