# [H] liquidate() and claim_funds() track money to be received separately

## Summary
Severity: High
Reporter: jkoppel
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320
Type: audit-issue

## Details
# liquidate() and claim_funds() track money to be received separately

## Summary

liquidate() and claim_funds() track money to be received separately. Various orderings of calls can result in user obtaining different amounts of WETH ---including more than their fair share

## Vulnerability Detail

1. User gets a deposit in the vault
2. 99.99% of debt in vault becomes available for claim
3. User calls claim(), obtaining 99.99% of their deposit
4. User calls liquidate(), obtaining another 99.99% of their deposit

Note: I am unclear exactly how liquidation in Alchemix is supposed to work. But, however it works, it remains true that calling liquidate() before claim() gives the user a different amount than calling claim() before liquidate(). Either way, seems bad

## Impact

User can get double the amount of money they are owed from the vault

## Code Snippet

liquidate() updates shares_owned and is_liquidated, but does not touch amount_claimed
claim() updates amount_claimed and reads from shares_owned, but does not inspect is_liquidated

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L444

## Tool used

Manual Review

## Recommendation

Only allow users to claim amounts in increments of 1 share. Burn that share upon doing so.
