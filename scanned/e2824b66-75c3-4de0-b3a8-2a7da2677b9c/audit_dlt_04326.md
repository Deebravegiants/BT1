# [H] Reentrancy exploit

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-nounsdao
Published: 2022-12-07
Source: https://github.com/sherlock-audit/2022-11-nounsdao-judging/issues/26
Type: sherlock-finding

## Details
pzeus

high

# Reentrancy exploit

## Summary
Potential of reentrancy attack
## Vulnerability Detail
There is an external contract call which might end up with an reentrancy exploit since we do not know the implementation of the ERC token
## Impact
Might end up with stealing funds from the protocol
## Code Snippet
https://github.com/sherlock-audit/2022-11-nounsdao/blob/main/src/Stream.sol#L237
## Tool used

Manual Review

## Recommendation
Usage of [OpenZeppelin's](https://github.com/OpenZeppelin) `nonReentrant` guard or some other custom implementation preventing this
