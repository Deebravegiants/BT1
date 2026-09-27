# [M] If the mint address is a smart contract, it can cause the NFT to become stuck, resulting in losses for the users.

## Summary
Severity: Medium
Reporter: ziyou-
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158
Type: audit-issue

## Details
# If the mint address is a smart contract, it can cause the NFT to become stuck, resulting in losses for the users.

## Summary
If the mint address is a smart contract, it can cause the NFT to become stuck, resulting in losses for the users.

## Vulnerability Detail
If the mint is done by a contract that does not have the capability to handle ERC721 tokens, it will get stuck and the user will lose the NFT.

## Impact
If the mint is done by a contract that does not have the capability to handle ERC721 tokens, it will get stuck and the user will lose the NFT.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158
 nft.mint(mintedBefore + i + 1, msg.sender);

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
    function mint(uint256 _tokenId, address _receiver) external onlyMinter {
        _mint(_receiver, _tokenId);
    }

## Tool used

Manual Review

## Recommendation
use _safeMint.
