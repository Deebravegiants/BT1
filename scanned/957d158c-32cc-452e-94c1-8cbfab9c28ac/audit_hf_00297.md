# [H] `TimeswapConvenience.sol#borrowGivenDebt`

## Summary
Severity: High
Contest weight: 0.1119
Dataset id: 1485
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This issue is similar to the two previous issues related to `state.y` manipulation. Unlike the other two issues, this function is not on `TimeswapPair.sol` but on `TimeswapConvenience.sol`, therefore this can not be solved by adding `onlyConvenience` modifier.

Actually, we believe that it does not make sense for the caller to specify the interest they want to pay, we recommend removing this function.

## Recommendation
No recommendation
