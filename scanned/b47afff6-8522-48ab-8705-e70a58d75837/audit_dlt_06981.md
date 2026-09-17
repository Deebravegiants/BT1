# [M] Staking tokens can be stolen

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-anchor
Published: 2022-03-09
Source: https://github.com/code-423n4/2022-02-anchor-findings/issues/37
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-anchor/blob/7af353e3234837979a19ddc8093dc9ad3c63ab6b/contracts/anchor-token-contracts/contracts/gov/src/staking.rs#L88


# Vulnerability details

## Impact
The staking contract keeps track of _shares_ of each user.
When withdrawing from the staking contract the `amount` parameter is converted to `shares` and this value is decreased (`shares = amount / total_balance * total_share`).
This shares calculation rounds down which allows stealing tokens.

The current code seems to try to protect against this by doing a maximum `std::cmp::max(v.multiply_ratio(total_share, total_balance).u128(), 1u128)` but this only works for the case where the shares would round down to zero. It's still exploitable.

```rust
let withdraw_share = amount
// @audit only rounds up when it'd be zero, but should always round up
    .map(|v| std::cmp::max(v.multiply_ratio(total_share, total_balance).u128(), 1u128))
// @audit sets it to the `amount` parameter if not `None`
let withdraw_amount = amount
    .map(|v| v.u128())
```

#### POC
Assume `total_balance = 2e18` and `total_share=1e18`. Then withdrawing/burning one share should allow withdrawing `total_balance / total_share = 2` amount.
However, imagine someone owns 1 shares (bought for 2 amount). Then `withdraw_voting_tokens(amount=3)`. And `withdraw_share = std::cmp::max(v.multiply_ratio(total_share, total_balance).u128(), 1u128) = max(amount=3 * total_share=1e18 / total_balance=2e18, 1) = max("3/2", 1) = 1`
The attacker made a profit.

The attacker can make a profit by staking the least `amount` to receive one share, and then immediately withdrawing this one share by specifying the largest `amount` such that the integer rounding still rounds to this one share. They make a small profit. They can repeat this many times in a single transaction with many messages.
Depending on the token price, this can be profitable as [similar attacks show](https://blog.neodyme.io/posts/lending_disclosure).

## Recommended Mitigation Steps
The protocol tries to protect against this attack but the `max(., 1)` is not enough mitigation. There are several ways to fix this:

1. Always round up in `withdraw_share`
2. Always recompute the `withdraw_amount` with the new `withdraw_share` even if the `amount` parameter was set.
3. Use a `share` parameter (instead of the `amount` parameter) and use it as `withdraw_share`. Rounding down on the resulting `withdraw_amount` is bad for the attacker as burning a share leads to fewer tokens.
