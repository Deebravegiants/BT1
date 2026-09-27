# [H] Lender's can't get back their loans

## Summary
Severity: High
Reporter: 0xdevPed
Source: https://github.com/sherlock-audit/2023-01-cooler/blob/main/src/Cooler.sol#L122
Type: audit-issue

## Details
# Lender's can't get back their loans

## Summary
Lender's can't get back their loans

## Vulnerability Detail
borrowers can't repay their loans due to the use of transferFrom instead of transfer

## Impact
Protocol Malfunction
Loss of lender's funds

## Code Snippet

https://github.com/sherlock-audit/2023-01-cooler/blob/main/src/Cooler.sol#L122
## Tool used

Manual Review

## Recommendation
use transfer
