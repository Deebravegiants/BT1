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
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/13_
