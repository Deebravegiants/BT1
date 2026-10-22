# [M] Spot contracts execute functions will revert before swapping fee-on-transfer tokens

## Summary
Severity: Medium
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L161
Type: audit-issue

## Details
# Spot contracts execute functions will revert before swapping fee-on-transfer tokens

## Summary
`execute_limit_order` and `execute_dca_order` will revert before swapping fee-on-transfer tokens against any kind of token.

## Vulnerability Detail
When a user's limit order gets executed tokens are sent from the user to the `LimitOrders` contract in `execute_limit_order`:

[LimitOrders.vy#L161](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L161)
```solidity
self._safe_transfer_from(order.token_in, order.account, self, order.amount_in)
```

But during the transfer a fee will get deducted from `order.amount_in`, therefore `order.amount_in - fee` will be present in the contract. Then, when calling `exactInput` to carry out the swap, `order.amount_in` will still be used as `amountIn` parameter:

[LimitOrders.vy#L173-L180](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L173-L180)
```solidity
uni_params: ExactInputParams = ExactInputParams({
        path: path,
        recipient: self,
        deadline: block.timestamp,
        amountIn: order.amount_in,
        amountOutMinimum: order.min_amount_out
    })
    amount_out: uint256 = UniswapV3SwapRouter(UNISWAP_ROUTER).exactInput(uni_params)
```

Thus, the call to the Uniswap router will revert since there isn't enough token being sent by the `LimitOrders` contract. Same goes for `Dca` contract.

## Impact
`LimitOrders` and `Dca` contracts doesn't support sending fee-on-transfer tokens for swaps.

## Code Snippet
[LimitOrders.vy#L161](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L161)
[LimitOrders.vy#L173-L180](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L173-L180)

## Tool used

Manual Review

## Recommendation
Consider checking the balances before and after sending the tokens to the contract and using the difference as `amountIn` for the swap.
