# [M] Functions `execute_dca_order` and `execute_limit_order` can be both called by `order.account` with the `_share_profit` boolean to true to get more rewards than intended

## Summary
Severity: Medium
Reporter: Vagner
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L186
Type: audit-issue

## Details
# Functions `execute_dca_order` and `execute_limit_order` can be both called by `order.account` with the `_share_profit` boolean to true to get more rewards than intended

## Summary
Functions `execute_dca_order` and `execute_limit_order` from `Dca.vy` and `LimitOrders.vy` can be both called by anyone to execute the Dca's and limit orders set by the users , including the user who created the Dca/LimitOrder.
## Vulnerability Detail
Functions `execute_dca_order` and `execute_limit_order` from `Dca.vy` and `LimitOrders.vy` can be both called by anyone to execute the Dca's and limit orders set by the users. The people that executes those order, which are named `searchers` from the comments https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L186
can set the boolean argument `_share_profit` to true, so they can get some of the fees of the Dca order or limit order, since they were active in the protocol. The problem is that even the one who created the Dca/LimitOrder can call the function with the same boolean, getting more rewards for himself on each trade executed. Since there is not check for `order.account` to be different for `msg.seder`, everybody creating an order would look to execute it by himself so he can get the `order.min_amount_out` or ` amount_minus_fee` + the 50% of the rewards for the searchers, making it so there is no real initiative for searchers to watch and execute orders.
## Impact
This is a medium severity since users can profit from all of the fees of the protocol, making them get more tokens than they are supposed to creating no initiative for searchers to interact with the protocol.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L186-L189
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L228-L231
## Tool used

Manual Review

## Recommendation
If you want people that are active in the protocol to benefit from searching for orders that executable, make it so, if the function `execute_dca_order` or `execute_limit_order` is called by the `order.account` , they are not able to also get the 50% of the profits, making the 50% of the profits exclusive only  for other accounts.
