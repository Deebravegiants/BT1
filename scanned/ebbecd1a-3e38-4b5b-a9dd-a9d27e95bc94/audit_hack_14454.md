# [M] [MED] ERC721 tokens can be forever stuck in a smart contract upon minting

## Summary
Severity: Medium
Reporter: 0xtotem
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L159
Type: audit-issue

## Details
# [MED] ERC721 tokens can be forever stuck in a smart contract upon minting

## Summary

[Source](https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/65)

Usage of `safeMint` for ERC721 is recommended instead of `mint` to ensure that if a contract mint tokens it is able to transfer them, resulting in tokens being stuck forever in the contract.

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L159

## Vulnerability Detail

`safeMint` ensures that the caller (if a smart contract) implements  `onERC721Received` and is able to transfer NFT.

## Impact

## Code Snippet

One way of solving this is to change the `MeritNFT.sol` `mint` function to:

```solidity
    /// @notice Mints an NFT. Can only be called by an address with the minter role and tokenId must be unique
    /// @param _tokenId Id of the token
    /// @param _receiver Address receiving the NFT
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _safeMint(_receiver, _tokenId);
    }
```

It might be a good idea to change `mint` to `safeMint` as well or adapt the documentation.

## Tool used

Manual Review

## Recommendation

Using `safeMint` instead of `mint`.
More information on [OpenZeppelin](https://docs.openzeppelin.com/contracts/2.x/api/token/erc721#ERC721-_safeMint-address-uint256-).
