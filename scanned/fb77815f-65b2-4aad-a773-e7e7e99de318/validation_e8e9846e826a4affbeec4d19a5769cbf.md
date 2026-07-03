### Title
Stale Chainlink Price Accepted Without Freshness Validation Enables Over-Minting of rsETH - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, performing no staleness or validity checks. When a Chainlink feed goes stale (e.g., during network congestion, sequencer downtime, or a depeg event), a depositor can supply an LST at the inflated stale price and receive more rsETH than the actual value warrants, diluting all existing rsETH holders.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` at line 52 reads the Chainlink feed as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

The `roundId`, `updatedAt`, and `answeredInRound` return values are all silently discarded. No check is made that:
- `answeredInRound >= roundId` (detects a stale/incomplete round)
- `updatedAt != 0` (detects an incomplete round)
- `updatedAt` is within an acceptable heartbeat window (detects a frozen feed)
- `price > 0` (detects a zero/negative price)

This is the oracle used by `LRTOracle.getAssetPrice()`, which is called inside `LRTOracle._getTotalEthInProtocol()` and directly by `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

The same codebase already implements proper staleness checks in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle` — the oracle used for all LST assets in the core deposit path — has none of these guards.

### Impact Explanation
When a Chainlink LST/ETH feed goes stale while the actual market price of the LST has dropped (e.g., a depeg event, slashing, or sequencer downtime on an L2 deployment), the stale inflated price is used to compute `rsethAmountToMint`. The depositor receives more rsETH than the deposited value justifies. This dilutes the backing of all existing rsETH holders — a direct theft of value from rsETH holders proportional to the price discrepancy and deposit size.

**Impact: High** — Theft of unclaimed yield / dilution of existing rsETH holders. At sufficient scale (large deposit during a significant depeg + stale feed), this can approach protocol insolvency.

### Likelihood Explanation
Chainlink feeds go stale in documented real-world scenarios:
- Network congestion preventing keeper updates
- Sequencer downtime on L2 chains (Arbitrum, Base, Optimism, Linea, zkSync — all chains where RSETHPool contracts are deployed)
- Feed deprecation or migration windows
- Extreme market volatility causing keeper failures

An attacker only needs to monitor the `updatedAt` timestamp of the relevant Chainlink feed and act during the stale window. No flashloan or complex setup is required — a standard `depositAsset()` call suffices.

**Likelihood: Medium** — Stale feed windows are infrequent but have occurred historically; the attacker path requires no special permissions.

### Recommendation
Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optional: if (block.timestamp - updatedAt > HEARTBEAT_THRESHOLD) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

### Proof of Concept
1. Chainlink's `stETH/ETH` feed goes stale at `1.0e18` (1:1 peg) while stETH actually depegs to `0.95e18` on the market.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
3. `getRsETHAmountToMint` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.0e18`.
4. `rsethAmountToMint = (1000e18 * 1.0e18) / rsETHPrice` — computed at full peg.
5. Attacker receives rsETH worth ~1000 ETH while depositing stETH worth only ~950 ETH.
6. The ~50 ETH difference is extracted from existing rsETH holders' backing. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
