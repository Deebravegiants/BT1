# [H] User will lose funds if they don't claim before liquidating their token

## Summary
Severity: High
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L430-L440
Type: audit-issue

## Details
# User will lose funds if they don't claim before liquidating their token

## Summary

Once a position has been liquidated the owner can no longer claim any WETH. If the user had unclaimed rewards before liquidating then those funds will be lost forever

## Vulnerability Detail

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L430-L440

After a token is Vault#liquidated _claimable_for_token will always return 0 which will block any future claim for that tokenId. If the token is claimed before being liquidated then all the funds that should be claimable will be permanently trapped in the contract.

## Impact

Unclaimed rewards will be lost when a token is liquidated

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320-L352

## Tool used

Manual Review

## Recommendation

During liquidation, positions should be automatically claimed before withdrawing
