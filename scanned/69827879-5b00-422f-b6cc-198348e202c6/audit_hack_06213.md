# [H] User loses rewards when call liquidate as claim function is not called for him

## Summary
Severity: High
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L334
Type: audit-issue

## Details
# User loses rewards when call liquidate as claim function is not called for him

## Summary
User loses rewards when call liquidate as claim function is not called for him
## Vulnerability Detail
When user calls `Vault.liquidate`, then his position is [marked as liquidated](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L334), which means that he [can't call claim anymore](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L334) as function will always return 0 for this position.

`Vault.liquidate` doesn't call `claim` for the position before it set `position.is_liquidated` to true, as result user loses funds.
## Impact
Lose of funds for user who liquidates position.
## Code Snippet
Provided above
## Tool used

Manual Review

## Recommendation
Call `claim` before liquidation for the position.
