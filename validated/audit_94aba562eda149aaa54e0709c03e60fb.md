Audit Report

## Title
Unvalidated Chainlink Price Response in `ChainlinkPriceOracle.getAssetPrice()` Corrupts rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and returns the result without validating for zero/negative price, stale round, or incomplete round. A zero price for any supported LST asset propagates unchecked into `LRTOracle._getTotalEthInProtocol()`, corrupting `rsETHPrice`. Depending on the `pricePercentageLimit` configuration, this either triggers an unwarranted protocol-wide pause (temporary fund freeze) or allows depositors to mint excess rsETH at the expense of existing holders (protocol insolvency).

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` at L49–55 fetches the Chainlink price and immediately casts and returns it with no sanity checks:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Missing checks: `price <= 0`, `answeredInRound < roundId`, `updatedAt == 0`.

The protocol's own `ChainlinkOracleForRSETHPoolCollateral.getRate()` (L26–37) correctly performs all three checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The bad price flows into `LRTOracle._getTotalEthInProtocol()` (L336–343), which is called by `_updateRsETHPrice()` (L214–316). The downside-protection check at L270–282 only pauses when `pricePercentageLimit > 0` and the drop exceeds the configured threshold:

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```

When `pricePercentageLimit == 0`, this condition is always false, so the corrupted `rsETHPrice` is written to state at L313. It is then used in `LRTDepositPool.getRsETHAmountToMint()` (L520):

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

An artificially low `rsETHPrice` denominator causes this division to return an inflated rsETH mint amount.

## Impact Explanation

**Scenario A — Temporary freezing of funds (Medium):** When `pricePercentageLimit > 0` and the zero price causes a drop exceeding the threshold, `_updateRsETHPrice()` pauses `LRTDepositPool` and `LRTWithdrawalManager` (L278–280), freezing all user deposits and withdrawals until admin intervention.

**Scenario B — Protocol insolvency (Critical):** When `pricePercentageLimit == 0` (or the affected asset's TVL share is small enough that the price drop stays within the limit), the corrupted `rsETHPrice` is written to state. Any depositor calling `depositAsset()` or `depositETH()` immediately after receives more rsETH than their deposited assets are worth, permanently diluting all existing rsETH holders. This constitutes protocol insolvency — an allowed Critical impact.

## Likelihood Explanation

`updateRSETHPrice()` is public and permissionless (only `whenNotPaused`), callable by any external account at any time. Chainlink feeds are documented to return `0` during circuit breaker events, feed deprecation, or sequencer downtime on L2. The protocol supports multiple LST assets (stETH, ethX, sfrxETH, rETH), each with its own feed, multiplying the attack surface. The inconsistency with `ChainlinkOracleForRSETHPoolCollateral` demonstrates the protocol is aware of this class of issue, making the omission in `ChainlinkPriceOracle` a clear gap. No privileged access is required; a normal external caller can trigger the exploit immediately after a Chainlink feed returns a bad value.

## Recommendation

Apply the same validation already present in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, add a per-feed heartbeat staleness check: `if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();`.

## Proof of Concept

1. Chainlink's stETH/ETH feed returns `price = 0` (circuit breaker or feed deprecation).
2. Any external caller invokes `LRTOracle.updateRSETHPrice()` (public, no access control beyond `whenNotPaused`).
3. `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice()` → returns `0`.
4. `totalETHInProtocol` excludes the entire stETH TVL (e.g., 10,000 ETH counted as 0).
5. `newRsETHPrice = (totalETHInProtocol - 0) / rsethSupply` is significantly below `highestRsethPrice`.
6. **Path A (`pricePercentageLimit > 0`, drop exceeds limit):** `isPriceDecreaseOffLimit = true` → `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` → all user funds frozen.
7. **Path B (`pricePercentageLimit == 0`):** `isPriceDecreaseOffLimit = false` → `rsETHPrice` written as deflated value → depositor calls `depositAsset(stETH, 1 ether, 0, "")` → `getRsETHAmountToMint` computes `(1e18 * getAssetPrice(stETH)) / deflatedRsETHPrice`, minting far more rsETH than 1 stETH is worth → existing holders diluted.

**Foundry fork test outline:**
```solidity
// Fork mainnet, mock stETH Chainlink feed to return price=0
// Call LRTOracle.updateRSETHPrice() as address(1)
// Assert: either protocol is paused (Path A) or rsETHPrice < pre-update price (Path B)
// For Path B: deposit 1 stETH, assert rsethAmountToMint > fair value
```