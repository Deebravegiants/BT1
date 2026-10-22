# [M] ORDM-9 | Average Price of a Position is Miscalculated

## Summary
Severity: Medium
Contest weight: 0.3954
Dataset id: 20557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _increasePosition and _decreasePosition the user’s position is essentially recreated with a modified positionSize and/or positionCollateral. When the position is recreated, the userPosition.avgPrice is set to the updatedAvgPrice, which is based on the deltaSize and calculated as follows.
```solidity
uint256 updatedAvgPrice = _verifyAndUpdatePrice(
    userPosition.marketId, userPosition.isLong, false, OrderDS.OrderType.OPEN_NEW_POSITION,
    userOrder.deltaSize
);
```
When the updatedAvgPrice is calculated, it will include the negative impact from the increase or decrease delta change. Therefore, the remaining position immediately has negative PnL as the avgPrice assigned is automatically worse than market price.

## Recommendation
Calculate the average price so that the updated size is valued at the current price, as this was the price the PnL was settled at.
avgPrice = marketPrice * (sizeRemaining/totalNewSize) + updatedPrice * (sizeDelta/totalNewSize)
