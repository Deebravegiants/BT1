### Title
No Staleness Check on Chainlink `latestRoundData()` in `ChainlinkPriceOracle` Allows Stale Asset Prices to Corrupt rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but discards every validation field (`roundId`, `updatedAt`, `answeredInRound`), accepting whatever price the feed returns with no staleness detection. This stale price propagates directly into the rsETH/ETH exchange rate used for all deposits and withdrawals.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` is used; `updatedAt` (the timestamp of the last update) and `answeredInRound` (the round in which the answer was computed) are silently discarded. [1](#0-0) 

By contrast, the sister contract `ChainlinkOracleForRSETHPoolCollateral` in the same repository explicitly guards against this:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
``` [2](#0-1) 

The stale price returned by `ChainlinkPriceOracle.getAssetPrice()` is consumed by `LRTOracle.getAssetPrice()`, which is called inside `_getTotalEthInProtocol()`, which is called by `_updateRsETHPrice()`. [3](#0-2) 

`_updateRsETHPrice()` uses the total ETH value to compute and store `rsETHPrice`, the global exchange rate for the entire protocol. [4](#0-3) 

### Impact Explanation

A stale Chainlink price for any supported LST asset (e.g., stETH, rETH, cbETH) causes `_getTotalEthInProtocol()` to return an incorrect TVL. This directly corrupts `rsETHPrice`:

- **Inflated stale price** → overstated TVL → rsETH minted at a higher rate than warranted → depositors receive fewer rsETH tokens than they should (value loss for depositors).
- **Deflated stale price** → understated TVL → rsETH minted at a lower rate → depositors receive more rsETH than they should (theft of yield from existing holders).

Either direction constitutes the contract failing to deliver promised returns, and the deflated-price direction constitutes theft of unclaimed yield from existing rsETH holders. Impact: **High** (theft of unclaimed yield) / **Low** (contract fails to deliver promised returns).

### Likelihood Explanation

Chainlink feeds can go stale during network congestion, sequencer downtime (on L2s), or when a feed is deprecated and replaced. `updateRSETHPrice()` is a public, permissionless function callable by any user at any time. [5](#0-4) 

Any unprivileged caller can trigger `updateRSETHPrice()` while a feed is stale, locking in the corrupted exchange rate.

### Recommendation

Add staleness checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (price <= 0) revert InvalidPrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (answeredInRound < roundId) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Optionally, add a configurable `heartbeat` per feed and check `block.timestamp - updatedAt > heartbeat`.

### Proof of Concept

1. A supported LST asset (e.g., rETH) has its Chainlink feed go stale (last updated 25 hours ago).
2. Any user calls `LRTOracle.updateRSETHPrice()`.
3. `_getTotalEthInProtocol()` calls `getAssetPrice(rETH)` → `ChainlinkPriceOracle.getAssetPrice(rETH)` → returns the 25-hour-old price with no revert.
4. `_updateRsETHPrice()` computes `newRsETHPrice` using the stale TVL and stores it as `rsETHPrice`.
5. All subsequent deposits and withdrawals use the corrupted exchange rate until the next valid price update. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-31)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
```

**File:** contracts/LRTOracle.sol (L87-88)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
```

**File:** contracts/LRTOracle.sol (L214-231)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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
