# [H] function accruePrimeInterest

## Summary
Severity: High
Reporter: jefestar
Source: https://github.com/sherlock-audit/2023-03-notional/blob/main/contracts-v2/contracts/external/CalculationViews.sol#L517-L522
Type: audit-issue

## Details
# function accruePrimeInterest

## Summary
function accruePrimeInterest(uint16 currencyId)
## Vulnerability Detail
The contract contains multiple state update calls without the usage of a reentrancy guard.
## Impact
high - Reentrancy

## Code Snippet
https://github.com/sherlock-audit/2023-03-notional/blob/main/contracts-v2/contracts/external/CalculationViews.sol#L517-L522
## Tool used

Manual Review

## Recommendation
Add a reentrancy guard (using a mutex) to restrict reentrant calls.
