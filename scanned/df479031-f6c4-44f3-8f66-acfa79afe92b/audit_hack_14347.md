# [M] Contract uses `mint` instead of `safeMint`

## Summary
Severity: Medium
Reporter: Musaka
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L158
Type: audit-issue

## Details
# Contract uses `mint` instead of `safeMint`

## Summary
**MeritDutchAuction** should use `safeMint` instead of `mint` to prevent potential issues with NFTs being lost.
## Vulnerability Detail
The current implementation of the [`mint`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L158) function in `MeritDutchAuction.sol` calls `nft.mint()`, which is then forwarded to `MeritNFT.sol` where [`_mint`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63) is finally called.
```jsx
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }
```
Here the NFT is minted without any safety checks. And because some minters (contract) are not able to operate with NTFs (missing receivers) the NTFs minted to them will be lost forever.
[link](https://github.com/sherlock-audit/2023-04-footium-judging#issue-m-7-minting-inconsistencies-on-footiumplayer-and-footiumclub) to a similar issue.
## Impact
Can potentially result in the loss of NFTs. 
## Code Snippet
[`_mint`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63)
## Tool used

Manual Review

## Recommendation
Implement [`safeMint`](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L245-L247) instead of `_mint`
