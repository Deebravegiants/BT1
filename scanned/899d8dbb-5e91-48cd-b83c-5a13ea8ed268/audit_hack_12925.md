# [H] Incorrect Way Of Making Profit For `Spot-dex`

## Summary
Severity: High
Reporter: 0xhacksmithh
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L189
Type: audit-issue

## Details
# Incorrect Way Of Making Profit For `Spot-dex`

## Summary
Refer Details Section
## Vulnerability Detail
 Inside functions `execute_trailing_stop_limit_order(0` and `execute_limit_order()`, There is a feature where it works like these
. User specify input parameters as `Order` with 
. Order contains `min_amount_out` which signifies minimum amount out from swap to act as a slippage protection
. Then Swapping occures
. After `Swapping`, `order.min_amount_out` send back to caller instead of whole `Swapped Amount`
. And Protocol take `swap output amount - order.min_amount_out` as profit

There may be a problem here that caller may sometime set less `min_amount_out` or even forget some time to set.
In that case a large amount or even whole amount of user token will took as Protocol profit.
```solidity
    UniswapV3SwapRouter(UNISWAP_ROUTER).exactInputSingle(uni_params)

    ERC20(order.token_out).transfer(order.account, order.min_amount_out)
```
## Impact
Refer Details Section

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L189
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L188

## Tool used

Manual Review

## Recommendation
Should re-consider those methods
