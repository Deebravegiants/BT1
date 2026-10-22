# [M] M-1 No Slippage Protection

## Summary
Severity: Medium
Contest weight: 0.3680
Dataset id: 14125
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
• ExternalRequestsManagerBetaV1.sol#L234
• ExternalRequestsManagerBetaV1.sol#L175
```
The amounts of tokens to mint and transfer in completeMint() and completeBurn() in the ExternalRequestsManagerBetaV1 are not related to any on-chain oracle and are prone to slippage: users may receive less tokens than they expected.

## Recommendation
We recommend adding the minAmountOut and deadline parameters to the workflow.
