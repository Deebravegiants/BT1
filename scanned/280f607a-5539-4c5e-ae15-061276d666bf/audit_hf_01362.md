# [H] MJR-2 Wrong logic in withdrawAll

## Summary
Severity: High
Contest weight: 0.0275
Dataset id: 6940
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the moment withdrawAll counts balance as: balanceOfPool(_gauge) (VoterProxy.sol#L92) Correct logic should be: balanceOfPool(gauge).add(IERC20(token).balanceOf(address(this))). The withdrawAll method is used by shutdownSystem so potentially some tokens could remain in the contract.

## Recommendation
It is recommended to count amount of tokens as balanceOfPool(gauge).add(IERC20(token).balanceOf(address(this))).
