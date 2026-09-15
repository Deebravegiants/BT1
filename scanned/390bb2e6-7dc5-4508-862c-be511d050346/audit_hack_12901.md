# [M] `Dca.execute_dca_order` and `LimitOrders.execute_limit_order` could revert on zero value transfers

## Summary
Severity: Medium
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable-sces60107/tree/main#q-which-erc20-tokens-do-you-expect-will-interact-with-the-smart-contracts
Type: audit-issue

## Details
# `Dca.execute_dca_order` and `LimitOrders.execute_limit_order` could revert on zero value transfers

## Summary

There are certain ERC20 tokens which revert on zero-value transfers (e.g. LEND). And the README.md mentions that the Spot contracts need to be able to interact with any pool/token,
https://github.com/sherlock-audit/2023-06-unstoppable-sces60107/tree/main#q-which-erc20-tokens-do-you-expect-will-interact-with-the-smart-contracts
https://github.com/sherlock-audit/2023-06-unstoppable-sces60107/tree/main#additional-information-on-tokens-used
> The Spot contracts need to be able to interact with any pool/token 

`Dca.execute_dca_order` and `LimitOrders.execute_limit_order` could revert on zero value transfers if `profit/2` is zero.

## Vulnerability Detail


`Dca.execute_dca_order` and `LimitOrders.execute_limit_order` send the profit if `_share_profit` is true. But it doesn’t consider the zero-value transfers, which can cause revert if the `token_out` doesn’t support zero value transfer.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L231
```vyper
def execute_dca_order(_uid: bytes32, _uni_hop_path: DynArray[address, 3], _uni_pool_fees: DynArray[uint24, 2], _share_profit: bool):
    …

    # allows searchers to execute for 50% of profits
    if _share_profit:
        profit: uint256 = amount_out - amount_minus_fee
        self._safe_transfer(order.token_out, msg.sender, profit/2)
    
    …
```
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L189
```vyper
def execute_limit_order(_uid: bytes32, _path: DynArray[address, 3], _uni_pool_fees: DynArray[uint24, 2], _share_profit: bool):
    …

    # allows searchers to execute for 50% of profits
    if _share_profit:
        profit: uint256 = amount_out - order.min_amount_out
        self._safe_transfer(order.token_out, msg.sender, profit/2)
    
    …
```

## Impact

The executions of orders shouldn’t revert when `profit/2` is zero.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L231
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L189


## Tool used

Manual Review

## Recommendation

Add a check to prevent zero-value transfers
```diff
def execute_dca_order(_uid: bytes32, _uni_hop_path: DynArray[address, 3], _uni_pool_fees: DynArray[uint24, 2], _share_profit: bool):
    …

    # allows searchers to execute for 50% of profits
    if _share_profit:
        profit: uint256 = amount_out - amount_minus_fee
-       self._safe_transfer(order.token_out, msg.sender, profit/2)
+       if profit/2 > 0:
+           self._safe_transfer(order.token_out, msg.sender, profit/2)
    
    …
```
