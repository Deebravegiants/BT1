# [M] withdrawAuction distribution can be altered

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/227
Type: sherlock-finding

## Details
hyh

medium

# withdrawAuction distribution can be altered

## Summary

If withdrawAuction() be called when an auction is not live, a griefing attack is possible: Bob the withdrawer can front-run the withdrawAuction() with dequeueCrab(), removing his withdrawal, causing the withdrawAuction() accounting malfunction is a sense that it will distribute not 100% of the rewards, but less as the function parameters were determined as if Bob's withdrawal was there.

This is possible as all other parameters determining the sum are dynamic, while `_p.crabToWithdraw` is pre-determined by function caller (auction operator).

The remaining `100% - actual` part will be frozen on the contract balance as the corresponding user entries be successfully deleted. 

## Vulnerability Detail

withdrawAuction() determines the WETH `amountIn` to swap for USDC to distribute dynamically, and sum of `withdraw.amount` is dynamic given that auction is not live. I.e. both USDC total sum to distribute and sum of `withdraw.amount` will be reduced by Bob's actions, but `_p.crabToWithdraw` will stay the same.

I.e. the `usdcAmount = (((withdraw.amount * 1e18) / _p.crabToWithdraw) * usdcReceived) / 1e18` formula has `_p.crabToWithdraw` determined by the auction organizer beforehand, while `usdcReceived` is dynamic and cumulative sum of `withdraw.amount` can be manipulated by Bob, who removed his crabs from the queue.

This means that `usdcReceived` and the sum of `withdraw.amount` was reduced by Bob's dequeueCrab(), but `_p.crabToWithdraw` stayed the same, being determined by the state where Bob's queue item was present. I.e. sum of `withdraw.amount` no longer corresponds to `_p.crabToWithdraw` and withdrawers will receive less than 100% of `usdcReceived` in total.

This will cause a shortage of actual withdrawal queue, due to which the remaining withdrawers will receive less funds.

As there are no rescue function, the remaining USDC will be frozen on contract balance.

## Impact

Withdrawers will lose funds, receiving less USDC than was due. The unallocated funds will be permanently frozen on the contract balance.

Setting the severity to be medium as `isAuctionLive == false` is required for dequeueCrab().

## Code Snippet

withdrawAuction() determines how much WETH to sell dynamically and base USDC amount calculations on `_p.crabToWithdraw`:

https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L624-L722


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/227_
