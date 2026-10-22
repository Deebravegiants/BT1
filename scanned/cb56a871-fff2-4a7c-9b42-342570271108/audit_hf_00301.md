# [M] DOS pay function

## Summary
Severity: Medium
Contest weight: 0.1459
Dataset id: 1506
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the `pay()` function users repay their debt and in line 364: <https://github.com/code-423n4/2022-01-timeswap/blob/main/Timeswap/Timeswap-V1-Core/contracts/TimeswapPair.sol#L364> it decreases their debt.

Let's say a user wants to repay all his debt, he calls the `pay()` function with his full debt. An attacker can see it and frontrun to repay a single token for his debt (since it’s likely the token uses 18 decimals, a single token is worth almost nothing) and since your solidity version is above 0.8.0 the line: `due.debt -= assetsIn[i];` will revert due to underflow.

The attacker can keep doing it every time the user is going to pay and since 1 token is basically 0$ (18 decimals) the attacker doesn’t lose real money.

## Proof of Concept
From solidity docs:

Since Solidity 0.8.0, all arithmetic operations revert on over- and underflow by default, thus making the use of these libraries unnecessary.

## Recommendation
If `assetsIn[i]` is bigger than `due.debt` set `assetsIn[i] = due.debt` and `due.debt = 0`.

The convenience contract will implement how much asset to pay in.
