# [M] `AuctionLoanLiquidator#placeBid` can be DoS

## Summary
Severity: Medium
Contest weight: 0.5972
Dataset id: 21168
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function placeBid(address _nftAddress, uint256 _tokenId, Auction memory _auction, uint256 _bid)
        external
        nonReentrant
        returns (Auction memory)
    {
        _placeBidChecks(_nftAddress, _tokenId, _auction, _bid);

        uint256 currentHighestBid = _auction.highestBid;
        // MIN_INCREMENT_BPS = 10000, _BPS = 500 , add 5%
        if (_bid == 0 || (currentHighestBid.mulDivDown(_BPS + MIN_INCREMENT_BPS, _BPS) >= _bid)) {
            revert MinBidError(_bid);
        }

        uint256 currentTime = block.timestamp;
        uint96 expiration = _auction.startTime + _auction.duration;
        uint96 withMargin = _auction.lastBidTime + _MIN_NO_ACTION_MARGIN;
        uint96 max = withMargin > expiration ? withMargin : expiration;
        if (max < currentTime && currentHighestBid > 0) {
            revert AuctionOverError(max);
        }
        .....
    }
```

The attacker performs a DoS attack on the `Bid` function, causing other users to be unable to participate and eventually obtaining the NFT at a low price.

## Proof of Concept
The `placeBid` function requires each bid to increase by 5% from the original, locking in for a period of time after each bid.

The problem here is that if the initial price increases from a very small value, the second increase in percentage only needs to be a very small amount. For example: 100 wei -> 105 wei -> 110 wei.

So an attacker can start with a small bid and keep growing slowly. Because of the time lock, other users cannot participate for a period of time. Normal users must wait until the time lock is over and the transaction needs to be executed before the attacker.

If normal users are unable to participate in the bidding, the attacker can obtain the auction item (NFT) at a very low price.

## Recommendation
```solidity
function placeBid(.....){
    require (_bid > MIN_BID);
}
```
