# [M] Auction variables can be changed during ongoing auction

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-06
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/13
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Submission hash (on-chain):** 0xcc5e1c8e731fe0c1e9294364b3e83e017e5c40dbeb87a3095cf10dd9fa90e9c5
**Severity:** medium

**Description:**
**Description**\
In `AuctionManager.sol`, The auction variables can be changed anytime by admin and even during ongoing auctions, and these changes take effect immediately during ongoing auction. The whitelisted verified users who want to bid in auction will need to have a sufficient time to react to the sudden changes changes. 


The most important variables of auctions are `whitelistBidAmount`,     `minBidAmount`,`maxBidAmount`. These variables can be changed by admin in case of `minBidAmount` and `maxBidAmount`and contract owner in case of `whitelistBidAmount`


These important variables are used to verify the `_bidAmountPerBid` passed in `createBid()` which can be seen below,

```Solidity
File: src/AuctionManager.sol

    function createBid(
        uint256 _bidSize,
        uint256 _bidAmountPerBid
    ) external payable whenNotPaused nonReentrant returns (uint256[] memory) {
        require(_bidSize > 0, "Bid size is too small");
        if (whitelistEnabled) {
            require(
                nodeOperatorManager.isWhitelisted(msg.sender),
                "Only whitelisted addresses"
            );
            require(
                msg.value == _bidSize * _bidAmountPerBid &&
>>                   _bidAmountPerBid >= whitelistBidAmount &&
>>                    _bidAmountPerBid <= maxBidAmount,
                "Incorrect bid value"
            );
        } else {
            if (
                nodeOperatorManager.isWhitelisted(msg.sender)
            ) {
                require(
                    msg.value == _bidSize * _bidAmountPerBid &&
>>                        _bidAmountPerBid >= whitelistBidAmount &&
>>                        _bidAmountPerBid <= maxBidAmount,
                    "Incorrect bid value"
                );
            } else {
                require(
                    msg.value == _bidSize * _bidAmountPerBid &&
>>                        _bidAmountPerBid >= minBidAmount &&
>>                        _bidAmountPerBid <= maxBidAmount,
                    "Incorrect bid value"
                );
            }
        }


       // some code

```


The major issues impacts can be:

1) some sudden changes to `setMinBidPrice()` and `setMaxBidPrice()` may cause whitelisted users/bidder's transaction to be failed and their bid is not successfully completed and not stored with bidId. Minimum and maximum bid price can be changed to be relatively high later, which forces the users to stop bidding on the auction as they might not have enough funds. If the users knew in advance that the min and max bid prices increase will become large, then the users would not bid on the auction in the first place. Therefore current implementation would cause a big issue to users who want to bid.

2) The sudden changes may change the users expectations and their bidding plans considering the economic conditions.

**Attachments**
Code location:

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/AuctionManager.sol#L314-L325

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/AuctionManager.sol#L111-L132

**Recommendation**
1) Recommend do not apply changes to auction validating variables on ongoing auctions or when creating the auction, it can be stored in the corresponding auction struct. When calling `createBid()`, `minBidAmount ` and `maxBidAmount` could be calculated based on the stored `minBidAmount` and `maxBidAmount` for the respective auction, instead of the changing the `AuctionManager.setMinBidPrice()` and  `AuctionManager.setMaxBidPrice()`values during ongoing auctions.

2) Recommend to add a timelock for the changes in contract by admin.
