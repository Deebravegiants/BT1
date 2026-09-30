# [M] Users can list NFT from other collections if they own ghost NFT

## Summary
Severity: Medium
Contest weight: 0.4052
Dataset id: 10487
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users list their NFTs for sale
```solidity
function listNft(
    uint256 _tokenId,
    uint256 _price
) external
    isPayableToken(_payToken)
    onlyMintedByGhostNFTContract(_tokenId)
    nonReentrant
{
    IERC721 nft = IERC721(_nft);
    // ...
}
```
As per the comment, there would be a few NFT collections that could be listed for sale, the first one being
the Ghost one. The problem with the current listing function is that a user can list an NFT from any other
collection for sale as long as he has an NFT from the GHOST collection with the same id and has approved
it to the marketplace contract.
onlyMintedByGhostNFTContract modifier it is only checked if the user has allowed the marketplace
contract to operate with the NFT in mind. That way a user can just own a GHOST NFT with some id and
_tokenId. The NFT from the fake collection would be transferred to the marketplace contract and up for
sale.

## Recommendation
Verify that the NFT being listed is from an approved collection and not just that the user owns a token with the same ID from the Ghost collection.
