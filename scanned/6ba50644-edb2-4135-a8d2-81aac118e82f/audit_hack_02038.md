# [M] 6.3 Incorrect Return Value for mintFresh

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Specification Changed

The mintFresh function that is internally responsible of minting new cTokens, has the following
specification regarding its return value:

```
* @return (uint) the actual mint amount.
```
At the end of the function, it says:

```
return actualMintAmount;
```
However, the actualMintAmount variable contains the amount of underlying tokens used for minting
and not the amount of minted cTokens.

Specification changed:

The specification was changed to match the implementation.
