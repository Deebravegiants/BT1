# [M] `UPDATE_CONTRACT_ROLE` Unable To Revoke NFT Port Permissions (721)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/96
Type: sherlock-finding

## Details
0x0

high

# `UPDATE_CONTRACT_ROLE` Unable To Revoke NFT Port Permissions (721)

## Summary

It's not possible to revoke NFT Port Permissions with an account holding solely `UPDATE_CONTRACT_ROLE`.

## Vulnerability Detail

[`ERC721NFTProduct.update`](https://github.com/sherlock-audit/2022-10-nftport/blob/main/evm-minting-master/contracts/templates/ERC721NFTProduct.sol#L186)

The docstring for `ERC721NFTProduct.update` states that accounts with either roles `UPDATE_CONTRACT_ROLE` or `ADMIN_ROLE` should be able to update configuration items. The implementation does not reflect this as `GranularRoles.revokeNFTPortPermissions` requires `msg.sender` to additionally have `ADMIN_ROLE`.

## Impact

- Accounts holding `UPDATE_CONTRACT_ROLE` are unable to revoke NFT Port Permissions

## Code Snippet

```solidity
function update(
    Config.Runtime calldata newConfig,
    RolesAddresses[] memory rolesAddresses,
    bool isRevokeNFTPortPermissions
) public onlyRole(UPDATE_CONTRACT_ROLE) {
    // If metadata is frozen, baseURI cannot be updated
    require(
        metadataUpdatable ||
            (keccak256(abi.encodePacked(newConfig.baseURI)) ==
                keccak256(abi.encodePacked(baseURI))),
        "Update: Metadata is frozen"
    );

    baseURI = newConfig.baseURI;
    royaltiesAddress = newConfig.royaltiesAddress;
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/96_
