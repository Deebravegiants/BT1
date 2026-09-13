# [M] Owner can indefinitely DOS contract by setting fee recipient to bad address

## Summary
Severity: Medium
Reporter: 0x52
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L367-L402
Type: audit-issue

## Details
# Owner can indefinitely DOS contract by setting fee recipient to bad address

## Summary

Owner can DOS contract by setting fee recipient to address that reverts when receiving the fees

## Vulnerability Detail

When assets are withdrawn from the contract, it is mandatory that fees be sent to the fee recipient. If the fee recipient is unable to receive transfers from the collateral token then all functions will revert and withdrawals will become impossible. An example would be if the collateral was USDC and the recipient was set to a blacklisted address.

## Impact

All withdraws become impossible

## Code Snippet

[VaultInternal.sol#L367-L402](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L367-L402)

## Tool used

Manual Review

## Recommendation

Fees should accumulate in the contract rather forcing users to transfer every time. Adjust fee collection methods to increment and internal counter and remove that amount when calculating the total supply. Add another function to collect all accumulated fees when called.
