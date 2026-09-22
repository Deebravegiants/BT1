# [M] 6.2 ERC20 Function Calls Ignore Return Values

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The ERC20 specification states:

```
Callers MUST handle false from returns (bool success). Callers MUST NOT assume that false is never returned!
```
In some calls to the ERC20 tokens those return values are ignored:

- IBurnableMintableERC677Token(_token).mint(address(manager), fee) in
    _distributeFee function.
- IBurnableMintableERC677Token(_token).transfer(address(manager), fee) in
    _distributeFee function.
- IBurnableMintableERC677Token(_bridgedToken).mint(address(this), 1) in
    setCustomTokenAddressPair function.
- _getMinterFor(_token).mint(_recipient, _value) in _releaseTokens function.

In most cases that happens during the calls to non-native Tokens that were deployed via the factory. But
due to the setCustomTokenAddressPair function the non-native contracts can have any behavior
and the return values need to be checked explicitly.

Code corrected:

All calls to transfer and mint function now check the return values.
