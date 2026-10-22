# [H] Users with claimable funds may lose them if they liquidate their own loan

## Summary
Severity: High
Reporter: 0xlmanini
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404
Type: audit-issue

## Details
# Users with claimable funds may lose them if they liquidate their own loan

## Summary

Issue found at: Vault.vy#liquidate(), Vault.vy#withdraw_underlying_to_claim() and Vault.vy#_claimable_for_token().

## Vulnerability Detail

If users were to leave claimable funds within the Vault and call liquidate() without first claiming such funds, they won't be able to claim them afterwards: Vault.vy#_claimable_for_token() will return 0 as the position for such token id has been liquidated.

## Impact

Permament loss of rewards, as no logic for rescueing the stray funds is implemented.

## Code Snippet

[withdraw_underlying_to_claim()](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394-L404)
[liquidate()](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320-L352)
[_claimable_for_token()](https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L430-L440)
## Tool used

Manual Review

## Recommendation

Consider pushing claimable funds to a token_owner within the liquidate() function so as to not leave them in the contract, or fuse togethre withdrawal and claim flows
