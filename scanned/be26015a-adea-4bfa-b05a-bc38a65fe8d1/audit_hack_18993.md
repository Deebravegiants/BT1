# [M] Strange setter `setPaused`

## Summary
Severity: Medium
Reporter: Restless Mulberry Manatee
Source: https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/AvailBridge.sol#L110-L116
Type: audit-issue

## Details
# Strange setter `setPaused`

krkba
## Summary
 
## Vulnerability Detail
The `setPaused` function appears to be a setter but doesn't modify any storage variables. Setters are expected to update storage variables to reflect the desired state changes in the contract.
## Impact
The pausing mechanism may not work as expected, and the contract may not respond to the intended state changes.
## Code Snippet
https://github.com/sherlock-audit/2023-12-avail/blob/main/contracts/src/AvailBridge.sol#L110-L116
## Tool used

Manual Review

## Recommendation
Ensure that the `setPaused` function or equivalent functions actually modify storage variables to reflect the desired state changes.
