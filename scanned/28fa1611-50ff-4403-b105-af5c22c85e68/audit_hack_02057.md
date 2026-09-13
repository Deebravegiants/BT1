# [M] 6.12 Possible Overflows

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

Primitive Finance pointed out these issues while the audit was ongoing. They are aware that the following
expressions could overflow:

res.cumulativeRisky += res.reserveRisky * deltaTime;
uint256 reserveRisky = (res.reserveRisky * 1e18) / res.liquidity;

Code corrected

The overflow is avoided by casting the variables to uint256 as follows:

res.cumulativeRisky += uint256(res.reserveRisky) * deltaTime;
delRisky = (delLiquidity * reserve.reserveRisky) / reserve.liquidity;, where
delLiquidity is of type uint256.
