# [H] Auctions can end in epoch after intended,

## Summary
Severity: High
Contest weight: 0.8801
Dataset id: 17719
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When liens are liquidated, the router checks if the auction will complete in a future epoch and, if it does, sets up a liquidation accountant and other logistics to account for it. However, the check for auction completion does not take into account extended auctions, which can therefore end in an unexpected epoch and cause accounting issues, losing user funds. The liquidate() function performs the following check to determine if it should set up the liquidation to be paid out in a future epoch:
```solidity
if (PublicVault(owner).timeToEpochEnd() <= COLLATERAL_TOKEN.auctionWindow())
```
This function assumes that the auction will only end in a future epoch if the auctionWindow (typically set to 2 days) pushes us into the next epoch. 15 minutes. In these cases, auctions are extended repeatedly, up to a maximum of 1 day.
```solidity
if (firstBidTime + duration - block.timestamp < timeBuffer) {
    uint64 newDuration = uint256(
        duration + (block.timestamp + timeBuffer - firstBidTime)
    ).safeCastTo64();
    if (newDuration <= auctions[tokenId].maxDuration) {
        auctions[tokenId].duration = newDuration;
    } else {
        auctions[tokenId].duration =
            auctions[tokenId].maxDuration -
            firstBidTime;
    }
    extended = true;
}
```
The result is that there are auctions for which accounting is set up for them to end in the current epoch, but will actual end in the next epoch. Users who withdrew their funds in the current epoch, who are entitled to a share of the auction's proceeds, will not be paid out fairly.

## Recommendation
Change the check to take the possibility of extension into account:
```solidity
if (PublicVault(owner).timeToEpochEnd() <= COLLATERAL_TOKEN.auctionWindow() + 1 days)
```
