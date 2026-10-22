# [H] Claimable amount calculation is incorrect

## Summary
Severity: High
Reporter: hickuphh3
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L430-L440
Type: audit-issue

## Details
# Claimable amount calculation is incorrect

## Summary
The claimable amount is incorrectly calculated.

## Vulnerability Detail
The amount claimable `_claimable_for_token` for a token is
```vyper
total_claimable_for_position: uint256 = position.shares_owned * self.amount_claimable_per_share / PRECISION
return total_claimable_for_position - position.amount_claimed
```
but `amount_claimable_per_share` is a global variable that increments upon every invocation of `withdraw_underlying_to_claim()`.

This means that a deposit would immediately have `amount_claimable_per_share` * `shares_owned` claimable amount.

## POC
1) Alice deposits 1 ETH, gets 100 shares.
2) Loan is repaid, incrementing `amount_claimable_per_share` to, say, 100.
3) Bob deposits 5 ETH, gets 500 shares, but his amount claimable would be 500 shares * 100 = 50_000.

## Impact
Claims can be stolen because deposits have incorrect claimable amounts.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L430-L440

## Tool used
Manual Review

## Recommendation
Similar to most reward distribution mechanisms, there should be a `amount_claimable_per_share` tracker per position that is initialised and updated upon every user action.
