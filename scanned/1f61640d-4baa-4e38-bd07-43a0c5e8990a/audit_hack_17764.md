# [M] Unauthorized order executions.

## Summary
Severity: Medium
Reporter: Upbeat Sand Chicken
Source: https://github.com/sherlock-audit/2023-12-flatmoney/blob/main/flatcoin-v1/src/DelayedOrder.sol#L378-L410
Type: audit-issue

## Details
# Unauthorized order executions.

krkba
## Summary
## Vulnerability Detail
In `executeOrder` function, there is no checks to ensure that the caller of the function is authorized to execute the order.
## Impact
Unauthorized order executions.
## Code Snippet
https://github.com/sherlock-audit/2023-12-flatmoney/blob/main/flatcoin-v1/src/DelayedOrder.sol#L378-L410
## Tool used

Manual Review

## Recommendation
