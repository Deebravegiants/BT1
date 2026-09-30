# [C] Revisited Logic of ChronosMarketplace::placeBidWithETH()

## Summary
Severity: Critical
Contest weight: 0.6199
Dataset id: 11819
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ChronosMarketplace contract provides users with a trustless NFT trading market, which supports three kinds of trading modes: Fixed Price, English Auction, and Limit Order. In particular, one entry routine, i.e., placeBidWithETH(), is designed to bid for a given English Auction with ETH. While examining its logic, we observe its current implementation needs to be improved.

To elaborate, we show below the related code snippet of the contract. Inside the placeBidWithETH() routine, we notice payable(auctionInfo.highestBidder).transfer(oldBidPrice) (line 592) is called to refund the ETH to the last bidder. However, it comes to our attention that the auctionInfo.highestBidder is set to the new bidder (i.e., msg.sender, line 588) before, which directly undermines the assumption of the protocol design.
```solidity
function placeBidWithETH(
    uint256 _auctionId
) external payable override nonReentrant whenNotPaused {
    address bidder = msg.sender;
    require(bidPrice > minimumBidPrice, Errors.LOW_BID_PRICE);
    address oldWinner = auctionInfo.highestBidder;
    uint256 oldBidPrice = auctionInfo.highestBidPrice;
    auctionInfo.highestBidder = bidder;
    auctionInfo.highestBidPrice = bidPrice;
    if (oldWinner != address(0)) {
        payable(oldWinner).transfer(oldBidPrice);
    }
    emit PlaceBid(bidder, _auctionId, bidPrice);
}
```
Moreover, we observe it is exposed to potential DoS risks. If the last bidder is a malicious contract, it can always revert the transaction in its receive()/fallback() routine. By doing so, he can win the auction eventually. Note other routines, i.e., cancelListNftForAuction()/finishAuction()/placeBid(), are vulnerable to this DoS attack as well.

## Recommendation
Properly refund the assets to the last bidder and apply a defense mechanism to avoid possible DoS attack.
