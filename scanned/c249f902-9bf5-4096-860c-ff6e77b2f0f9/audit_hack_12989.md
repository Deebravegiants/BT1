# [M] Incomplete implementation on `TrailingStopDex`, missing profit swapping and sharing

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L130-L194
Type: audit-issue

## Details
# Incomplete implementation on `TrailingStopDex`, missing profit swapping and sharing

## Summary

In the [`TrailingStopDex.vy`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L130-L194) contract of the Unstoppable protocol, there are two critical functionalities left unimplemented - swapping of profits and profit sharing between `msg.sender` and `self`.

## Vulnerability Detail

There is an absence of methods to handle and distribute profits. The corresponding lines of code are left with **TODO** comments indicating incomplete implementation. Such a situation can potentially lead to economic inefficiencies and misaligned incentives.

## Impact

Given that these functionalities are not currently implemented, any profits generated from trades exceeding the `min_amount_out` threshold will stay in the contract and will not be swapped or distributed. This could lead to economic inefficiencies, potential funds lockup, and misaligned incentives for users and the protocol.

## Code Snippet

The relevant code snippet is found in the `execute_trailing_stop_limit_order` function, where TODO comments highlight these gaps:
[`TrailingStopDex.vy#L191-L192`](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L191-L192)
```vy
ERC20(order.token_out).transfer(order.account, order.min_amount_out) # anything > min_amount_out stays in contract as profit

# TODO swap profits into what?
# TODO share profit between msg.sender and self?
```

## Tool used

Manual Review

## Recommendation

To address this issue, the protocol should:

1) Implement a profit swapping mechanism that determines how profits (amounts exceeding `min_amount_out`) are to be swapped. This could potentially involve swapping these profits to another desirable token.

2) Establish a profit-sharing mechanism to distribute these profits between `msg.sender` (the executor of the order) and `self` (the contract). This distribution should be performed in a way that aligns with the protocol's economic design and user incentives.

These implementations would help to prevent the potential accumulation of undistributed profits in the contract and to ensure the protocol operates in line with its intended economic design and incentives for users.
