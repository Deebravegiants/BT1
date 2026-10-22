# [H] Calculating the limit order price using  `amountMinOut` , will freeze orders

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L82-L88
Type: audit-issue

## Details
# Calculating the limit order price using  `amountMinOut` , will freeze orders

## Summary
Calculating the limit order price using  `amountMinOut` , will freeze orders

## Vulnerability Detail
Currently when executing limit orders the keepers check that the price is met according to the `min_amount_out ` param. Unstoppable is getting the price orders by the division of 

`_amount_in and _min_amount_out`

`def post_limit_order(
        _token_in: address,
        _token_out: address,
        _amount_in: uint256,
        _min_amount_out: uint256,
        _valid_until: uint256
    ):`

As discussed with sponsor: `Our own keepers execute as soon as min_amount_out can be achieved by executing the swap. `

Therefore, order execution will be triggered as soon as the price is reached with no room for slippage.

This will cause 2 problems:

- Malicious MEVs can directly create extra slippage so that the order does not go through due to minAmountOut being the exact price the user expects.
- The market itself will fluctuate, even more in this case that we are in arbitrum and there is not as much liquidity as in mainnet, and minAmountOut will lot of times will not be reached.

## Impact
This will cause loss of funds for keepers and delay of execution of the orders for the users. The price might not be back to that point in a while.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L82-L88

## Tool used
Manual Review

## Recommendation
Consider calculating the amounMinOut in a different way instead of using it as a price point. You can still divide amountOut and amountIn, but do not use minAmounOut for that because it will freeze orders.
