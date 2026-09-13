# [M] wrong subtraction

## Summary
Severity: Medium
Reporter: Short Cherry Koala
Source: https://github.com/sherlock-audit/2024-01-looksrare/blob/main/contracts-yolo/contracts/YoloV2.sol#L524
Type: audit-issue

## Details
# wrong subtraction

## Summary
we should verify that protocolFeeOwed is greater than the msg.value.
## Vulnerability Detail
 protocolFeeOwed -= msg.value;

## Impact

## Code Snippet
https://github.com/sherlock-audit/2024-01-looksrare/blob/main/contracts-yolo/contracts/YoloV2.sol#L524
## Tool used

Manual Review

## Recommendation
use a require statement to verify.
