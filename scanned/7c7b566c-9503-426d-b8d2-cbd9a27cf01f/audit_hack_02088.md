# [M] 6.1 ERC721 Use of Unsafe Methods

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The ERC721 standard focuses on ensuring that token transfers do not lock / loose tokens. That is why
the use of "safe" functions such as safeTransferFrom was introduced. This applies not only to
transfers, but to minting as well. However, the implementation of mintAndTransfer in the contract
ERC721Lazy does not use the "safe" _safeMint but the _mint function, whose use is discouraged.

Code corrected:

Function mintAndTransfer now uses _safeMint function.
