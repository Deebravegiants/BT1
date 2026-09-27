# [M] `MeritNFT` does not set up `DEFAULT_ADMIN_ROLE`

## Summary
Severity: Medium
Reporter: AkshaySrivastav
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L45-L55
Type: audit-issue

## Details
# `MeritNFT` does not set up `DEFAULT_ADMIN_ROLE`

## Summary
The `DEFAULT_ADMIN_ROLE` is not set up in `MeritNFT` contract which can make various features and functions unusable.


## Vulnerability Detail
The `MeritNFT` contract inherits `AccessControl` contract in which only `DEFAULT_ADMIN_ROLE` has the ability to call `grantRole` and `revokeRole` functions. Since the role is never granted to any address, it becomes impossible to grant roles to new addresses and revoke roles of existing addresses.

This leads to the following outcomes:
- `URI_SETTER` role cannot be granted or revoked.
    `_uriSetter` address cannot be changed after deployment. If the existing `_uriSetter` account gets compromised then there will be no way to revoke the `URI_SETTER` role from the compromised account and grant the role to a new safe account.

- With the presence of `renounceRole` function, existing accounts with any granted role can renounce their roles. Further, as already explained, those renounced roles cannot be given to a new account leaving the respective role's list empty.

Note, the issue impacts the `MINTER_ROLE` similarly but it was assumed that only `MeritDutchAuction` will be granted the minter role, so there is no real need to grant or revoke this role after initialization. If that is not the case and minter role also needs to be given to multiple addresses, for eg, if multiple auction contract can be created for a single NFT, then this bug will also prevent minter role to be granted or revoked after initialization.

POC:
This test case was added to `MeritNFT.t.sol`.
```solidity
    function test_audit_scenario() public {
        assertEq(nft.getRoleMemberCount(nft.URI_SETTER()), 1);
        assertEq(nft.getRoleMemberCount(nft.DEFAULT_ADMIN_ROLE()), 0);
    }
```

## Impact
The `grantRole` and `revokeRole` functions becomes unusable leading to unintended scenarios (already explained above).

## Code Snippet
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
Consider setting up the `DEFAULT_ADMIN_ROLE` in the constructor of `MeritNFT` contract for an account.
