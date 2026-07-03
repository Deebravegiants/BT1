### Title
`ChainlinkPriceOracle.getAssetPrice` Accepts Stale Chainlink Prices With No Staleness Validation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all staleness-related return values (`updatedAt`, `answeredInRound`). There is no time-based or round-based freshness check. A stale price is accepted as valid and flows directly into rsETH minting calculations, enabling depositors to receive inflated rsETH amounts at the expense of existing holders.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-54
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`updatedAt` and `answeredInRound` are both discarded (the tuple destructuring uses `(, int256 price,,,)`). No check of the form `block.timestamp - updatedAt > heartbeat` or `answeredInRound < roundId` is performed.

This result is consumed by `LRTOracle.getAssetPrice()`, which is called in two critical paths:

1. **Deposit minting** — `LRTDepositPool.getRsETHAmountToMint()` computes:
   ```solidity
   rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
   ```
2. **rsETH price update** — `LRTOracle._getTotalEthInProtocol()` sums `assetER * totalAssetAmt` for every supported asset to derive the new `rsETHPrice`.

Both paths use the raw, unchecked Chainlink answer.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` (used in pool collateral pricing) at least checks `answeredInRound < roundID`, demonstrating that the project is aware of staleness concerns but failed to apply them to the core oracle.

### Impact Explanation
**High — Theft of unclaimed yield.**

When a Chainlink LST/ETH feed goes stale (price frozen at a value higher than the current market price), any depositor can call `LRTDepositPool.depositAsset()` and receive rsETH computed against the inflated stale price. The excess rsETH minted is backed by fewer real assets than implied, diluting the ETH-per-rsETH ratio for all existing holders. Their accrued yield (reflected in the rsETH/ETH exchange rate) is permanently reduced.

### Likelihood Explanation
**Medium.** Chainlink feeds update on deviation thresholds (typically 0.5%) or heartbeat intervals (24 hours for many LST/ETH feeds). During periods of network congestion, oracle downtime, or when an asset's price moves slowly, feeds can remain stale for hours. This is a well-documented real-world event. No special permissions are required — any depositor can trigger the path.

### Recommendation
Add a per-feed configurable heartbeat and validate freshness in `getAssetPrice()`:

```solidity
mapping(address asset => uint256 heartbeat) public assetHeartbeat;

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();
    require(answeredInRound >= roundId, "Stale round");
    require(block.timestamp - updatedAt <= assetHeartbeat[asset], "Stale price");
    require(price > 0, "Invalid price");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

### Proof of Concept

1. Assume `stETH/ETH` Chainlink feed has a 24-hour heartbeat and last updated at price `1.05 ETH` per stETH.
2. The actual stETH market price drops to `0.98 ETH` (e.g., due to a slashing event), but the feed has not yet updated (deviation threshold not crossed, heartbeat not elapsed).
3. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0)`.
4. `getRsETHAmountToMint` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.05e18`.
5. rsETH minted = `(1000e18 * 1.05e18) / rsETHPrice` — attacker receives rsETH valued at 1050 ETH worth of assets while only depositing 980 ETH worth.
6. The 70 ETH surplus is extracted from existing rsETH holders' accrued yield, permanently reducing the rsETH/ETH exchange rate for all other holders.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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
