### Title
Stale Chainlink Price Accepted Without Freshness Validation Enables Over-Minting of rsETH - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards the `updatedAt` and `answeredInRound` return values, accepting arbitrarily stale prices. This price feeds directly into rsETH minting calculations in `LRTDepositPool`, allowing a depositor to receive more rsETH than the fair value of their deposit whenever a Chainlink feed is stale with an inflated price — diluting all existing rsETH holders.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the LST/ETH exchange rate from a Chainlink aggregator:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The `updatedAt` timestamp and `answeredInRound` round ID are silently dropped. No maximum age check (e.g., `block.timestamp - updatedAt > heartbeat`) and no round-completeness check (`answeredInRound >= roundId`) are performed. [1](#0-0) 

By contrast, the protocol's own `ChainlinkOracleForRSETHPoolCollateral` — used in the L2 pool path — explicitly guards against both conditions:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
``` [2](#0-1) 

The stale price returned by `ChainlinkPriceOracle` propagates through two critical paths:

**Path 1 — Direct deposit minting:**
`LRTDepositPool.getRsETHAmountToMint()` computes:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

`lrtOracle.getAssetPrice(asset)` delegates directly to `ChainlinkPriceOracle.getAssetPrice()`. [4](#0-3) 

**Path 2 — rsETH price update:**
`LRTOracle._getTotalEthInProtocol()` also calls `getAssetPrice(asset)` for every supported LST to compute the protocol TVL, which then sets `rsETHPrice`. [5](#0-4) 

### Impact Explanation

If a Chainlink LST/ETH feed is stale with an inflated price (e.g., the feed last reported a price of 1.05 ETH per stETH but the true rate has since dropped to 1.00 ETH):

- The numerator `amount * getAssetPrice(asset)` is inflated.
- The depositor receives more rsETH than the ETH-equivalent value they deposited.
- Every existing rsETH holder is diluted — their share of the underlying pool is reduced without compensation.

This is a direct, quantifiable theft of value from existing rsETH holders. The magnitude scales with the size of the deposit and the degree of price staleness.

**Impact: High — Theft of unclaimed yield / dilution of existing holders.**

### Likelihood Explanation

Chainlink feeds operate on a heartbeat model (e.g., 1-hour or 24-hour heartbeat for LST feeds). During Ethereum network congestion — the exact scenario described in the reference Umee report — Chainlink keeper transactions may fail to land, causing feeds to go stale beyond their heartbeat. This is a documented, historically observed condition (e.g., during the March 2020 congestion event). No attacker action is required to cause the staleness; the attacker only needs to observe the stale state and deposit.

**Likelihood: Medium.**

### Recommendation

Add staleness and round-completeness checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0) revert IncompleteRound();
if (block.timestamp - updatedAt > MAX_PRICE_AGE) revert PriceOutdated();
if (price <= 0) revert InvalidPrice();
```

`MAX_PRICE_AGE` should be set per-asset to match the Chainlink feed's documented heartbeat plus a reasonable buffer.

### Proof of Concept

1. Assume stETH/ETH Chainlink feed has a 24-hour heartbeat. The last reported price was 1.05 ETH/stETH, 25 hours ago. The true current rate is 1.00 ETH/stETH (feed is stale).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
3. `getRsETHAmountToMint()` computes: `(1000e18 * 1.05e18) / rsETHPrice`. With `rsETHPrice = 1e18`, the attacker receives **1050 rsETH** for 1000 stETH (worth 1000 ETH).
4. The attacker now holds rsETH backed by 1050 ETH of claimed value but only contributed 1000 ETH of real value.
5. The 50 ETH surplus is extracted from existing rsETH holders' share of the pool.
6. Attacker redeems rsETH via the withdrawal system, receiving more ETH than deposited.

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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
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
