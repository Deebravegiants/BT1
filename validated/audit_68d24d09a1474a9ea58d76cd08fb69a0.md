### Title
Missing Negative Price Validation in Chainlink Oracle Causes Deposit Freeze - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the `int256` Chainlink answer directly to `uint256` without verifying `price > 0`. This is the direct analog of the Plonk verifier's missing range check: both fail to validate that an externally-supplied numeric value falls within the domain required for correct arithmetic before using it in downstream computations.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` retrieves the raw Chainlink answer as `int256` and immediately casts it to `uint256`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no `require(price > 0, ...)` guard. If `price` is zero or negative (a known Chainlink edge case during circuit-breaker events or feed misconfiguration), the two's-complement cast produces a value near `type(uint256).max`. Solidity 0.8 checked arithmetic then causes `uint256(price) * 1e18` to revert with an overflow panic.

This revert propagates through every caller:

1. `LRTOracle.getAssetPrice()` → `LRTOracle._getTotalEthInProtocol()` → `LRTOracle._updateRsETHPrice()` / `LRTOracle.updateRSETHPrice()` — price updates are bricked.
2. `LRTDepositPool.getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)` — every `depositAsset()` and `depositETH()` call reverts. [2](#0-1) [3](#0-2) 

The `updatePriceOracleForValidated` admin helper does perform a sanity check at oracle-registration time, but this check is absent from `updatePriceOracleFor` and, critically, is never re-evaluated at runtime when the feed's answer changes. [4](#0-3) 

### Impact Explanation

All user-facing deposit paths (`depositETH`, `depositAsset`) call `getRsETHAmountToMint`, which calls `getAssetPrice`. A non-positive Chainlink answer causes every deposit to revert, temporarily freezing user funds in the protocol. This matches the **Medium — Temporary freezing of funds** impact tier.

### Likelihood Explanation

Chainlink price feeds for LST/ETH assets can transiently return zero or negative answers during circuit-breaker activations, feed migrations, or aggregator bugs. This is a documented edge case in Chainlink's own security guidance. No privileged action is required from the attacker; the condition arises from the feed itself.

### Recommendation

Add an explicit positivity check immediately after reading the Chainlink answer:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
require(price > 0, "ChainlinkOracle: non-positive price");
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

This mirrors the fix recommended in the Plonk verifier report: validate that the externally-supplied value is within the valid domain before using it in arithmetic.

### Proof of Concept

1. Chainlink feed for a supported LST (e.g., stETH) returns `price = -1` during a circuit-breaker event.
2. `ChainlinkPriceOracle.getAssetPrice(stETH)` executes `uint256(-1) * 1e18`, which overflows and reverts.
3. Any call to `LRTDepositPool.depositAsset(stETH, ...)` or `LRTDepositPool.depositETH(...)` (which internally calls `getRsETHAmountToMint` → `lrtOracle.getAssetPrice`) reverts.
4. `LRTOracle.updateRSETHPrice()` also reverts, preventing any price update.
5. All user deposits are frozen until the admin replaces the oracle or the feed recovers. [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L101-108)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
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
