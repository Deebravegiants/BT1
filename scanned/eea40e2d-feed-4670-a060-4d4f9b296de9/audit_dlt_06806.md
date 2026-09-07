# [M] DOS pay function

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-timeswap
Published: 2022-01-06
Source: https://github.com/code-423n4/2022-01-timeswap-findings/issues/86
Type: code-finding

## Details
# Handle

egjlmn1


# Vulnerability details

in the `pay()` function users repay their debt and in line 364:
https://github.com/code-423n4/2022-01-timeswap/blob/main/Timeswap/Timeswap-V1-Core/contracts/TimeswapPair.sol#L364
it decreases their debt.

lets say a user wants to repay all his debt, he calls the `pay()` function with his full debt.
an attacker can see it and frontrun to repay a single token for his debt (since it's likely the token uses 18 decimals, a single token is worth almost nothing)
and since your solidity version is above 0.8.0 the line:
`due.debt -= assetsIn[i];` will revert due to underflow

The attacker can keep doing it everytime the user is going to pay and since 1 token is baisicly 0$ (18 decimals) the attacker doesn't lose real money

## Impact
A DoS on every user that  repay his full debt (or enough that the difference between his total debt to what he pays his negligible)

## Proof of Concept
From solidity docs
```
Since Solidity 0.8.0, all arithmetic operations revert on over- and underflow by default, thus making the use of these libraries unnecessary.
```

## Tools Used
manual code review

## Recommended Mitigation Steps
if `assetsIn[i]` is bigger than `due.debt` set `assetsIn[i]=due.debt` and `due.debt=0`
