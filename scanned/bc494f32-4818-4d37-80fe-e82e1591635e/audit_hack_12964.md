# [M] is_accepting_new_orders can block execute_limit_order

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L577
Type: audit-issue

## Details
# is_accepting_new_orders can block execute_limit_order

## Summary

In MarginDex, `is_accepting_new_orders` can block `execute_limit_order`.

## Vulnerability Detail

```vyper
@external
def execute_limit_order(_uid: bytes32):
    """
    @notice
        Allows executing a pending LimitOrder.
        Any msg.sender may execute LimitOrders for all accounts.
        The specified min_amount_out ensures the Trade is only
        opened at the intended exchange rate / price.
    """
    assert self.is_accepting_new_orders, "not accepting new orders"

@external
def set_is_accepting_new_orders(_is_accepting_new_orders: bool):
    """
    @notice
        Allows admin to put protocol in defensive or winddown mode.
        Open trades can still be completed but no new trades are accepted.
    """
    assert msg.sender == self.admin, "unauthorized"
    self.is_accepting_new_orders = _is_accepting_new_orders
```

This is an incorrect check of `is_accepting_new_orders` in `execute_limit_order`. `is_accepting_new_orders` should only be used in `post_limit_order`.
In contrast, execute_order in spot-dex does not check for `is_accepting_new_orders`.
As you can also see from the code comment in `set_is_accepting_new_orders`, this is an implementation error.

## Impact

When MarginDex suspends accepting new orders, old orders also cannot be executed.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L577

## Tool used

Manual Review

## Recommendation

Add a new pause check like spot-dex
