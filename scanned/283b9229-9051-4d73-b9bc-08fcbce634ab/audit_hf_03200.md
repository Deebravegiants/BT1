# [M] BondAggregator.liveMarketsBy eventually will

## Summary
Severity: Medium
Contest weight: 0.4354
Dataset id: 17781
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BondAggregator.liveMarketsBy eventually will revert because of block gas limit l#L259-L280
```solidity
function liveMarketsBy(address owner_) external view returns (uint256[] memory) {
    uint256 count;
    IBondAuctioneer auctioneer;
    for (uint256 i; i < marketCounter; ++i) {
        auctioneer = marketsToAuctioneers[i];
        if (auctioneer.isLive(i) && auctioneer.ownerOf(i) == owner_) {
            ++count;
        }
    }
    uint256[] memory ids = new uint256[](count);
    count = 0;
    for (uint256 i; i < marketCounter; ++i) {
        auctioneer = marketsToAuctioneers[i];
        if (auctioneer.isLive(i) && auctioneer.ownerOf(i) == owner_) {
            ids[count] = i;
            ++count;
        }
    }
    return ids;
}
```
BondAggregator.liveMarketsBy function is looping through all markets and does at least marketCounter amount of external calls (when all markets are not live) and at most 4 * marketCounter external calls (when all markets are live and owner matches). This all consumes a lot of gas, even that is called from view function. And each new market increases loop size. That means that after some time marketsToAuctioneers mapping will be big enough that the gas amount sent for view/pure function will be not enough to retrieve all data (50 million gas according to this). So the function will revert. Also similar problem is with findMarketFor, marketsFor and liveMarketsFor functions. Functions will always revert and whoever depends on it will not be able to get information.

## Recommendation
Remove not active markets or some start and end indices to functions.
