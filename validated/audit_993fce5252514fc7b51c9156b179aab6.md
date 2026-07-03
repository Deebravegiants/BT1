### Title
Missing Staleness Check in `ChainlinkPriceOracle.getAssetPrice()` Allows Stale Price to Inflate rsETH Minting, Diluting Existing Holders - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all validity fields (`updatedAt`, `answeredInRound`, `roundId`). A stale Chainlink price is silently accepted and propagated into the rsETH exchange rate, allowing an attacker to mint rsETH at a deflated price and extract value from existing holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` retrieves the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values of `latestRoundData()` are available — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — but only `answer` is used. There is no check on:
- `updatedAt` (timestamp of last update — detects heartbeat staleness)
- `answeredInRound >= roundId` (detects an incomplete/in-progress round)
- `price > 0` (detects a zeroed-out or negative feed)

This is in direct contrast to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which is used for the pool collateral path and correctly validates all three conditions:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The vulnerable `getAssetPrice()` feeds directly into the rsETH price computation chain:

1. `ChainlinkPriceOracle.getAssetPrice()` is called by `LRTOracle.getAssetPrice()` [3](#0-2) 
2. Which is called by `LRTOracle._getTotalEthInProtocol()` for every supported LST asset [4](#0-3) 
3. Which feeds `_updateRsETHPrice()`, computing `newRsETHPrice = totalETHInProtocol / rsethSupply` [5](#0-4) 
4. The resulting `rsETHPrice` is stored and used by `LRTDepositPool` to determine how many rsETH tokens to mint per deposited asset.

The entry point `updateRSETHPrice()` is **public and permissionless** — any external caller can trigger it:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [6](#0-5) 

---

### Impact Explanation

**Theft of yield from existing rsETH holders (High).**

If a Chainlink feed for any supported LST asset goes stale with a price lower than the true current price (e.g., during network congestion, feed deprecation, or L2 sequencer downtime):

1. `totalETHInProtocol` is undervalued.
2. `newRsETHPrice` is deflated below its true value.
3. An attacker calls `updateRSETHPrice()` to commit the stale low price on-chain.
4. The attacker deposits assets and receives more rsETH than the true exchange rate warrants.
5. When the price is corrected (next honest update), the attacker's excess rsETH represents value extracted from all existing rsETH holders — their proportional claim on the underlying pool is diluted.

The inverse (stale high price) causes depositors to receive fewer rsETH tokens than deserved, representing a loss to new depositors.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 1 hour or 24 hours depending on the feed). During periods of low volatility, feeds may not update for the full heartbeat window. On L2 deployments, sequencer downtime can cause feeds to go stale for extended periods. The attack requires no privileged access — only the ability to observe a stale feed and call the public `updateRSETHPrice()` function at the right moment.

---

### Recommendation

Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > MAX_STALENESS_PERIOD) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`MAX_STALENESS_PERIOD` should be set per-feed based on the Chainlink heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed, with a small buffer).

---

### Proof of Concept

1. Assume `stETH/ETH` Chainlink feed has a 24-hour heartbeat and last updated 23 hours ago at price `0.999e18`.
2. The true current price has dropped to `0.97e18` due to a depeg event, but the feed has not yet updated.
3. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control).
4. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `0.999e18` instead of `0.97e18`.
5. `totalETHInProtocol` is inflated → `newRsETHPrice` is inflated above true value.
6. Attacker deposits stETH via `LRTDepositPool.depositAsset()` and receives fewer rsETH than deserved (inverse scenario).

For the dilution scenario: if the feed is stale at a **lower** price than reality (e.g., feed froze during a price rally):
- `totalETHInProtocol` is undervalued → `rsETHPrice` is deflated.
- Attacker calls `updateRSETHPrice()` to commit the deflated price.
- Attacker deposits assets and receives excess rsETH at the artificially low price.
- When the oracle is corrected, the attacker's rsETH is worth more than what they paid, at the expense of existing holders. [7](#0-6) [6](#0-5) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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
