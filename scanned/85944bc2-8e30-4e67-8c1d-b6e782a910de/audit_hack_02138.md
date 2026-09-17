# [H] [Pool] - Anyone can remove liquidity from Pools, allowing them to alter the price

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Handle

a_delamo


# Vulnerability details

## Impact

On the `Pool.sol`, the function `removeForMember` is public. Allowing anyone to call the method using an address of an LP in order to remove liquidity from the pools and return to the LP account.

If we combine the ability to remove liquidity and being able to do flash loans, we can alter prices and extract value from the remaining LPs.
