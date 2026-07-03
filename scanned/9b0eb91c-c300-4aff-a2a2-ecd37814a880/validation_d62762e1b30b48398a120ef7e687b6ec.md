### Title
Missing Staleness Check on Chainlink Price Feed Allows Stale Asset Prices to Corrupt rsETH Exchange Rate - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` return value, accepting arbitrarily stale Chainlink prices. These prices flow directly into the rsETH/ETH exchange rate calculation, enabling incorrect minting and redemption amounts for all users.

---

### Finding Description

In `ChainlinkPriceOracle.getAssetPrice()`, the Chainlink aggregator's `latestRoundData()` is called and only the `price` field is used; `updatedAt` is never validated: [1](#0-0) 

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt silently dropped
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

This price is consumed by `LRTOracle._getTotalEthInProtocol()`, which aggregates the ETH-denominated value of every supported LST: [2](#0-1) 

```solidity
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // stale price accepted here
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
```

`totalETHInProtocol` is then used to compute `newRsETHPrice`, which is written to the global `rsETHPrice` state variable: [3](#0-2) 

The public `updateRSETHPrice()` function is callable by any address: [4](#0-3) 

This means any unprivileged caller can trigger a price update at any moment, including during a period when a Chainlink feed is stale.

---

### Impact Explanation

If a Chainlink feed for a supported LST (e.g., stETH/ETH, ETHx/ETH) goes stale:

- **Stale price higher than actual**: `totalETHInProtocol` is overstated → `rsETHPrice` is inflated → depositors mint more rsETH than their assets are worth, diluting existing holders. This constitutes direct theft of value from existing rsETH holders.
- **Stale price lower than actual**: `rsETHPrice` is deflated → depositors receive fewer rsETH tokens than deserved, and withdrawers receive less ETH than owed.

Both scenarios represent share/asset mis-accounting that directly harms users. The `pricePercentageLimit` guard only triggers a revert or pause when the *new* price deviates from `highestRsethPrice` by more than the configured threshold; a moderately stale price that has not moved far from the peak will pass this check silently.

**Impact classification**: Medium — temporary freezing of funds / contract fails to deliver promised returns, with potential for Critical (direct theft) if the stale price diverges significantly before the guard triggers.

---

### Likelihood Explanation

Chainlink feeds can go stale during extreme market volatility, network congestion, or Chainlink node outages. The heartbeat for ETH-denominated LST feeds is typically 24 hours, meaning a feed can be up to 24 hours stale before Chainlink's own circuit breaker fires. Because `updateRSETHPrice()` is permissionless, any user — including an attacker — can deliberately call it during a known stale window to lock in the incorrect exchange rate before the feed recovers.

---

### Recommendation

Add a configurable `maxStaleness` parameter and validate `updatedAt` in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
if (block.timestamp - updatedAt > maxStaleness) revert StalePriceFeed();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Set `maxStaleness` per asset to match the Chainlink feed's documented heartbeat plus a small buffer (e.g., heartbeat + 1 hour).

---

### Proof of Concept

1. A Chainlink feed for a supported LST (e.g., stETH/ETH) goes stale — `updatedAt` is 12 hours old while the actual LST price has dropped 5%.
2. An attacker calls `LRTOracle.updateRSETHPrice()` (permissionless).
3. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → `latestRoundData()` returns the stale (inflated) price; no staleness check exists.
4. `totalETHInProtocol` is overstated by ~5% of the stETH TVL.
5. `newRsETHPrice` is set higher than the true value; the `pricePercentageLimit` guard does not trigger if the deviation is within the configured threshold.
6. The attacker (or any user) immediately deposits ETH and mints rsETH at the inflated rate, receiving more rsETH than their deposit is worth.
7. When the feed recovers and `updateRSETHPrice()` is called again, `rsETHPrice` corrects downward, diluting all existing holders. [1](#0-0) [4](#0-3) [5](#0-4) [3](#0-2)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-251)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L331-344)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```
