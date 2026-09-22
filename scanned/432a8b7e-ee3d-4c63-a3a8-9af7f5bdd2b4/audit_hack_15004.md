# [M] the Loan_To_Collateral is hardcoded to 3000Dai/gOHM

## Summary
Severity: Medium
Reporter: Amusing Myrtle Weasel
Source: https://github.com/sherlock-audit/2023-08-cooler/blob/main/Cooler/src/Clearinghouse.sol#L55
Type: audit-issue

## Details
# the Loan_To_Collateral is hardcoded to 3000Dai/gOHM
## Summary
the Loan_To_Collateral is hardcoded to 3000Dai/gOHM
## Vulnerability Detail
It should take the price from oracle, because the price is stale.
## Impact
Miss calculatins, loss of funds
## Code Snippet
https://github.com/sherlock-audit/2023-08-cooler/blob/main/Cooler/src/Clearinghouse.sol#L55
## Tool used

Manual Review

## Recommendation
Take the price from oracle
