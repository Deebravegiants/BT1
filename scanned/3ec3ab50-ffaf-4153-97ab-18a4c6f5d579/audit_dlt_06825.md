# [M] AuctionLoanLiquidator#placeBid can be DoS

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-gondi
Published: 2024-04-16
Source: https://github.com/code-423n4/2024-04-gondi-findings/issues/37
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-gondi/blob/b9863d73c08fcdd2337dc80a8b5e0917e18b036c/src/lib/AuctionLoanLiquidator.sol#L222


# Vulnerability details

## Impact
The attacker performs a DoS attack on the `Bid` function, causing other users to be unable to participate and eventually obtaining the NFT at a low price.

## Proof of Concept

The placeBid function requires each bid to increase by 5% from the original, locking in for a period of time after each bid.

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
@>      uint96 withMargin = _auction.lastBidTime + _MIN_NO_ACTION_MARGIN;
        uint96 max = withMargin > expiration ? withMargin : expiration;
        if (max < currentTime && currentHighestBid > 0) {
            revert AuctionOverError(max);
        }
        .....
    }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-gondi-findings/issues/37_
