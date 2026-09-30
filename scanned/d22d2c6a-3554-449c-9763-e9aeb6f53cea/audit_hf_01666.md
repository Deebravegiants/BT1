# [M] fyToken contribution limits are incorrect as they compare fyToken and buyToken amounts with idoSize in idoToken units

## Summary
Severity: Medium
Contest weight: 0.3768
Dataset id: 9017
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The fyToken contribution limit is enforced as:
```solidity
uint256 globalTotalFunded = idoConfig.totalFunded[buyToken] + idoConfig.totalFunded[fyToken] + amount;
...
uint256 maxFyTokenFunding = (idoConfig.idoSize * idoConfig.fyTokenMaxBasisPoints) / 10000;
if (globalTotalFunded > maxFyTokenFunding) revert FyTokenContributionExceedsLimit();
```
As can be seen, maxFyTokenFunding is in idoToken units (idoSize refers to idoToken) and globalTotalFunded in fyToken or buyToken units.

## Recommendation
Make sure the limit is imposed by comparing the same units.
