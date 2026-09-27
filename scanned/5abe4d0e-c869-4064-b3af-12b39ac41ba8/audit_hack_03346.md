# [M] fee can be escaped with reentrancy.

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L158-L213
Type: audit-issue

## Details
# fee can be escaped with reentrancy.

## Summary

Comparing the before and after balance of the swap call for the swapped amount can be exploited to escape the fee by wrapping the actual swap inside a fake swap.

## Vulnerability Detail

The attacker can reenter with another externalSwap -> swapTarget.call to avoid the fee.

1. Swap minAmount with 1inch, inside the 1inch swap, reenter the externalSwap.
2. the inner swap is the actual amount: $1M, which should pay for fee 
3. After the inner swap, amountReceived includes the fee, which will be sent back to the user

As a result, the user successfully escaped most of the fee.

## Impact

User can not pay the fee.

## Code Snippet

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L158-L213

## Tool used

Manual Review

## Recommendation

Consider adding nonReentrant() modifier to external swap, multiswap and mix swap.
