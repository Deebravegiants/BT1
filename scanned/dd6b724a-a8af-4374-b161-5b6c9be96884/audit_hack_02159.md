# [M] createBasket re-entrancy

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

pauliax


# Vulnerability details

## Impact
function createBasket in Factory should also be nonReentrant as it interacts with various tokens inside the loop and these tokens may contain callback hooks.

## Recommended Mitigation Steps
Add nonReentrant modifier to the declaration of createBasket.
