# [M] BondAggregator.findMarketForFunction Will Break

## Summary
Severity: Medium
Contest weight: 0.5959
Dataset id: 17788
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function payoutFor(
    uint256 amount_,
    uint256 id_,
    address referrer_
) public view override returns (uint256) {
    // Calculate the payout for the given amount of tokens
    uint256 fee = amount_.mulDiv(_teller.getFee(referrer_), 1e5);
    uint256 payout = (amount_ - fee).mulDiv(markets[id_].scale, marketPrice(id_));
    
    // Check that the payout is less than or equal to the maximum payout,
    // Revert if not, otherwise return the payout
    if (payout > markets[id_].maxPayout) {
        revert Auctioneer_MaxPayoutExceeded();
    } else {
        return payout;
    }
}
```
The BondAggregator.findMarketFor function will call the BondBaseSDA.payoutFor function within the for-loop. If the computed payout is larger than the markets[id_].maxPayout as mentioned earlier, this will cause the entire for-loop to "break" and the transaction to revert. Assume that the user configures the minAmountOut_ to be 0, then the condition minAmountOut_ <= maxPayout Line 244 will always be true. The amountIn_ will always be passed to the payoutFor function. In some markets where the computed payout is larger than the market's max payout, the BondAggregator.findMarketFor function will revert.
```solidity
function findMarketFor(
    address payout_,
    address quote_,
    uint256 amountIn_,
    uint256 minAmountOut_,
    uint256 maxExpiry_
) external view returns (uint256) {
    uint256[] memory ids = marketsFor(payout_, quote_);
    uint256 len = ids.length;
    uint256[] memory payouts = new uint256[](len);

    uint256 highestOut;
    uint256 id = type(uint256).max; // set to max so an empty set doesn't return 0, the first index
    uint48 vesting;
    uint256 maxPayout;
    IBondAuctioneer auctioneer;
    for (uint256 i; i < len; ++i) {
        auctioneer = marketsToAuctioneers[ids[i]];
        (, , , , vesting, maxPayout) = auctioneer.getMarketInfoForPurchase(ids[i]);

        if (expiry <= maxExpiry_) {
            payouts[i] = minAmountOut_ <= maxPayout
                ? payoutFor(amountIn_, ids[i], address(0))
                : 0;

            if (payouts[i] > highestOut) {
                highestOut = payouts[i];
                id = ids[i];
            }
        }
    }

    return id;
}
```
The find market feature within the protocol is broken under certain conditions. As such, users would not be able to obtain the list of markets that meet their requirements. The market makers affected by this issue will lose the opportunity to sell their bond tokens.

## Recommendation
Consider using try-catch or address.call to handle the revert of the BondBaseSDA.payoutFor function within the for-loop gracefully. This ensures that a single revert of the BondBaseSDA.payoutFor function will not affect the entire for-loop within the BondAggregator.findMarketFor function.
