# [M] `dailyDebtIncreaseLimitLeft` is not updated in `liquidate`

## Summary
Severity: Medium
Contest weight: 0.1284
Dataset id: 20990
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
On days with a significant number of liquidated positions, particularly when the asset quantity is substantial, there will be an excess of assets available in the vault that cannot be borrowed; thereby, causing a drastic decrease in the utilization rate.

This also contradicts what was stated in the `repay()` function, which asserts that repaid amounts should be borrowed again. Liquidation is also a form of repayment:
    
    // when amounts are repayed - they may be borrowed again
            dailyDebtIncreaseLimitLeft += assets;

## Proof of Concept
`dailyDebtIncreaseLimitLeft` was not incremented in `liquidate()`, see [here](https://github.com/code-423n4/2024-03-revert-lend/blob/435b054f9ad2404173f36f0f74a5096c894b12b7/src/V3Vault.sol#L685-L757).

## Recommendation
Include `dailyDebtIncreaseLimitLeft` increment in `liquidate()`.
    
    dailyDebtIncreaseLimitLeft += state.liquidatorCost;
