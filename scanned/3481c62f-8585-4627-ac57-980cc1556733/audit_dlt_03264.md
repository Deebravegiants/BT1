# [M] The Asset.lotPrice doubles the oracle timeout in the worst case

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/24
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/Asset.sol#L139-L145


# Vulnerability details

When the `tryPrice()` function revert, for example oracle timeout, the `Asset.lotPrice` will use a decayed historical value:
```solidity
uint48 delta = uint48(block.timestamp) - lastSave; // {s}
if (delta <= oracleTimeout) {
    lotLow = savedLowPrice;
    lotHigh = savedHighPrice;
} else if (delta >= oracleTimeout + priceTimeout) {
    return (0, 0); // no price after full timeout
} else {
```

And the delta time is from the last price saved time. If the delta time is greater than oracle timeout,  historical price starts decaying. 

But the last price might be saved at the last second of the last oracle timeout period. So the `Asset.lotPrice` will double the oracle timeout in the worst case.

## Impact
The `Asset.lotPrice` will double the oracle timeout in the worst case. When the rewards need to be sold or basket is rebalancing, if the price oracle is offline temporarily, the `Asset.lotPrice` will use the last saved price in max two oracle timeout before the historical value starts to decay. It increases the sale/buy price of the asset.

## Proof of Concept
The `lastSave` is updated in the `refresh()` function, and it's set to the current `block.timestamp` instead of the `updateTime` from the chainlink feed:
```solidity
function refresh() public virtual override {
    try this.tryPrice() returns (uint192 low, uint192 high, uint192) {
        if (high < FIX_MAX) {
            savedLowPrice = low;
            savedHighPrice = high;
            lastSave = uint48(block.timestamp);
```
But in the `OracleLib`, the oracle time is checked for the delta time of `block.timestamp - updateTime`:
```
uint48 secondsSince = uint48(block.timestamp - updateTime);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/24_
