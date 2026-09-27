# [H] Early-liquidating owners permanently lose part of their deposit

## Summary
Severity: High
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L437
Type: audit-issue

## Details
# Early-liquidating owners permanently lose part of their deposit

## Summary

liquidate() always only liquidates part of a positions shares. The remaining shares can never be liquidated, and the user can never claim any more funds

## Vulnerability Detail

liquidate() always only liquidates at most half of a position's shares. liquidate() sets the is_liquidate flag to True, meaning it can never be called again. When the is_liquidate flag is set to True, claim() cannot claim anything (enforced by https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L437 ).

The result: the user has permanently lost part of their deposit.

## Impact

Users will not get their full deposit back.

Unless stolen by someone else exploiting the contract, these funds will remain locked in the contract forever.

## Code Snippet

This code ensures that shares_to_liquidate is always strictly less than position.shares_owned: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L339.

Not that collaterisation is always at least 2 * DECIMALS.

## Tool used

Manual Review

## Recommendation

Either allow repeated liquidations, or remove the code in `_claimable_for_token` that ensures people with already-liquidated positions cannot claim anythnig.
