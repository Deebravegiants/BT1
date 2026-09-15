# [?] Fix for the race condition with tx status and receipts (#1658)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-02-12
Source: https://github.com/FuelLabs/fuel-core/commit/b7e1c6ece6cafb3c64ca41b6e0c966ee67bca46f
Type: security-commit

## Details
Fix for the race condition with tx status and receipts (#1658)

Example of the failed CI
https://github.com/FuelLabs/fuel-core/actions/runs/7865306004/job/21471566710?pr=1656

The change moves receipts into the `TransationStatus` to avoid requests
to the database. The `TxPool` directly listens for blocks and
transaction statuses to notify the user via subscription. But when it
notifies the users, the off-chain database can still be outdated,
leading to empty receipts.

This PR fixes the race condition for the receipts. However, the problem
still exists for the end user if they want to fetch some updated
information from the off-chain database. I created a separate issue to
track it: https://github.com/FuelLabs/fuel-core/issues/1659.

It is the fix for the https://github.com/FuelLabs/fuel-core/pull/1656
