# [H] Everyone can call mintRebalancer and burnRebalancer.

## Summary
Severity: High
Reporter: 0x2e
Source: https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L204-L210
Type: audit-issue

## Details
# Everyone can call mintRebalancer and burnRebalancer.

## Summary

Everyone can call mintRebalancer and burnRebalancer. But these functions should only be called by rebalancer.

## Vulnerability Detail

Everyone can call mintRebalancer and burnRebalancer. But these functions should only be called by rebalancer.

## Impact

For example, when users call `rebalance()` in USSDRebalancer, an attacker can frontrun and call mintRebalancer(max), then the `rebalance()` will revert due to integer overflow.

## Code Snippet

https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L204-L210

## Tool used

Manual Review

## Recommendation

Add modifier onlyBalancer.
