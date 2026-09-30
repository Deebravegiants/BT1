# [M] Trades in blocks where the bid or ask drops to zero use outdated prices

## Summary
Severity: Medium
Contest weight: 0.4371
Dataset id: 19855
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The oracle prices used for trades allow multiple oracles and their last prices to be provided. The oldest block's price becomes the primary price, and the newer price becomes the secondary price. Trades in blocks where the primary price is non-zero, but the secondary price is zero, will be priced incorrectly.

For position increase/decrease orders, the price used is either the primary or the secondary price, but a value of zero for the secondary price is considered to be a sentinel value indicating ’empty’, or 'no price has been set'. In such cases, the secondary price is ignored, and the primary price is used instead.

Users exiting their positions in the first block where the price touches zero, are able to exit their positions at the primary (older) price rather than the secondary (newer) price of zero. This is pricing difference is at the expense of the pool and the other side of the trade.

The secondary price is only used when it's non-zero:
```solidity
// File: gmx-synthetics/contracts/oracle/Oracle.sol : Oracle.getLatestPrice()
function getLatestPrice(address token) external view returns (Price.Props memory) {
    if (token == address(0)) { return Price.Props(0, 0); }
    Price.Props memory secondaryPrice = secondaryPrices[token];
    if (!secondaryPrice.isEmpty()) {
        return secondaryPrice;
    }
    Price.Props memory primaryPrice = primaryPrices[token];
    if (!primaryPrice.isEmpty()) {
        return primaryPrice;
    }
    revert OracleUtils.EmptyLatestPrice(token);
}
```
cts/oracle/Oracle.sol#L341-L356

## Recommendation
Use an actual sentinel flag rather than overloading the meaning of a 'zero' price.
