# [M] resultAuction doesn't correctly validate the _nft param

## Summary
Severity: Medium
Contest weight: 0.4274
Dataset id: 10491
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function resultAuction(
    uint256 _auctionId,
    uint256 _tokenId
) external nonReentrant {
    AuctionNFT storage auction = auctionNfts[_auctionId];
    require(!auction.success, "already resulted");
    require(
        msg.sender == owner() ||
        msg.sender == auction.creator ||
        msg.sender == auction.lastBidder,
        "not creator, winner, or owner"
    );
    require(block.timestamp > auction.endTime, "auction not ended");
    IERC721 nft = IERC721(auction.nft);
    auction.success = true;
    auction.winner = auction.creator;
    auction.status = Status.COMPLETED;
    uint256 heighestBid = auction.heighestBid;
    uint256 totalPrice = heighestBid;
    if (!nftSold[_nft][_tokenId]) {
        // If it's an initial sale
        _processInitialSale(totalPrice);
        nftSold[_nft][_tokenId] = true;
    } else {
        // If it's a resale, process royalty
        totalPrice = _processResale(totalPrice);
    }
    payable(auction.creator).transfer(totalPrice);
}
```
the resultAuction function allows a user to buy an nft that was listed for sale, the user will input _nft param
according to the auctionNFT. _nft param value is only used to determine if the sale is the initial sale or a
re-sale.
A user can take advantage of this in order to either only pay the initial sale fee instead of the re-sale fee or
vice versa.

## Recommendation
Correctly validate the _nft param is equal to the auctionNFT nft param.
