# [M] Use `_safeMint` function instead of `_mint`

## Summary
Severity: Medium
Reporter: sorrynotsorry
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
Type: audit-issue

## Details
# Use `_safeMint` function instead of `_mint`

## Summary
Use `_safeMint` function instead of `_mint`
## Vulnerability Detail
The MeritNFT contract uses _mint function to mint the users their assets.
OpenZeppelin recommends the usage of `_safeMint` instead of `_mint`. If the recipient of the NFT is a contract, `_safeMint` checks whether they can handle ERC721 tokens.
## Impact
Loss of NFT
## Code Snippet

```solidity
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }
```
[Link](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63)
## Tool used

Manual Review

## Recommendation
Use `_safeMint` function instead of `_mint`
