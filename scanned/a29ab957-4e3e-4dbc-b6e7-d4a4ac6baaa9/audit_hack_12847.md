# [M] Spot dex cant handle fee-on-transfer tokens

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L160-L161
Type: audit-issue

## Details
# Spot dex cant handle fee-on-transfer tokens

## Summary

`Dca.vy`, `LimitOrder.vy` and `TrailingStopDex.vy` does not properly support tokens that implement a fee on transfer. These types of tokens deduct a fee from any transfer of tokens, resulting in the recipient receiving less than the original amount sent. 

## Vulnerability Detail

The specific issue lies in the ERC20 token transfer.

Lests analyze the method `execute_limit_order` focus on lines [LimitOrders.vy#L160-L161](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L160-L161), this code assumes that the full `order.amount_in` will be transferred to `self`. This assumption is incorrect when the token in question implements a fee on transfer. When a fee is deducted, `self` will receive less tokens than `order.amount_in`. The subsequent call to `approve` and `ExactInputSingleParams` could therefore potentially fail as they rely on `self` having a balance of `order.amount_in`.

## Impact

This vulnerability could potentially halt token swaps midway if the token involved deducts a transfer fee. This can result in an unsuccessful token swap, which in turn could lock funds and possibly lead to financial loss for the user. 

## Code Snippet

- [Dca.vy#L200-L201](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L200-L201)
- [LimitOrders.vy#L160-L161](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/LimitOrders.vy#L160-L161)
- [TrailingStopDex.vy#L170-L171](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/TrailingStopDex.vy#L170-L171)

## Tool used

Manual Review

## Recommendation

To rectify this vulnerability, it's recommended to replace `order.amount_in` with the account of balance of `ERC20(order.token_in)` after the swap minus before the transferFrom call. This ensures that the correct balance (after any potential fees) is used for the approve call and the ExactInputSingleParams. It's also advised to add error handling for unsuccessful transfers and approvals.

Example:
```vy
    balance_before: uint256 = ERC20(order.token_in).balanceOf(self)
    
    # transfer token_in from user to self
    ERC20(order.token_in).transferFrom(order.account, self, order.amount_in)

    correct_amount: uint256 = ERC20(order.token_in).balanceOf(self) - balance_before

    # approve UNISWAP_ROUTER to spend token_in
    ERC20(order.token_in).approve(UNISWAP_ROUTER, correct_amount)

    # Use correct_amount instead of order.amount_in
```
