# [M] `transfer()` is not safe, please use `_safe_transfer()`

## Summary
Severity: Medium
Reporter: BugHunter101
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L334
Type: audit-issue

## Details
# `transfer()` is not safe, please use `_safe_transfer()`

## Summary

`transfer()` is not safe, please use `_safe_transfer()` because of some ERC20 token (such USDC) which `transfer()` may not return true/false

## Vulnerability Detail

`transfer()` is not safe, please use `_safe_transfer()` because of some ERC20 token (such USDC) which `transfer()` may not return true/false

for example:
```vyper
@external
def withdraw_fees(_token: address):
    amount: uint256 = ERC20(_token).balanceOf(self)
    assert amount > 0, "zero balance"

    ERC20(_token).transfer(self.owner, amount)
```

And other contract have the same problem such as use `transfer_from` instead of `safe_transfer_from`,please check!

## Impact

It will cause user does not know that the calling function is wrong because of some ERC20 token (such USDC) which `transfer()` may not return true/false

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L334

## Tool used

Manual Review

## Recommendation

Using `_safe_transfer` instead of `transfer` 
Using `_safe_transfer_from` instead of `transfer_from`
