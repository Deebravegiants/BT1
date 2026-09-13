# [H] Insufficient Role Revocation Mechanism through `MINTER_ROLE` and `URI_SETTER`

## Summary
Severity: High
Reporter: moneyversed
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L45-L55
Type: audit-issue

## Details
# Insufficient Role Revocation Mechanism through `MINTER_ROLE` and `URI_SETTER`

## Summary

The contract system does not include functionality for revoking or transferring roles for the "MINTER_ROLE" and "URI_SETTER" roles. Once these roles are assigned, they cannot be changed, posing a potential security risk.

## Vulnerability Detail

The `MeritNFT` contract employs two roles: "MINTER_ROLE" and "URI_SETTER". The MINTER_ROLE has the power to mint new tokens, while the URI_SETTER can set the base URI for all tokens.

However, there's no mechanism to transfer or revoke these roles once they are set. If the initial address assigned to these roles becomes compromised or is no longer trustworthy, there's no way to alter or revoke these roles. This presents a significant security risk.

This problem is in the "MeritNFT" contract, specifically in the constructor:

```solidity
constructor(
    string memory _name,
    string memory _symbol,
    string memory _baseTokenURI,
    address _uriSetter,
    address _minter
) ERC721(_name, _symbol) {
    baseTokenURI_ = _baseTokenURI;
    _setupRole(URI_SETTER, _uriSetter);
    _setupRole(MINTER_ROLE, _minter);
}
```

## Impact

An account with MINTER_ROLE can mint an unlimited number of tokens, potentially devaluing the token. If the URI_SETTER role is compromised, an attacker could redirect token URIs to misleading or malicious destinations. The inability to revoke or change these roles once they are assigned increases the potential damage that can be done if the keys for these accounts are compromised.

## Code Snippet

In the constructor of the `MeritNFT` contract:

```solidity
constructor(
    string memory _name,
    string memory _symbol,
    string memory _baseTokenURI,
    address _uriSetter,
    address _minter
) ERC721(_name, _symbol) {
    baseTokenURI_ = _baseTokenURI;
    _setupRole(URI_SETTER, _uriSetter);
    _setupRole(MINTER_ROLE, _minter);
}
```

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L45-L55

## Tool used

Manual Review

## Recommendation

Implement a mechanism for transferring or revoking roles to provide a way to recover if the initially assigned address is compromised or needs to be changed. Consider using the OpenZeppelin `AccessControl` contract's `renounceRole` and `transferRole` functions to add this functionality. 

## Proof of Concept

This issue is architectural and doesn't require a specific transaction to reproduce. Instead, it represents a missing feature in the smart contracts that should be addressed to increase the system's overall security.

To verify this issue, check the source code of the `MeritNFT` contract, especially the constructor, and verify that there's no functionality to revoke or transfer the "MINTER_ROLE" and "URI_SETTER" roles.
