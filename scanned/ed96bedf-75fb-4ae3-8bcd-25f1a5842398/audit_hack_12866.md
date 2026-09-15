# [H] Leverage limit orders to extract value via margin trading

## Summary
Severity: High
Reporter: 0xyPhilic
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L128-L149
Type: audit-issue

## Details
# Leverage limit orders to extract value via margin trading

## Summary

The protocol offers two types of trading - limit orders and margin trading. The limit orders are handled by `LimitOrders.vy` where a user can open a limit order by executing `post_limit_order`, which allows the user to define `amount_in` of one token and `min_amout_out` of another essentially giving the option to the user to set a specific price at which he would like to make the purchase (below that price as example the tx would fail due to the `min_amount_out` condition not satisfied). The limit orders can be executed by any third party through an arbitrary `_path` which is passed by that third party when invoking `execute_limit_order` function. On the other hand the `MarginDex.vy` allows a user to `open_trade` with a margin provided by LPs. Opening a trade is basically swapping one asset for another via UniswapV3 where part of the funds for the swap are provided by the trader and the rest (margin) are provided by the LPs. which the trader borrows. At any point the trader can use `close_trade` which makes a full close of the open position by swapping back to the original asset via UniswapV3 and repaying the LPs the borrowed amount + fees. Whatever is left above that is the trader PnL. 

## Vulnerability Detail

The vulnerability occurs when a savvy trader leverages limit orders in order to boost the price of a given asset on UniswapV3 where he/she can open a margin position, thus making a profit on the back of the LPs in the `MarginDex`. A requirement here would be that either there is a significant amount of `limit orders` within a given range and/or a pool with lower liquidity is set for margin trading. The following scenario illustrates the exploit path:

1/ A malicious user notices multiple limit orders within a given range to buy token X with token Y (high value limit orders)
2/ The malicious user creates a SC that will interact with the protocol and execute multiple actions within a single transaction (this step is not necessary as a simple bot can do it in multiple transactions, but it eases the attacker)
3/ The contract call first opens a margin trading position on the `MarginDex` swapping token X for token Y with additional liquidity from LPs
4/ After the margin position is opened the contract call then executes all the `limit_orders` which are pending through the pool on which the margin position is open - users buy token Y with token X, which increases the value of token Y significantly
5/ Immediately after the limit orders execution the final step in the contract call is to close the margin position of the malicious user by swapping token Y to token X at an artificially increased price at a profit for the malicious user

The effect of the above mentioned exploit can be further increased by using flash loan - either to affect the price in the pool in order to fit it within the limit orders range or just to increase the potential profits of the malicious user as long as there is enough available liquidity provided by LPs.

## Impact

This attack scenario affects both users and liquidity providers since users that bought token Y with token X by getting their `limit_orders` executed will be at a loss after the malicious user closes his margin position, since it will decrease the price of token Y.
At the same time the malicious user will profit on the backs of LPs as their liquidity will be used to pay the malicious user gains.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L128-L149

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L205-L216

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L129-L191

## Tool used

Manual Review

## Recommendation

The best way to avoid such a scenario is to set a reasonable cooldown between `open_trade` and `close_trade` on the `MarginDex.vy`, similarly to the cooldown currently set for `withdraw_liquidity`.
