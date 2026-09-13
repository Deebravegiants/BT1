# [M] USDT, etc. cannot be sent at the time of deposit.

## Summary
Severity: Medium
Reporter: innertia
Source: https://github.com/sherlock-audit/2023-03-teller/blob/main/teller-protocol-v2/packages/contracts/contracts/CollateralManager.sol#L327
Type: audit-issue

## Details
# USDT, etc. cannot be sent at the time of deposit.

## Summary
USDT, etc. cannot be sent at the time of deposit.
## Vulnerability Detail
USDT will fail when invoked because the `transferFrom` function does not have a return value set.
## Impact
Cannot lend or borrow a loan if USDT is set up.
## Code Snippet
https://github.com/sherlock-audit/2023-03-teller/blob/main/teller-protocol-v2/packages/contracts/contracts/CollateralManager.sol#L327
## Tool used

Manual Review

## Recommendation
Use safeTransferFrom
