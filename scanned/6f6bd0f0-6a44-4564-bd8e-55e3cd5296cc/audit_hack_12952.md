# [M] The `MarginDex.execute_limit_order()` function validates `is_accepting_new_orders` which is incorrect because the queued orders should be executed

## Summary
Severity: Medium
Reporter: 0xbepresent
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L829
Type: audit-issue

## Details
# The `MarginDex.execute_limit_order()` function validates `is_accepting_new_orders` which is incorrect because the queued orders should be executed

## Summary

The `MarginDex.execute_limit_order()` function validates incorrectly if the protocol is accepting new orders because queued orders should be executed.

## Vulnerability Detail

The [Vault.set_is_accepting_new_orders()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L829) function helps to put the protocol in defensive mode, as the funcion comment says: *Allows admin to put protocol in defensive or winddown mode. Open trades can still be completed but no new trades are accepted.*. So open trades (queued orders) can be executed even when the protocol is in defensive mode.

The problem is that the [MarginDex.execute_limit_order()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L569C5-L569C24) validates again if the protocol is accepting new orders in the 577 code line:

```python
File: MarginDex.vy
569: def execute_limit_order(_uid: bytes32):
...
577:     assert self.is_accepting_new_orders, "not accepting new orders"
...
```

That is a contradiction because the order is validated before is queued if the protocol is accepting new orders in the [MarginDex.post_limit_order()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L514C5-L514C21) 530 code line:

```python
File: MarginDex.vy
514: def post_limit_order(
515:     _account: address,
516:     _position_token: address,
517:     _debt_token: address,
518:     _margin_amount: uint256,
519:     _debt_amount: uint256,
520:     _min_amount_out: uint256,
521:     _valid_until: uint256,
522:     _tp_orders: DynArray[TakeProfitOrder, 8],
523:     _sl_orders: DynArray[StopLossOrder, 8],
524: ) -> LimitOrder:
...
...
530:     assert self.is_accepting_new_orders, "not accepting new orders"
```

So, it is not necessary to validate again the `is_accepting_new_orders` in the `Vault.execute_limit_order()`.

The [Vault.add_tp_order()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L337) function works correctly, because it [validates if the protocol is in defensive mode](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L337) before the order is queued. Then, once is queued, the order can be [executed without restrictions](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L378) even if the protocol is in defensive mode.

## Impact

Queued `post_limit_order` orders can not be executed if the protocol goes into defensive mode.


## Code Snippet

- The [Vault.set_is_accepting_new_orders()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L829) function.
- The [MarginDex.execute_limit_order()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L569C5-L569C24) function.
- The [MarginDex.post_limit_order()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L514C5-L514C21) function.

## Tool used

Manual review

## Recommendation

It is not necessary to validates if the protocol is defensive mode in the [Vault.execute_limit_order()](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L577) becuase the queued orders should be executed:

```diff
@external
def execute_limit_order(_uid: bytes32):
    """
    @notice
        Allows executing a pending LimitOrder.
        Any msg.sender may execute LimitOrders for all accounts.
        The specified min_amount_out ensures the Trade is only
        opened at the intended exchange rate / price.
    """
--  assert self.is_accepting_new_orders, "not accepting new orders"
```
