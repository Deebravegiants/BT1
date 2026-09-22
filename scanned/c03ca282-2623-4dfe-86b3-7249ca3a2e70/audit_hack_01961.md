# [C] 6.4 Missing Access Control in UniV3Oracle

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

The function addUniV3Pools populates the mapping poolsIndex with the address of a Uniswap pool
for a pair of tokens. The function should be accessible only to trusted accounts, however, it does not
implement any access restriction. As the function is external anyone can set arbitrary addresses as
Uniswap pools, hence freely manipulate the oracle prices.

Code corrected:

The updated code resolves the issue by restricting the access to the function addUniV3Pools only to
the admin, hence preventing malicious users from setting arbitrary addresses as Uniswap pools:

```
function addUniV3Pools(IUniswapV3Pool[] memory pools) external {
_requireAdmin();
_addUniV3Pools(pools);
}
```
