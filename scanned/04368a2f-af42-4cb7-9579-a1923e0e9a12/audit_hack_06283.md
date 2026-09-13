# [H] liquidate() causes total_shares to become less than the number of shares controlled by the vault

## Summary
Severity: High
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L336
Type: audit-issue

## Details
# liquidate() causes total_shares to become less than the number of shares controlled by the vault

## Summary

The liquidate() function reduces total_shares by position.shares_owned. However, it only liquidates some of the shares. This causes the withdrawn tokens intended for the liquidated position owner to instead go to other depositors.

## Vulnerability Detail

See summary

## Impact

Other depositors get a portion of the deposits of early liquidators

## Code Snippet

liquidate() subtracts all shares owned by a position from total shares, even though it only liquidates some: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L336

## Tool used

Manual Review

## Recommendation

Only reduce total_shares by the number of shares liquidated.
