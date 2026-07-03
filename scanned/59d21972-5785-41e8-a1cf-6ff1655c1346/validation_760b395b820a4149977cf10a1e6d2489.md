### Title
Stale Chainlink Price Accepted Without Timestamp or Validity Validation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards every validation field (`updatedAt`, `answeredInRound`, `roundId`). It also performs no check that the returned `price` is positive. A stale or zero/negative price flows directly into rsETH mint calculations, enabling depositors to receive inflated rsETH amounts at the expense of existing holders, or causing a revert-by-wrap on a negative price cast.

### Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol` line 52, the call to `latestRoundData()` discards all four validation return values:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The fields `roundId`, `startedAt`, `updatedAt`, and `answeredInRound` are all thrown away. No check is made that:
- `updatedAt` is recent (no staleness window enforced)
- `answeredInRound >= roundId` (no incomplete-round guard)
- `price > 0` (no zero/negative price guard)

This is in direct contrast to `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`, which correctly validates all three conditions before returning a price.

The stale price propagates through the following call chain:

1. `ChainlinkPriceOracle.getAssetPrice(asset)` → returns stale price
2. `LRTOracle.getAssetPrice(asset)` → delegates to the above via `IPriceFetcher`
3. `LRTDepositPool.getRsETHAmountToMint()` → `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()`
4. `LRTDepositPool.depositAsset()` / `depositETH()` → mints rsETH using the stale price

### Impact Explanation
If a Chainlink feed goes stale while the last reported price is inflated relative to the true current price (e.g., the asset has crashed but the oracle has not updated), a depositor calling `depositAsset()` receives more rsETH than the deposited assets are worth. This dilutes all existing rsETH holders proportionally, constituting protocol insolvency. Additionally, if `price` is returned as a negative `int256` (possible in edge-case Chainlink behavior), the unchecked cast `uint256(price)` wraps to a near-`type(uint256).max` value, causing either a massive over-mint or an arithmetic revert, both of which are harmful.

**Impact level: High** — theft of yield/value from existing rsETH holders via dilution; potential for protocol insolvency.

### Likelihood Explanation
Chainlink feeds can go stale during network congestion, sequencer downtime (on L2), or when the deviation threshold is not breached for an extended period. The heartbeat for many LST/ETH feeds is 24 hours, meaning a price that is hours old can be returned without any on-chain indication of staleness. This is a well-documented real-world scenario that has been exploited in other protocols.

### Recommendation
Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral.sol`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Where `STALENESS_THRESHOLD` is set per-feed based on its documented heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed).

### Proof of Concept

**Vulnerable code — `ChainlinkPriceOracle.getAssetPrice()`:** [1](#0-0) 

All four validation fields are discarded; no staleness, no round completeness, no sign check.

**Contrast — `ChainlinkOracleForRSETHPoolCollateral.getRate()` (correct pattern):** [2](#0-1) 

**Stale price flows into rsETH mint amount:** [3](#0-2) 

**Entry point reachable by any unprivileged depositor:** [4](#0-3) 

**Attack scenario:**
1. A supported LST asset (e.g., stETH) experiences a sharp price drop.
2. The Chainlink feed for that asset has not yet updated (within its heartbeat window, e.g., 24 h).
3. An attacker calls `depositAsset(stETH, largeAmount, 0, "")`.
4. `getRsETHAmountToMint` uses the stale (inflated) price, minting excess rsETH.
5. The attacker immediately redeems or sells the excess rsETH, extracting value from existing holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
