# [?] Remove ignore RUSTSEC-2024-0336 (#2384)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-10-23
Source: https://github.com/FuelLabs/fuel-core/commit/481d4bb12187ddc769eecfbb064e496fa1dcd97b
Type: security-commit

## Details
Remove ignore RUSTSEC-2024-0336 (#2384)

## Linked Issues/PRs
Resolves https://github.com/FuelLabs/fuel-core/issues/1843

## Description
This has been fixed in https://github.com/FuelLabs/fuel-core/pull/1954.
Verified it by running cargo audit on my own did had this warning.

Co-authored-by: Green Baneling <XgreenX9999@gmail.com>
