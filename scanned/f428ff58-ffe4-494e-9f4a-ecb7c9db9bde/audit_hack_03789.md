# [H] Potential reentrancy attack

## Summary
Severity: High
Reporter: pzeus
Source: https://github.com/opynfinance/squeeth-monorepo/blob/main/packages/hardhat/contracts/strategy/CrabStrategyV2.sol#L698
Type: audit-issue

## Details
# Potential reentrancy attack

## Summary
Potential of reentrancy exploit
## Vulnerability Detail
There is an attack vector of reentering the following [function](https://github.com/opynfinance/squeeth-monorepo/blob/main/packages/hardhat/contracts/strategy/CrabStrategyV2.sol#L698)
## Impact
High, since the attacker could steal either users or protocol's funds
## Code Snippet
https://github.com/opynfinance/squeeth-monorepo/blob/main/packages/hardhat/contracts/strategy/CrabStrategyV2.sol#L698
## Tool used

Manual Review

## Recommendation
I would recommend the usage of `nonReentrant` guard from [OpenZeppelin](https://github.com/OpenZeppelin) framework
