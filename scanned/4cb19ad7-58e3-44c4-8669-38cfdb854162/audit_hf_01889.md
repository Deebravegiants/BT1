# [H] NFT marked as sold on initial sale can lead to losing funds

## Summary
Severity: High
Contest weight: 0.7520
Dataset id: 10466
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol implements a classic NFT contract with the addition of a marketplace where users could sell and auction off their NFTs. When an NFT is bought (or auction settled) there is a check that verifies if this is a first sale.
```solidity
if (!nftSold[_nft][_tokenId]) {
    // If it's an initial sale
    _processInitialSale(totalPrice);
    nftSold[_nft][_tokenId] = true;
} else {
    // If it's a resale, process royalty
    totalPrice = _processResale(totalPrice);
    payable(auction.creator).transfer(totalPrice);
}
```
Basically, if it is an initial sale, from the protocol, the payment is transferred to the protocol wallets. If it is a re-sale the funds are transferred to the seller's wallet. There are also 10 users who by participating in a raffle have won the chance to buy one of the first 10 GHOST NFTs. This is implemented in the GhostNFTMarketplace::initialSale function. The problem is that on the initial sale the nftSold is NOT updated and when a user sells or auctions off the NFT through the GhostNFTMarketplace the payment would go to the protocol wallets instead of the seller.

## Recommendation
In GhostNFTMarketplace::initialSale update the nftSold mapping to true.
```solidity
nftSold[GhostNFTAddress][_tokenId] = true;
```
