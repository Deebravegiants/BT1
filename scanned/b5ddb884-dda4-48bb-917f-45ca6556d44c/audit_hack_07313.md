# [M] OlympusTreasury::repayDebt should have onlyWhileActive

## Summary
Severity: Medium
Reporter: Met
Source: https://github.com/sherlock-audit/2023-02-olympus/blob/main/src/modules/TRSRY/OlympusTreasury.sol#L125-L129
Type: audit-issue

## Details
# OlympusTreasury::repayDebt should have onlyWhileActive

## Summary
As per audit instructions, deactivating a contract should prevent deposits. But OlympusTreasury::repayDebt is missing the onlyWhileActive decorator, therefore deposits (repayments) remain possible even if the contract is deactivated.
## Vulnerability Detail

## Impact

## Code Snippet
https://github.com/sherlock-audit/2023-02-olympus/blob/main/src/modules/TRSRY/OlympusTreasury.sol#L125-L129
## Tool used

Manual Review

## Recommendation
Add the onlyWhileActive  decorator.
