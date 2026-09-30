# [M] Improved Validation of Unclaimed List in claimAuctionBid()

## Summary
Severity: Medium
Contest weight: 0.4552
Dataset id: 12498
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the MantisSwap protocol, the Marketplace contract provides a platform where users can list a part of their deposit of MNT and veMNT in the veMNT contact for sell. The owner can specify the price for the list or specify the start price if the list is an auction. In the case of an auction, the bid winner can claim the list by calling the claimAuctionBid() routine after the auction end time. In the following, we show below the code snippet of the claimAuctionBid() routine. Specifically, it transfers the required tokens to the seller and the fee to the treasury, and move the MNT/veMNT in the list to the bidder. At last, it marks the listings[seller][lid].sold = true (line 230) which indicates the list is sold. However, while examining the validation of the list at the beginning of the claimAuctionBid() routine, we notice there is a lack of validation for the list state. As a result, a sold list can be claimed more than once.
```solidity
function claimAuctionBid(address seller, uint256 lid) external whenNotPaused nonReentrant {
    Listing memory listing = listings[seller][lid];
    require(block.timestamp >= listing.endTime, "Auction not over");
    Bid memory bid = bids[seller][lid];
    address bidder = bid.bidder;
    require(bidder != address(0), "No bids found");
    address token = bid.token;
    uint256 tokenAmount = (bid.amount * (10 ** IERC20(token).decimals())) / 1e6;
    uint256 feeAmount = tokenAmount * exchangeFees / 1e4;
    uint256 sellerAmount = tokenAmount - feeAmount;
    Public
    IERC20(token).safeTransfer(seller, sellerAmount);
    IERC20(token).safeTransfer(treasury, feeAmount);
    mntLp.approve(address(veMnt), listing.mntLpAmount);
    require(veMnt.exchangeVeMnt(seller, bidder, listing.mntLpAmount, listing.veMntAmount, listing.veMntRate), "Error");
    listings[seller][lid].sold = true;
    emit Bought(seller, lid, bidder, token, bid.amount);
}
```

## Recommendation
Properly validate the state of the list at the beginning of the claimAuctionBid() routine.
