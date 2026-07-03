### Title
Stale Chainlink Price Accepted Without Validation in `ChainlinkPriceOracle.getAssetPrice()` Causes Incorrect rsETH Minting — (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all validation fields (`updatedAt`, `answeredInRound`, `roundId`), accepting stale or invalid prices without any check. This stale price propagates directly into `LRTDepositPool.getRsETHAmountToMint()`, causing depositors to receive incorrect amounts of rsETH — over-minting dilutes existing holders (theft of yield), under-minting harms depositors.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the LST/ETH exchange rate from a Chainlink feed:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

All five return values of `latestRoundData()` are available — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — but only `price` is read. There is no check for:
- **Staleness**: no `block.timestamp - updatedAt > heartbeat` guard
- **Incomplete round**: no `updatedAt == 0` guard
- **Stale round**: no `answeredInRound < roundId` guard
- **Non-positive price**: no `price <= 0` guard

This is in direct contrast to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which the same codebase ships and which does validate `answeredInRound < roundID` and `timestamp == 0`, demonstrating the protocol is aware of these checks but failed to apply them in the core oracle used for deposits.

The stale price flows into the core minting formula in `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` delegates to `ChainlinkPriceOracle.getAssetPrice()`, which returns the unvalidated stale price. This value directly determines how many rsETH tokens are minted to the depositor.

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield / share mis-accounting**

If a Chainlink LST/ETH feed (e.g., stETH/ETH, rETH/ETH) goes stale with an inflated price (e.g., the feed is stuck at 1.05 ETH per stETH while the true rate has dropped to 1.00 ETH), any depositor calling `depositAsset()` receives 5% more rsETH than the actual ETH value of their deposit warrants. This over-minting dilutes all existing rsETH holders proportionally — a direct theft of their accrued yield and principal value. The inverse (stale deflated price) harms depositors by under-minting.

The stETH/ETH Chainlink feed has a 24-hour heartbeat, meaning prices can be up to 24 hours stale before Chainlink triggers an update. During this window, the vulnerability is fully exploitable by any depositor.

---

### Likelihood Explanation

**Likelihood: Low**

Chainlink feeds can go stale during network congestion, oracle node disruptions, or feed deprecation events. The 24-hour heartbeat on LST/ETH feeds creates a meaningful window. While not a routine occurrence, it is a realistic and documented failure mode for Chainlink oracles. No attacker capability is required beyond calling the public `depositAsset()` function during a stale-price window.

---

### Recommendation

Apply the same staleness validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
    require(answeredInRound >= roundId, "Stale price: round not complete");
    require(updatedAt != 0, "Stale price: incomplete round");
    require(price > 0, "Invalid price");
    // Optional: require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too stale");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. The Chainlink stETH/ETH feed goes stale (e.g., 12 hours without update, within the 24-hour heartbeat). The last reported price is 1.05e18 (stETH at a 5% premium to ETH), but the true current rate has dropped to 1.00e18.
2. An attacker (or any depositor) calls `LRTDepositPool.depositAsset(stETH, 100e18, minRSETH, "")`.
3. `_beforeDeposit()` calls `getRsETHAmountToMint(stETH, 100e18)`.
4. `getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.05e18`.
5. `rsethAmountToMint = (100e18 * 1.05e18) / rsETHPrice` — the depositor receives ~5% more rsETH than the 100 stETH is actually worth in ETH.
6. All existing rsETH holders are diluted by the excess minted rsETH. When `updateRSETHPrice()` is next called, the true TVL is lower than the inflated rsETH supply implies, and the rsETH price drops — existing holders lose value.

**Root cause line**: `contracts/oracles/ChainlinkPriceOracle.sol` line 52: `(, int256 price,,,) = priceFeed.latestRoundData();` [1](#0-0) 

**Propagation path**: `LRTDepositPool.depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()` [2](#0-1) 

**Contrast with validated oracle in same codebase**: `ChainlinkOracleForRSETHPoolCollateral.getRate()` checks `answeredInRound < roundID` and `timestamp == 0` but `ChainlinkPriceOracle` does not. [3](#0-2)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
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
