Audit Report

## Title
Stale Chainlink Price Accepted Without Timestamp or Validity Validation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all four validation return values (`roundId`, `startedAt`, `updatedAt`, `answeredInRound`) and performs no check that `price > 0`. A stale or zero price flows directly into rsETH mint calculations via `LRTDepositPool.getRsETHAmountToMint()`, enabling any depositor to receive inflated rsETH amounts at the expense of existing holders when a Chainlink feed has not updated within its heartbeat window.

## Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol` at line 52, `latestRoundData()` is called with all validation fields silently discarded:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

No check is made that `updatedAt` is recent, that `answeredInRound >= roundId`, or that `price > 0`. This is in direct contrast to `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` lines 30–32, which correctly validates all three conditions before returning a price.

The stale price propagates through the following confirmed call chain:
1. `ChainlinkPriceOracle.getAssetPrice(asset)` → returns stale price (line 52)
2. `LRTOracle.getAssetPrice(asset)` → delegates via `IPriceFetcher`
3. `LRTDepositPool.getRsETHAmountToMint()` → `rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()` (line 520)
4. `LRTDepositPool.depositAsset()` → callable by any unprivileged user (line 99), mints rsETH using the stale price

The `minRSETHAmountExpected` slippage parameter in `depositAsset()` protects only the depositor from receiving too little rsETH; it does not protect existing holders from dilution when the price is stale and inflated.

## Impact Explanation
When a supported LST asset's Chainlink feed goes stale while the last reported price is above the true current price (e.g., the asset has crashed but the oracle has not updated within its heartbeat window), any depositor calling `depositAsset()` receives more rsETH than the deposited assets are worth. This dilutes all existing rsETH holders proportionally, constituting direct theft of value from existing holders. At sufficient scale or with a sufficiently stale price, this constitutes protocol insolvency. This maps to **High — Theft of unclaimed yield** (dilution of existing rsETH holders' proportional claim on protocol assets) and potentially **Critical — Protocol insolvency** depending on the magnitude of the price deviation.

## Likelihood Explanation
Chainlink feeds can go stale during network congestion or when the deviation threshold is not breached for an extended period. Many LST/ETH feeds have a 24-hour heartbeat, meaning a price that is many hours old can be returned without any on-chain indication of staleness. No special attacker capability is required beyond calling the public `depositAsset()` function. The attacker need only monitor for a divergence between the true asset price and the last Chainlink reported price, then deposit during the staleness window. This is a well-documented real-world scenario that has been exploited in other protocols.

## Recommendation
Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral.sol`, and additionally add a staleness threshold check:

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

`STALENESS_THRESHOLD` should be set per-feed based on its documented heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed).

## Proof of Concept
**Foundry fork test plan:**

1. Fork mainnet at a block where a supported LST Chainlink feed's `updatedAt` is more than its heartbeat in the past (simulate by warping `block.timestamp` forward past the heartbeat window).
2. Deploy or reference the existing `ChainlinkPriceOracle` with the stale feed registered for a supported asset.
3. Call `LRTDepositPool.depositAsset(asset, largeAmount, 0, "")` as an unprivileged address.
4. Observe that `getRsETHAmountToMint` uses the stale (inflated) price, minting excess rsETH relative to the true current asset value.
5. Confirm that existing rsETH holders' proportional claim on protocol assets is reduced.

The vulnerable line is confirmed at `contracts/oracles/ChainlinkPriceOracle.sol:52` — all four validation fields are discarded. The correct pattern exists at `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol:30-32` but is not applied here. The deposit entry point at `contracts/LRTDepositPool.sol:99-118` is reachable by any unprivileged caller, and the price is consumed at line 520.