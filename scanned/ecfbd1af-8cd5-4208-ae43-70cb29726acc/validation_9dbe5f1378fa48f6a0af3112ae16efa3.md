### Title
Missing Chainlink `minAnswer`/`maxAnswer` Circuit Breaker Check Allows Inflated Asset Pricing - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` with no validation against Chainlink's built-in `minAnswer`/`maxAnswer` circuit breaker boundaries, and no check that the returned price is greater than zero. If a supported LST asset crashes below Chainlink's `minAnswer`, the oracle silently returns the clamped floor price, inflating the protocol's computed TVL and rsETH price, enabling an attacker to deposit the devalued asset and extract value from honest rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price and immediately returns it after a decimal normalization, with no sanity checks: [1](#0-0) 

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Two defects are present simultaneously:
1. **No `price <= 0` guard** — a zero or negative answer is cast directly to `uint256`, producing a massive or zero value.
2. **No `minAnswer`/`maxAnswer` guard** — Chainlink aggregators clamp their answer to a pre-configured band. If the real market price falls below `minAnswer`, the feed returns `minAnswer` indefinitely, not the true price.

This result propagates through the full pricing stack:

- `LRTOracle.getAssetPrice()` delegates to `ChainlinkPriceOracle.getAssetPrice()`. [2](#0-1) 

- `_getTotalEthInProtocol()` multiplies each asset's balance by its (potentially clamped) oracle price to compute total ETH in the protocol. [3](#0-2) 

- `_updateRsETHPrice()` divides that inflated total by `rsethSupply` to set `rsETHPrice`. [4](#0-3) 

A secondary instance of the same missing `minAnswer`/`maxAnswer` check exists in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which supplies the ETH/USD rate to pool swap logic: [5](#0-4) 

---

### Impact Explanation

**Critical — Direct theft of user funds.**

When a supported LST asset (e.g., stETH, cbETH, rETH) crashes below Chainlink's `minAnswer`:

1. `_getTotalEthInProtocol()` overvalues the crashed asset, inflating `totalETHInProtocol`.
2. `rsETHPrice` is set above its true backing value.
3. An attacker deposits the near-worthless asset at the oracle's inflated `minAnswer` rate and receives rsETH priced as if the asset were still at `minAnswer`.
4. The attacker redeems rsETH for other assets or ETH, extracting real value from the pool.
5. Remaining rsETH holders are left holding tokens backed by less ETH than the price implies — a direct, permanent loss of funds.

The `pricePercentageLimit` circuit breaker in `_updateRsETHPrice()` only triggers if `pricePercentageLimit > 0` and the new price exceeds the historical peak. If the asset was already at `minAnswer` before the crash event, or if `pricePercentageLimit` is unset (zero), this guard does not fire. [6](#0-5) 

---

### Likelihood Explanation

Chainlink circuit breakers are a known, documented property of every aggregator. The Venus/LUNA incident on BSC is a real precedent. The LRT-rsETH protocol supports multiple LST assets, each with its own Chainlink feed and its own `minAnswer`. Any one of those assets experiencing a severe depeg (as has happened with stETH, LUNA-adjacent tokens, and others) is sufficient to trigger this path. No privileged access is required; any depositor can exploit it the moment the real price falls below `minAnswer`.

---

### Recommendation

In `ChainlinkPriceOracle.getAssetPrice()`, after calling `latestRoundData()`:

1. Revert if `price <= 0`.
2. Query the aggregator's `minAnswer` and `maxAnswer` from the underlying `AggregatorV2V3Interface` and revert (or trigger a fallback oracle) if the returned price equals either boundary.

Apply the same fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()` for the ETH/USD feed.

---

### Proof of Concept

**Setup:** stETH is a supported asset. Its Chainlink feed has `minAnswer = 0.5e18` (0.5 ETH). The real market price of stETH crashes to 0.05 ETH (e.g., a severe slashing event).

**Steps:**

1. Chainlink's stETH/ETH aggregator clamps its answer to `minAnswer = 0.5e18`.
2. `ChainlinkPriceOracle.getAssetPrice(stETH)` returns `0.5e18` — 10× the real price. [7](#0-6) 
3. `_getTotalEthInProtocol()` multiplies the protocol's stETH balance by `0.5e18`, inflating `totalETHInProtocol`. [8](#0-7) 
4. `_updateRsETHPrice()` sets `rsETHPrice` to the inflated value. [4](#0-3) 
5. Attacker calls `LRTDepositPool.depositAsset(stETH, largeAmount)`, receiving rsETH priced at the inflated rate — far more rsETH than the real backing warrants.
6. Attacker redeems rsETH for ETH or other assets, extracting real value. Honest holders are left with under-backed rsETH.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```

**File:** contracts/LRTOracle.sol (L336-344)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```
