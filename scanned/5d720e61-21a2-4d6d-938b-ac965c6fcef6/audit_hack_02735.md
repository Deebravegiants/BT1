# [M] M-05 Not using safeTransfer may prevent certain tokens from working

## Summary
Severity: Medium
Reporter: GalloDaSballo
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# M-05 Not using safeTransfer may prevent certain tokens from working

## Summary

Non Standard ERC20, [that have no return value](https://github.com/d-xo/weird-erc20#missing-return-values) on transfer or approve will not work with the codebase.

`function transfer(address, uint256);`

Because the solidity compiler will add a check for a non-zero return and those tokens return 0, the tx will revert.

## Vulnerability Detail

## Impact

Because of the different interface and the extra compiler checks, those tokens will not be compatible with the system

## Code Snippet

## Tool used

Manual Review

## Recommendation

Use safeTransfer to make the code compatible with all ER20s on mainnet
