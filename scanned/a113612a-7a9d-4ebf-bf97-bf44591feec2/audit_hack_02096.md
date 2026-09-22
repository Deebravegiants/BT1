# [M] 7.1 Failing Function Call

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

The TokenMinter contract implements the function setBridgeContract which should call
tokenContract.setBridgeContract. The setBridgeContract function does not exists in the
ERC677MultiBridgeToken contract. Hence, the function call would fail and the interface definition at
the beginning is incorrect.

Specification changed:

POA Network explains that the TokenMinter contract is used as an intermediate owner contract for the
PermittableToken contract wich represents the STAKE token. To clarify this, comments where added to
the TokenMinter contract.
