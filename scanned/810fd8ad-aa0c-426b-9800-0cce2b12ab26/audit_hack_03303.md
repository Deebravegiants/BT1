# [M] Check Utoken admin_ for nonzero address

## Summary
Severity: Medium
Reporter: nalus
Source: https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/UToken.sol#L244
Type: audit-issue

## Details
# Check Utoken admin_ for nonzero address

## Summary
Should be checked that admin_ in the initializer, isn't equal to address(0) otherwise deployer can lose contract ownership.

## Code Snippet
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/UToken.sol#L244

## Tool used
Me and VS code

## Recommendation
require(admin_  != address(0), "adminCannotBe0");
