# [H] 6.18 Wrong TVL Calculation in ERC20RootVault

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Code Corrected

ERC20RootVault._getTvlToken0 calculates the TVL of the Vault denominated in the token at
position 0 of an array of tokens. It iterates over all the tokens in the array, but only ever compares token
with index 0 to token with index 1. It should, however, compare token with index 0 to the token with the
current iteration's index. The function is only used in _calculatePerformanceFees.

```
for (uint256 i = 1; i < tvls.length; i++) {
(uint256[] memory prices, ) = oracle.price(tokens[0], tokens[1], 0x28);
```
Code corrected:

The issue has been resolved as the correct index is now used when querying the price of tokens inside
the loop.
