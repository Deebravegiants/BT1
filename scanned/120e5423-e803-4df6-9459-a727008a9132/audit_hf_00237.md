# [H] Unused slippage params

## Summary
Severity: High
Contest weight: 0.1251
Dataset id: 1226
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unused slippage params. function `addLiquidity` in VaderRouter (both V1 and V2) do not use slippage parameters:

uint256, // amountAMin = unused
uint256, // amountBMin = unused

making it susceptible to sandwich attacks / MEV. For a more detailed explanation, see: <https://github.com/code-423n4/2021-09-bvecvx-findings/issues/57>

## Recommendation
Consider paying some attention to the slippage to reduce possible manipulation attacks from mempool snipers.

Slippage checks are impossible in the Thorchain CLP model.

Taking as main over #1 as it is a more general issue, but refer to #1 for a more detailed description and justification for the severity rating.
