# [M] `execute_dca_order()` does not check if `order.account == msg.sender`

## Summary
Severity: Medium
Reporter: BugHunter101
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L190
Type: audit-issue

## Details
# `execute_dca_order()` does not check if `order.account == msg.sender`

## Summary

`execute_dca_order()` does not check if `order.account == msg.sender` , it may cause attacker to cancel dca_order and clear dca_order when the user is temporarily not eligible for execution

## Vulnerability Detail


As we can see, in `execute_dca_order()`, it will check `account_balance < order.amount_in_per_execution`,and the `account_balance = ERC20(order.token_in).balanceOf(order.account)`. However, if `iaccount_balance < order.amount_in_per_execution` ,it will call `_cancel_dca_order()`, then, the attacker can use call execute_dca_order() to clear someone 's order when atttacker monitor the user's`ERC20(order.token_in).balanceOf(order.account)` < `order.amount_in_per_execution`
```vyper
    # ensure user has enough token_in
    account_balance: uint256 = ERC20(order.token_in).balanceOf(order.account)
    if account_balance < order.amount_in_per_execution:
        log DcaOrderFailed(_uid, order.account, "insufficient balance")
        self._cancel_dca_order(_uid, "insufficient balance")#@audit
        return
```
For example:
1. Alice set a order and order.amount_in_per_execution = 100 tokenA, and now Alice have 101 tokenA
2. But now, Alice may need to use 50 tokenA to do other things, and may return later
3. Bob monitor the Alice tokenA 's balance is change to 101-50 =51 ,so this conform to`ERC20(order.token_in).balanceOf(order.account)` < `order.amount_in_per_execution`
4. Bob call `execute_dca_order()` and set the `_uid` is Alice 
5. Because of `ERC20(order.token_in).balanceOf(order.account)` < `order.amount_in_per_execution` ,so the order will clear
6. Now Alice got back 50 tokenA, and the balance is 101, it will cause wrong when she wants to call `execute_dca_order()` because of the order is clear.


## Impact

it may cause attacker to cancel dca_order and clear dca_order when the user is temporarily not eligible for execution

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L190

## Tool used

Manual Review

## Recommendation

Check if `order.account == msg.sender` . And please check other function like `exec_xxx_order()`, it maybe has same problem.
