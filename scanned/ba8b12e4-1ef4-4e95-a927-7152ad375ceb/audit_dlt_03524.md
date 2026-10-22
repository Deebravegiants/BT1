# [M] Add reentracy protections on function `executeTrade`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-06-tracer
Published: 2021-07-02
Source: https://github.com/code-423n4/2021-06-tracer-findings/issues/143
Type: code-finding

## Details
# Handle

shw


# Vulnerability details

## Impact

As written in the to-do comments, reentrancy could happen in the `executeTrade` function of `Trader` since the `makeOrder.market` can be a user-controlled external contract.

## Proof of Concept

Referenced code:
[Trader.sol#L121-L126](https://github.com/code-423n4/2021-06-tracer/blob/main/src/contracts/Trader.sol#L121-L126)

## Recommended Mitigation Steps

Add a reentrancy guard (e.g., the [implementation](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/security/ReentrancyGuard.sol) from OpenZeppelin) to prevent the users from reentering critical functions.
