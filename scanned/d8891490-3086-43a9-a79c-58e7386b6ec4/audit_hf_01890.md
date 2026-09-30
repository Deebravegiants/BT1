# [H] Users can place bets on canceled auctions

## Summary
Severity: High
Contest weight: 0.5519
Dataset id: 10467
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users create auctions and sell off their NFTs. Sellers can also cancel the auction but only if it is before the auction has started. This is achieved via the cancelAuction function and only the auction status is updated to CANCELLED and the NFT is transferred back to the owner. In the bidPlace and resultAuction functions there is no check whether the auction was canceled. That lets users freely bet on canceled auctions and when the time comes to close the auction the transaction will revert because the NFT was sent back to the owner when canceling. The last bidder's funds would get stuck in the contract.

## Recommendation
Delete the auction data in cancelAuction.
```solidity
auctionNfts[_auctionId].status = Status.CANCELLED;
delete auctionNfts[_auctionId];
```
