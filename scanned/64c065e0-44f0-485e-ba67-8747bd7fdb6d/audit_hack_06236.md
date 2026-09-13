# [M] If all operators are removed then the Vault contract will be stuck

## Summary
Severity: Medium
Reporter: weeeh_
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L604-L614
Type: audit-issue

## Details
# If all operators are removed then the Vault contract will be stuck

## Summary
If each operator is removed then the Vault contract will be stuck.

## Vulnerability Detail
On the contract Vault we manage the operators by calling `add_operator` and `remove_operator` functions. Their role is basically to manage the high level aspects of the contract. The issue here is that if all operators are removed then the contract is stuck as there's no way to call several functions of the contract which do require `is_operator[msg.sender]` to be true.

## Impact
The Vault contract is partially stuck as we cannot call functions requiring `is_operator[msg.sender]` to be true.

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L604-L614

## Tool used
vim
Manual Review

## Recommendation
An admin role like the `migration_admin` one should have also permissions to add and remove operators.
