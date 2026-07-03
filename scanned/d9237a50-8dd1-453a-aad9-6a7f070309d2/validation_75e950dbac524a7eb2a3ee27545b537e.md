### Title
Missing Chainlink Staleness Check Causes Erroneous rsETH Price and Mis-Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards the `updatedAt` and `answeredInRound` return values, never verifying that the price data is fresh. This oracle feeds directly into `LRTOracle._getTotalEthInProtocol()`, which determines `rsETHPrice`. A stale Chainlink feed for any supported LST (stETH, rETH, ETHx, etc.) causes `rsETHPrice` to be computed incorrectly, leading to wrong rsETH minting amounts for every depositor.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches price data from a Chainlink aggregator but silently ignores the freshness fields:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt, answeredInRound discarded
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

This oracle is registered as the `assetPriceOracle` for supported LSTs in `LRTOracle`:

```solidity
// contracts/LRTOracle.sol L156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

`getAssetPrice()` is consumed by `_getTotalEthInProtocol()`, which sums the ETH-denominated value of every supported asset:

```solidity
// contracts/LRTOracle.sol L336-343
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // stale price used here
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
``` [3](#0-2) 

The result feeds `_updateRsETHPrice()`, which computes and stores `rsETHPrice`:

```solidity
// contracts/LRTOracle.sol L250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [4](#0-3) 

`rsETHPrice` is then used in `LRTDepositPool.getRsETHAmountToMint()` to determine how many rsETH tokens every depositor receives:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

`updateRSETHPrice()` is a public, permissionless function — any external caller can trigger a price update at any time:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [6](#0-5) 

### Impact Explanation
When a Chainlink feed for a supported LST goes stale with a price lower than the true market price (e.g., during a network outage or circuit-breaker event):

- `totalETHInProtocol` is underestimated.
- `rsETHPrice` is set below its true value.
- New depositors calling `depositAsset()` receive **more rsETH than their deposit is worth** (`amount * staleLowPrice / staleLowRsETHPrice` can still over-mint if the stale price affects the denominator less than the numerator, depending on asset composition).
- Existing rsETH holders are diluted — their proportional claim on the protocol's real ETH TVL decreases.

Conversely, a stale high price (e.g., feed frozen after a depeg event) causes `rsETHPrice` to be overestimated, shortchanging new depositors and causing the contract to fail to deliver promised returns.

**Impact: High — Theft of unclaimed yield / dilution of existing rsETH holders; Low — Contract fails to deliver promised returns to new depositors.**

### Likelihood Explanation
Chainlink feeds have historically gone stale or been paused during high-volatility events (e.g., LUNA collapse, exchange outages). The protocol supports multiple LSTs (stETH, rETH, ETHx, sfrxETH, swETH), each with its own Chainlink feed. Any one of these feeds going stale is sufficient to trigger the issue. Because `updateRSETHPrice()` is permissionless, an attacker can deliberately call it at the moment a feed is stale to lock in the erroneous price before the feed recovers.

### Recommendation
Add a staleness threshold check after calling `latestRoundData()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale price: round not complete");
require(updatedAt != 0, "Stale price: round not complete");
require(block.timestamp - updatedAt <= MAX_STALENESS_PERIOD, "Stale price: too old");
require(price > 0, "Invalid price");
```

Define `MAX_STALENESS_PERIOD` per feed (e.g., 3600 seconds for ETH/USD, 86400 seconds for slower feeds). If a feed is stale, `getAssetPrice()` should revert, preventing `updateRSETHPrice()` from committing a corrupted `rsETHPrice` to storage.

### Proof of Concept
1. Chainlink feed for stETH/ETH goes stale (e.g., `updatedAt` is 25 hours ago, price frozen at 0.98e18 while true rate is 1.02e18).
2. Attacker calls `LRTOracle.updateRSETHPrice()` (permissionless).
3. `_getTotalEthInProtocol()` values all stETH holdings at 0.98e18 instead of 1.02e18 → `totalETHInProtocol` is ~4% lower than reality.
4. `rsETHPrice` is set ~4% below true value.
5. Attacker immediately calls `LRTDepositPool.depositAsset(stETH, largeAmount, 0)`.
6. `getRsETHAmountToMint` computes: `largeAmount * 0.98e18 / (deflated rsETHPrice)` — the attacker receives excess rsETH relative to the true ETH value deposited.
7. When the Chainlink feed recovers and `rsETHPrice` is corrected upward, the attacker's rsETH is worth more ETH than they deposited, at the expense of existing holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
