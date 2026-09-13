# [M] Incorrect chainlink setUp, stale data, no try-catch and no check for max deviations

## Summary
Severity: Medium
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L571-L580
Type: audit-issue

## Details
# Incorrect chainlink setUp, stale data, no try-catch and no check for max deviations

## Summary
Incorrect chainlink setUp, stale data, no try-catch and no check for max deviations

## Vulnerability Detail

I wrapped all chainlink issues common issues in one so it is easier to judge. 

Oracle should be checked and validated more. Checking for round completeness and invalid prices

The try-catch block and the deviation check should be implemented more as a design decision
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L571-L580 otherwise any function that fetches prices from the oracle will be unusable if a call to chainlink fails.

Consider implementing Uniswaps TWAP as a fallback oracle in the `catch` statement

## Impact
Incorrect chainlink setUp

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L571-L580
## Tool used

Manual Review

## Recommendation
Add the following checks to the returned values from chainlink `latestRoundData`

```solidity
 require(updatedAt > 0, "round is incomplete");
 require(answer > 0, "Invalid feed answer");
```

Consider wrapping chainlink also in a try-catch so that if the call to `latestRoundData` fails you have a fallback oracle in place (like tellor, or uni TWAP) to protect against any call to: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L562   failing due to a chainlink error.
