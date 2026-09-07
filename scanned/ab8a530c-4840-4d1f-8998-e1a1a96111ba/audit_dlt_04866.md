# [H] `ERC1155NFTProduct` does not support full functionality of `ERC1155`

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-nftport
Published: 2022-10-31
Source: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/88
Type: sherlock-finding

## Details
GimelSec

high

# `ERC1155NFTProduct` does not support full functionality of `ERC1155`

## Summary

By design `ERC1155` is a combination of `ERC721` and `ERC20`. Its ability to supply > 1 token for a specific token index also allows support for fragmentation of NFTs. However, the current implementation of `ERC1155NFTProduct` disallows minting of a specific token index once it has been created. This handicaps the cross-chain NFT transfer functionality for fragmented NFTs.

## Vulnerability Detail

In `ERC1155NFTProduct`, both `mintByOwner` and `mintByOwnerBatch` checks the existence of target token id before minting. If token id already exists, minting is disallowed.

```solidity
    function mintByOwner(
        address account,
        uint256 id,
        uint256 amount,
        string memory tokenUri
    ) public onlyRole(MINT_ROLE) {
        require(!_exists(id), "NFT: token already minted");
        if (bytes(tokenUri).length > 0) {
            _tokenURIs[id] = tokenUri;
            emit URI(tokenUri, id);
        }
        _mint(account, id, amount, "");
        tokenSupply[id] += amount;
    }

    function mintByOwnerBatch(
        address[] memory to,
        uint256[] memory ids,
        uint256[] memory amounts,
        string[] memory uris
    ) public onlyRole(MINT_ROLE) {
        for (uint256 i = 0; i < ids.length; i++) {
            require(!_exists(ids[i]), "One of tokens is already minted");
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-nftport-judging/issues/88_
