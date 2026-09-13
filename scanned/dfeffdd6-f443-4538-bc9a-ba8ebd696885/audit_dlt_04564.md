# [M] OWNER CAN SET FEES WITHOUT ANY LIMIT

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/136
Type: sherlock-finding

## Details
Mukund

medium

# OWNER CAN SET FEES WITHOUT ANY LIMIT

## Summary
In `setMinFee` function owner can set fees but there is no limit to how high or low owner can set fees .
## Vulnerability Detail
In `setMinFee` function owner can set fees but there is no limit how high or low owner can set fees which will make user pay high fees.
## Impact
people have to pay high fees
## Code Snippet
https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/OptionsConfig.sol#L37-L40
## Tool used

Manual Review

## Recommendation
set a upper and lower bound
