# [H] 7.1 mapToken() Callable Only by Mappers

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Specification Changed

In FxERC20RootTunnel and FxERC721RootTunnel, the mapToken function is annotated as follows:

```
/**
* @notice Map a token to enable its movement via the PoS Portal, callable only by mappers
* @param rootToken address of token on root chain
*/
function mapToken(address rootToken) public {
```
The function however has no access control, anyone may map a token.

The same function in FxERC1155RootTunnel lacks a function description. It also has no access
control.

Specification changed:

The comment has been changed to:

```
//@notice Map a token to enable its movement via the PoS Portal, callable by anyone
```
