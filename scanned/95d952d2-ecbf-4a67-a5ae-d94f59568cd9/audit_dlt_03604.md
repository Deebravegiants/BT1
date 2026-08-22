# [M] Adding liquidity with `useZapping = true` allows user to steal funds

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-11
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/127
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/main/src/staking/Liquidity.sol#L88-L89


# Vulnerability details

## Summary
The function [depositLiquidityAndIncreaseShare() can be called with useZapping = true](https://github.com/othernet-global/salty-io/blob/main/src/staking/Liquidity.sol#L88-L89) which internally swaps one token to another in order to maintain the correct ratio and then makes the deposit. This can be exploited to gain funds.

## Details
The protocol has taken important steps which either make a traditional sandwich attack unprofitable for the attacker or impossible to execute altogether. These are -
- AAA i.e. the internal atomic arb.
- [Limiting user swaps to one per block to prevent bypassing arbitrage within a single block](https://github.com/code-423n4/2024-03-saltyio-mitigation?tab=readme-ov-file#:~:text=Limited%20user%20swaps%20to%20one%20per%20block%20to%20prevent%20bypassing%20arbitrage%20within%20a%20single%20block). This also makes sure that a malicious user can not perform a sandwich attack by front-running another user's liquidity addition. The malicious front-run-swap and later on the back-run-swap won't be allowed by the protocol in a single block.

These constraints are however bypassed by calling the function `depositLiquidityAndIncreaseShare()` with `useZapping = true`.
<br>

Instead of doing a front-run-swap, simply let the zapping feature do it for you. This internal swap is not recorded as an actual "swap" by the protocol and hence when later on a back-run-swap is executed, it's not reverted in spite of being in the same block. Additionally, [arbitrage no longer occurs when zapping liquidity](https://github.com/code-423n4/2024-03-saltyio-mitigation?tab=readme-ov-file#:~:text=Arbitrage%20no%20longer%20occurs%20when%20zapping%20liquidity), as implemented in [this PR](https://github.com/othernet-global/salty-io/commit/f16623e6bf1cdb0845b83ebf3592e30885a8fc61). So you have now bypassed AAA as well. 

## Attack Scenario
- In a pool of `token1` and `token2`, the fair ratio to be maintained for `token1:token2` is `1:1`. One can imagine that `1 wei` of each token = `$1`.
- The first depositor, Alice calls `depositLiquidityAndIncreaseShare(token, token2, 100 ether, 100 ether, 100 ether, 100 ether, 200 ether, block.timestamp, false)` to deposit `100 ether` of each token with proper slippage parameters. She gets `2 * 100 ether = 200e18` shares.
- Another depositor, Charlie calls `depositLiquidityAndIncreaseShare( token1, token2, 100 ether, 100 ether, 100 ether, 99 ether, 199 ether, block.timestamp, false )` to attempt a deposit of `100 ether` of each token. He understands that in a dynamic market various swaps might be happening at the same time, effecting the price ratios, hence provides a slippage of around `1%` for token2 by specifying minimum token2 as `99 ether` and minimum shares as `199 ether`. He does not tolerate any slippage for token1 in our example.
- Bob, who is a malicious user, front-runs Charlie and calls `depositLiquidityAndIncreaseShare( token1, token2, 1 ether, 0, 0, 0, 0, block.timestamp, true )` to add `1 ether` of token1 with `useZapping = true`.
- The protocol makes the internal swap. If we inspect the reserves after this, we find:
```js
  new balances: token1 = 100999999999999999999, token2 = 100000000000000000000
  Manipulated ratio of token2:token1 =: 0.990099009900990099
```
- The internal zap-swap has resulted in the ratios to change.
  - **Note that** Bob can use multiple alternate accounts of his to call `depositLiquidityAndIncreaseShare()` with `useZapping = true` multiple times. This would skew the ratio even further. He just needs to take care to be within the slippage limits set by Charlie.
- Charlie's transaction goes through after Bob's transaction. His slippage parameters were invoked.
- Bob now swaps `1 ether` of token2 for token1. He calls `depositSwapWithdraw(token2, token1, 1 ether, 0, block.timestamp)` and receives `1.004950249987624375 ether` of token1, higher than the market rate of `1 ether`.
- Bob now withdraws his entire liquidity shares to make a profit of `$2462673092946115`.

## Impact
Bob can steal funds from Charlie and profit.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/127_
