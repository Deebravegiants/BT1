# [M] `TrailingStopDex.execute_trailing_stop_limit_order()` does not use `@nonreentrant('lock')`

## Summary
Severity: Medium
Reporter: BugHunter101
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165
Type: audit-issue

## Details
# `TrailingStopDex.execute_trailing_stop_limit_order()` does not use `@nonreentrant('lock')`

## Summary

`TrailingStopDex.execute_trailing_stop_limit_order()` does not use `@nonreentrant('lock')` ,it may cause reentrancy attack.

## Vulnerability Detail

As we can see ,`TrailingStopDex.execute_trailing_stop_limit_order()` does not use `@nonreentrant('lock')` ,it may cause reentrancy attack.
```vyper
@external
def execute_trailing_stop_limit_order(_uid: bytes32, _proof_round_id: uint80 ,_uni_pool_fee: uint24):
    order: TrailingStopLimitOrder = self.positions[_uid]

    assert order.valid_until > block.timestamp, "order expired"
    assert order.executed == False, "order already executed"

    account_balance: uint256 = ERC20(order.token_in).balanceOf(order.account)
    if account_balance < order.amount_in:
        log TrailingStopLimitOrderFailed(_uid, order.account, "insufficient balance")
        self._cancel_limit_order(_uid)
        return

    account_allowance: uint256 = ERC20(order.token_in).allowance(order.account, self)
    if account_allowance < order.amount_in:
        log TrailingStopLimitOrderFailed(_uid, order.account, "insufficient allowance")
        self._cancel_limit_order(_uid)
        return
    ......
    ......
```

And we can see other contract 's `execute_xxx_order()` using the`@nonreentrant('lock')` ,such Dca.vy `execute_dca_order()` function
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165
## Impact

it may cause reentrancy attack.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L88

## Tool used

Manual Review

## Recommendation

Using  `@nonreentrant('lock')` such like Dca.vy  `execute_dca_order()` function
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L165
