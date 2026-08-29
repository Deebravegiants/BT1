# [?] Protect against passing `i128::MIN` to `abs()` which causes overflow (#2241)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-09-25
Source: https://github.com/FuelLabs/fuel-core/commit/20812f1974dacb4782130c920e86b8676a9b12a9
Type: security-commit

## Details
Protect against passing `i128::MIN` to `abs()` which causes overflow (#2241)

## Linked Issues
Closes https://github.com/FuelLabs/fuel-core/issues/2210

## Description
This PR uses `saturating_abs()` instead of "raw" `abs()` inside the
`da_change()` to prevent overflow on `i128::MIN`.

### Before requesting review
- [X] I have reviewed the code myself

---------

Co-authored-by: Mitchell Turner <james.mitchell.turner@gmail.com>
