### Title
No Chainlink Price Staleness Check Allows Stale LST/ETH Rates to Silently Corrupt rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards the `updatedAt` return value entirely, accepting any price regardless of age. This is the same vulnerability class as the reference report (oracle staleness handling), but manifests as the opposite extreme: instead of a `maxLatency` that is too tight and causes reverts, there is **no latency bound at all**, so stale prices are silently consumed.

### Finding Description
In `getAssetPrice()`, the destructuring pattern `(, int256 price,,,)` drops all five return values except `answer`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol line 52
(, int256 price,,,) = priceFeed.latestRoundData();
```

The `updatedAt` (4th return value) is never read, so there is no `block.timestamp - updatedAt > maxLatency` guard. Any price, no matter how old, is returned as if it were current.

By contrast, the pool-level wrapper `ChainlinkOracleForRSETHPoolCollateral.getRate()` does capture `timestamp` and checks `answeredInRound < roundID` and `timestamp == 0`, but still omits a wall-clock freshness bound (`block.timestamp - timestamp > threshold`). The core oracle used for rsETH pricing has no check at all.

### Impact Explanation
`ChainlinkPriceOracle.getAssetPrice()` is the price source for every supported LST (stETH, rETH, ETHx, swETH, sfrxETH). It feeds:

1. `LRTOracle._getTotalEthInProtocol()` → `_updateRsETHPrice()` — sets the stored `rsETHPrice`.
2. `LRTDepositPool.getRsETHAmountToMint()` — `rsethAmountToMint = (amount × getAssetPrice(asset)) / rsETHPrice()` — determines how many rsETH tokens a depositor receives.
3. `LRTWithdrawalManager.getExpectedAssetAmount()` — `underlyingToReceive = amount × rsETHPrice() / getAssetPrice(asset)` — determines how much LST a withdrawer receives.

If a Chainlink LST/ETH feed goes stale at an inflated value (e.g., the feed freezes above the true market price), depositors receive fewer rsETH than they are owed. If it freezes at a deflated value, depositors receive more rsETH than they are owed, diluting existing holders. Either direction causes incorrect share accounting and a failure to deliver promised returns.

### Likelihood Explanation
Chainlink LST/ETH feeds (stETH/ETH, rETH/ETH, etc.) have documented heartbeats of 86 400 seconds on mainnet. A feed can go stale during network congestion, oracle node downtime, or feed deprecation. The reference report itself notes that at the time of writing every mainnet floor price feed had an `updatedAt` well over 3 600 seconds in the past. The same class of event applies here: any period of oracle inactivity longer than the heartbeat silently passes a stale price into the rsETH pricing math.

### Recommendation
Capture `updatedAt` in `getAssetPrice()` and revert if the price is older than an acceptable threshold (e.g., the feed's documented heartbeat plus a small buffer):

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
if (block.timestamp - updatedAt > MAX_PRICE_AGE) revert PriceNotRecentEnough();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

`MAX_PRICE_AGE` should be set per-feed or at least to the longest heartbeat among all configured feeds (86 400 s for mainnet LST/ETH feeds). Apply the same fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which checks `answeredInRound < roundID` but still lacks a wall-clock freshness bound.

### Proof of Concept
1. Chainlink stETH/ETH feed on mainnet stops updating (heartbeat expires, ~86 400 s passes).
2. Anyone calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice()` → returns the frozen stale price with no revert.
4. `rsETHPrice` is updated using the stale stETH/ETH rate.
5. A depositor calls `LRTDepositPool.depositAsset(stETH, amount, ...)`.
6. `getRsETHAmountToMint()` computes `rsethAmountToMint = (amount × stalePrice) / rsETHPrice` — if `stalePrice` is deflated relative to the true rate, the depositor receives fewer rsETH than they are owed; if inflated, existing holders are diluted.

Relevant code locations: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L331-349)
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

            unchecked {
                ++assetIdx;
            }
        }
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
