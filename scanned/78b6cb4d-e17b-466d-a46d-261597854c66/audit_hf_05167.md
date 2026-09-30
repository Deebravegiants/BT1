# [M] ERC721Bridgable and ERC1155B

## Summary
Severity: Medium
Contest weight: 0.5980
Dataset id: 23235
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the README:
The Bridged721 should be strictly compliant with EIP-721 and EIP-2981 The Bridged1155 should be strictly compliant with EIP-1155 and EIP-2981
EIP-2981 states the following:
Marketplaces that support this standard MUST pay royalties no matter where the sale occurred or in what currency, including on-chain sales, over-the-counter (OTC) sales and off-chain sales such as at auction houses.
As royalty payments are voluntary, entities that respect this EIP must pay no matter where the sale occurred - a sale conducted outside of the blockchain is still a sale.
The crux of the standard, is that if a contract is EIP-2981 compliant, the royalty should be paid to the artist who created the NFT no matter where the sale occurred. For that it first needs to be correctly reported to marketplaces, and attributed to the artist. It's worth noting that as returned by the EIP-2981 function royaltyInfo, both the royalty recipient and the royalty amount are specific to each NFT:
```solidity
function royaltyInfo(uint256 _tokenId, uint256 _salePrice) external view returns (address receiver, uint256 royaltyAmount);
```
The problem is that both ERC721Bridgable and ERC1155Bridgable completely violate this crucial property via both setting a uniform royalty amount across all NFTs, and designating themselves as the royalty recipient, thus reporting wrong amounts, and mixing them together in a single bucket. This makes it impossible to either correctly collect the appropriate royalty amounts, or to attribute the collected royalties to artists.
Both ERC721Bridgable and ERC1155Bridgable perform the following in their initialize function:
```solidity
// Set this contract to receive marketplace royalty
_setDefaultRoyalty(address(this), _royaltyBps);
```
As per-NFT royalties are not set, this makes the contract a single recipient of the same _r happens next, it's impossible to either correctly collect the appropriate royalty amounts at marketplaces, or to correctly attribute the royalties to different artists.
Definite loss of funds (NFT creators won't receive the appropriate royalties):
• Marketplaces who sell NFTs on L2s are not able to pay correct amounts of royalties
• Artists who created the NFTs in collections on L1, which are bridged to L2, are not able to track the amounts of royalties they have the right to receive (which effectively deprives them of said royalties)

## Recommendation
Both for ERC721Bridgable and ERC1155Bridgable have to implement a system which:
• correctly reports per-NFT royalty amounts on L2 via royaltyInfo
• correctly collects the appropriate royalty amounts, and tracks the per-NFT recipients of said amounts on L1.
Notice: this finding concerns only with the absence of the correct tracking and reporting system as per EIP-2981. Royalty distribution system from L2 to L1 is out of scope of this finding.
