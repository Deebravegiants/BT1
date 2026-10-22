# [M] secRewardsPerShare Insufficient precision

## Summary
Severity: Medium
Contest weight: 0.5521
Dataset id: 20607
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
We also introduced the field secRewardDebt. The idea of this field is to enable any lending platforms that are integrated with Neofinance Coordinator to send their own rewards based on this value (or rather the difference of this value since the last time secondary rewards were sent) and their own emission schedule for the tokens.

The current calculation formula for `secRewardsPerShare` is as follows:
```solidity
market.secRewardsPerShare += uint128((blockDelta * 1e18) / marketSupply);
```
`marketSupply` is `cNOTE`, with a precision of `1e18`. So as long as the supply is greater than `1` cNote, `secRewardsPerShare` is easily `rounded down` to `0`. Example: marketSupply = 10e18 blockDelta = 1 secRewardsPerShare=1 * 1e18 / 10e18 = 0

## Recommendation
It is recommended to use 1e27 for `secRewardsPerShare`:
```solidity
market.secRewardsPerShare += uint128((blockDelta * 1e27) / marketSupply);
```
The Warden has shown how, due to incorrect precision, it is possible to create a loss due to rounding down.

Because the loss is limited to yield, Medium Severity seems most appropriate.
