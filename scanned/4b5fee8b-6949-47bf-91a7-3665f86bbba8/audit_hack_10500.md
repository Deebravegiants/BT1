# [H] Whoever calls USSD.initialize first becomes the admin of the contracs

## Summary
Severity: High
Reporter: Delvir0
Source: https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L39
Type: audit-issue

## Details
# Whoever calls USSD.initialize first becomes the admin of the contracs

## Summary
Due to the fact that initialize is open, whoever calls it first becomes the admin
## Vulnerability Detail
https://github.com/sherlock-audit/2023-05-USSD/blob/main/ussd-contracts/contracts/USSD.sol#L39
Sets the address of caller to admin, which can be anyone
## Impact
Contract hijack
## Code Snippet
Mentioned above
## Tool used

Manual Review

## Recommendation
Implement AC
