# [C] Users can get NFTs for as little as 1 wei Wizzard_audit.md

## Summary
Severity: Critical
Contest weight: 0.3962
Dataset id: 16418
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Inside the WizardNFTMArkeplace token owners can create auctions and users can bid for a specific NFT through the placeBid function.
```solidity
function placeBid(
    uint256 tokenId
) external payable nonReentrant {
    MarketItem storage item = idToMarketItem[collectionAddr][tokenId];
    if (msg.value < item.highestBid) {
        revert BidShouldGreater();
    }
    payable(item.highestBidder).transfer(item.highestBid);
    item.highestBidder = payable(msg.sender);
    item.highestBid = msg.value;
    emit BidPlaced(tokenId, msg.sender, msg.value);
}
```
It can be seen that if a user sends more native tokens, the previous highestBid amount will be refunded to the highestBidder before updating the state variables with the new highestBid and new highestBidder. If the owner of the NFT decides to end an ongoing auction without accepting any bids through endAuction, the highestBid will again be refunded to the highestBidder.
```solidity
function endAuction(
    uint256 tokenId
) external onlyTokenOwner(collectionAddr, tokenId) {
    MarketItem storage item = idToMarketItem[collectionAddr][tokenId];
    if (!item.isOnAuction) {
        revert NotOnAuction();
    }
    payable(item.highestBidder).transfer(item.highestBid);
}
```
However, this push approach can lead to a scenario where a malicious user can buy an NFT for as little as 1 wei or brick the auction. If the bidder is a contract that doesn't have any receive or fallback methods, the transfer call will always fail. Thus, the only possible way to unbrick the auction will be to call acceptBid and send the NFT to the malicious contract.

## Recommendation
Use pull instead of push approach by implementing separate withdraw function that allows outbid users to get their funds back.
