### Title
Stale Chainlink Price Accepted Without Staleness Check — (`contracts/oracles/ChainlinkPriceOracle.sol`)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `answer`. The staleness indicators `updatedAt` and `answeredInRound` are silently ignored, so a stale or incomplete Chainlink round is accepted as a valid price. This is the direct analog of the LSSVMRouter bug: a multi-value return from a quote/price function is consumed with the status fields dropped, allowing invalid data to flow into downstream calculations.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and destructures only the `answer` field:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol line 52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

`latestRoundData()` returns five values: `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The fields `updatedAt` and `answeredInRound` are the protocol-defined staleness indicators: `updatedAt == 0` signals an incomplete round, and `answeredInRound < roundId` signals that the answer was computed in a prior round (i.e., the feed is stale). Both are dropped without any check.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.sol` — another oracle wrapper in the same repository — validates all three conditions before returning a price:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol lines 30-32
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The inconsistency proves the protocol is aware of the pattern but failed to apply it in `ChainlinkPriceOracle`.

`LRTOracle.getAssetPrice()` delegates directly to the registered `IPriceFetcher`, which for LST assets is `ChainlinkPriceOracle`: [3](#0-2) 

This stale price then propagates into two critical paths:

**Path 1 — rsETH minting:**
`LRTDepositPool.getRsETHAmountToMint()` divides `amount * lrtOracle.getAssetPrice(asset)` by `lrtOracle.rsETHPrice()`. [4](#0-3) 

**Path 2 — rsETH price update:**
`LRTOracle._getTotalEthInProtocol()` multiplies each asset's total deposit by `getAssetPrice(asset)` to compute the protocol TVL used in `_updateRsETHPrice()`. [5](#0-4) 

### Impact Explanation
If a Chainlink feed for a supported LST (e.g., stETH/ETH, ethX/ETH) becomes stale and the last recorded `answer` is higher than the true current price, any depositor calling `depositAsset()` or `depositETH()` will receive more rsETH than the deposited value warrants. This over-minting dilutes the share of all existing rsETH holders, constituting theft of their accrued yield. The same stale price inflates the computed TVL in `_updateRsETHPrice()`, causing the rsETH price to be set above its true value, compounding the mis-accounting.

**Impact: High — Theft of unclaimed yield (dilution of existing rsETH holders via over-minting).**

### Likelihood Explanation
Chainlink feeds can return stale data during periods of low L1 activity, sequencer downtime on L2, or when the deviation threshold is not crossed for an extended period. The condition is externally observable and does not require any privileged access. Any unprivileged depositor can trigger the vulnerable path by calling `depositAsset()` or `depositETH()` while the feed is stale.

**Likelihood: Medium.**

### Recommendation
Apply the same staleness checks used in `ChainlinkOracleForRSETHPoolCollateral.sol` inside `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    require(answeredInRound >= roundId, "Stale price");
    require(updatedAt != 0, "Incomplete round");
    require(price > 0, "Invalid price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a `block.timestamp - updatedAt <= MAX_DELAY` heartbeat check tuned to each feed's expected update frequency.

### Proof of Concept
1. Chainlink stETH/ETH feed enters a stale round (e.g., `answeredInRound = 5`, `roundId = 6`, last `answer = 1.05e18` while true rate has dropped to `1.00e18`).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1e18, 0, "")`.
3. `getRsETHAmountToMint` computes: `1e18 * 1.05e18 / rsETHPrice` → attacker receives ~5% more rsETH than the deposited value warrants.
4. `ChainlinkPriceOracle.getAssetPrice()` returns `1.05e18` without reverting because `updatedAt` and `answeredInRound` are never read.
5. Existing rsETH holders are diluted by the over-minted supply; the attacker can immediately redeem or bridge the excess rsETH for profit.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
