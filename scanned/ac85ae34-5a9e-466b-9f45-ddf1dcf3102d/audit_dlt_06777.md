# [H] CoreCollection can be reinitialized

## Summary
Severity: High
Chain: Smart contract
Component: 2022-03-joyn
Published: 2022-03-30
Source: https://github.com/code-423n4/2022-03-joyn-findings/issues/4
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-03-joyn/blob/main/core-contracts/contracts/CoreCollection.sol#L78-L97


# Vulnerability details

## Impact

Reinitialization is possible for CoreCollection as `initialize` function sets `initialized` flag, but doesn't control for it, so the function can be rerun multiple times.

Such types of issues tend to be critical as all core variables can be reset this way, for example `payableToken`, which provides a way to retrieve all the contract funds.

However, setting priority to be medium as `initialize` is `onlyOwner`. A run by an external attacker this way is prohibited, but the possibility of owner initiated reset either by mistake or with a malicious intent remains with the same range of system breaking consequences.

## Proof of Concept

`initialize` doesn't control for repetitive runs:

https://github.com/code-423n4/2022-03-joyn/blob/main/core-contracts/contracts/CoreCollection.sol#L87

## Recommended Mitigation Steps

Add `onlyUnInitialized` modifier to the `initialize` function:

https://github.com/code-423n4/2022-03-joyn/blob/main/core-contracts/contracts/CoreCollection.sol#L46-L49
