# [C] Malicious user can bid the minimum and always win

## Summary
Severity: Critical
Contest weight: 0.2779
Dataset id: 10459
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function bidPlace(
    uint256 _auctionId
) external payable nonReentrant isAuction(_auctionId) {
    require(
        block.timestamp >= auctionNfts[_auctionId].startTime,
        "auction not start"
    );
    require(
        block.timestamp <= auctionNfts[_auctionId].endTime,
        "auction ended"
    );
    require(
        msg.value >= auctionNfts[_auctionId].heighestBid,
        "less than highest bid price"
    );
    require(
        msg.value >= auctionNfts[_auctionId].minBid,
        "less than min bid price"
    );
    AuctionNFT storage auction = auctionNfts[_auctionId];
    // IERC20 payToken = IERC20(auction.payToken);
    uint256 lastBidPrice = auction.heighestBid;
    // Transfer back to last bidder
    payable(lastBidder).transfer(lastBidPrice);
}
```
The bidPlace function allows a user to place a bid on an auction, if the bid is higher than the previous bidder, the previous bidder will receive his ETH back via a transfer. The problem occurs when a malicious user uses a contract to place a bid. The malicious user adds a fallback function that reverts when receiving ether, therefore whenever he bids, no one may bid after him because the call will always revert. This allows the attacker to bid the minimum amount and never be outbid and thus cheat the auction creator out of his deserved funds. Additionally, since the nft will be transferred to him after the auction, he can actually receive the nft with no problem.

## Recommendation
Implement a pull mechanism, where the bidders can withdraw their bids in another function.
