# [H] LimitOrders.vy: Profit Draining Vulnerability in LimitOrders.vy Through Overstated min_amount_out

## Summary
Severity: High
Reporter: pengun
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L173-L190
Type: audit-issue

## Details
# LimitOrders.vy: Profit Draining Vulnerability in LimitOrders.vy Through Overstated min_amount_out

## Summary
There is a vulnerability in the `LimitOrders.vy` contract where an attacker can siphon profits intended for the protocol.

## Vulnerability Detail
`LimitOrders.vy` processes users' limit orders. Any residual funds from a transaction are split between the path searcher and the protocol, resulting in the contract holding profits from trades.

A malicious user can exploit this setup in the following way:

1. They post a limit order using the `post_limit_order `function, intentionally setting the min_amount_out value higher than the actual exchange rate.
2. They call `execute_limit_order`, setting the `share_profit` parameter to false.
3. The `_safe_transfer` function always sends the amount set in `min_amount_out`, allowing the user to drain the tokens left as protocol profits.

In this case, setting `share_profit` to false is crucial. If share_profit is set to true, the statement `profit: uint256 = amount_out - order.min_amount_out` will cause an underflow and revert the transaction.

## Impact
The vulnerability could lead to significant financial losses for the protocol. A malicious user can drain all profits that have been allocated to the protocol by exploiting this vulnerability.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L173-L190

## Tool used

Manual Review

## Recommendation
To prevent this, an additional step should be implemented to verify whether min_amount_out is greater than the actual amount exchanged through the swap.
