# [H] There are a couple of potential vulnerabilities in liquidate function

## Summary
Severity: High
Reporter: OCC
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320
Type: audit-issue

## Details
# There are a couple of potential vulnerabilities in liquidate function

## Summary
`liquidate` function did not check if the user's token balance was sufficient and valid to cover the `_token_id` being passed in as an argument, it also did not check if `shares_owned` was greater than zero before attempting to liquidate. For these why, it may result in reentrancy attack. 

## Vulnerability Detail

1.
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L320
There are no checking for the user's token balance is sufficient or insufficient, valid or invalid to cover the `_token_id` being passed in as an argument.  

If someone can create fake token and trick the contract into believing that he/she own it, then call the liquidate function with an invalid `_token_id`, causing the contract to try to liquidate a position that doesn't exist, leading to an error and the execution of the attacker's fallback function, allowing them to execute further code and potentially steal funds.

2.
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L336

This code also does not check if the `position.shares_owned` is greater than zero before attempting to liquidate it.

## Impact
High

## Code Snippet
Manually review

## Tool used
Manually review

### Manual Review
Done

## Recommendation

1. Add proper checker if the token exists and valid 

2. Add checker if shares_owned is greater than zero

The above checkers must be execute before proceeding with the liquidation.
