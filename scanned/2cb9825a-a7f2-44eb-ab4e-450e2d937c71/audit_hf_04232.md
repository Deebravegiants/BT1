# [M] M-10 | Keeper Gas Fee Is Fixed While Execution Gas Is Not

## Summary
Severity: Medium
Contest weight: 0.1146
Dataset id: 21128
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Every keeper operation is rewarded with a specific keeper fee, where the gas units are fixed and the fee is calculated on the spot with: gas * gasPrice + keeperProfit. However, some operations can use much more gas than others. Example: • Settling a normal order versus one with 3 hooks. • Flagging a position with 1 collateral versus one with 10 collaterals. • Liquidating a position where you don't need to loop through the window for previous liquidations versus one where you need to loop through every block (using the while). As a result some orders will be significantly more profitable than others, and some orders may end up being unprofitable entirely, even with a fee buffer, and as a result won't be executed.

## Recommendation
Consider tracking the gas used during an execution with gasLeft and use this amount to compute the keeper’s fee with an added profit margin.
