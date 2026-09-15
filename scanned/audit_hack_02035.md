# [M] 6.4 Broken/Partial ERC165 Support

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The ERC-721 specifies that the ERC-165 interface must be implemented which defines a standard
method to publish and detect what interfaces a smart contract implements.

```
function supportsInterface(bytes4 interfaceID) external view returns (bool);
```
The more derived ERC-721 contracts of Kyber Network do not overwrite this function. Hence, querying
the support of the additionally implemented interfaces through supportsInterface() will return
false.


Code corrected:

The issue has been addressed. Function supportsInterface will return true for the following
interfaces.

- ERC721Enumerable
- IERC721Permit

Thus, they are considered as supported by the contract according to ERC-165.
