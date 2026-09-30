# [H] `AuctionBurnReserveSkew.getPegDeltaFrequency

## Summary
Severity: High
Contest weight: 0.5943
Dataset id: 1126
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function getPegDeltaFrequency() public view returns (uint256) {
    uint256 initialIndex = 0;
    uint256 index;

    if (count > auctionAverageLookback) {
      initialIndex = count - auctionAverageLookback;
    }

    uint256 total = 0;

    for (uint256 i = initialIndex; i < count; ++i) {
      index = _getIndexOfObservation(i);
      total = total + pegObservations[index];
    }

    return total * 10000 / auctionAverageLookback;
}
```

When `count < auctionAverageLookback`, at L131, it should be `return total * 10000 / count;`. The current implementation will return a smaller value than expected.

The result of `getPegDeltaFrequency()` will be used for calculating `realBurnBudget` for auctions. With the result of `getPegDeltaFrequency()` being inaccurate, can result in an improper amount of excess Liquidity Extension balance to be used at the end of an auction.

I actually think this should be higher severity. This bug could manifest in liquidity extension being depleted to zero which could have catastrophic consequences downstream.

Agree with the finding, this is an incorrect logic in the protocol, which can limit it’s functionality and as the sponsor says: `could have catastrophic consequences downstream` as such I’ll increase the severity to high.

Mitigation seems to be straightforward

## Recommendation
No recommendation
