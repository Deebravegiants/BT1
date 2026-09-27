# [M] Vault.remove_operator allows to remove last operator

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L603-L614
Type: audit-issue

## Details
# Vault.remove_operator allows to remove last operator

## Summary
Vault.remove_operator allows to remove last operator
## Vulnerability Detail
Vault.remove_operator function is called by operators and allows to remove operator.
The caller can also remove himself, so it's actually possible that no operators will remain and it will be not possible to add new operator. 

This is the problem for the contract as in this case all functions that can be called by operator, can't be called anymore.
## Impact
Operator functions will be blocked.
## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L603-L614
## Tool used

Manual Review

## Recommendation
Do not allow operator to remove himself.
