Audit Report

## Title
Missing Staleness Validation on Chainlink `latestRoundData()` Enables Incorrect rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards `updatedAt`, `answeredInRound`, `roundId`, and does not check `price > 0`, accepting whatever price the feed last stored with no temporal or validity check. This stale price is consumed directly by `LRTDepositPool.getRsETHAmountToMint()` and `LRTWithdrawalManager.getExpectedAssetAmount()`, allowing an unprivileged depositor to receive excess rsETH backed by no real ETH value when a feed is stale at an inflated price, diluting all existing rsETH holders.

## Finding Description
`ChainlinkPriceOracle.getAssetPrice()` at line 52 retains only `price` from `latestRoundData()`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

None of the following checks are present: `answeredInRound >= roundId`, `updatedAt != 0`, `block.timestamp - updatedAt <= MAX_STALENESS`, or `price > 0`. The sister contract `ChainlinkOracleForRSETHPoolCollateral.getRate()` at lines 30–32 does perform the first three of these checks, confirming the protocol is aware of the pattern and intentionally applies it elsewhere.

The stale price propagates through the following confirmed call chain:

1. `LRTOracle.getAssetPrice(asset)` (L156–158) delegates to `IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset)`, resolving to `ChainlinkPriceOracle`.
2. `LRTOracle._getTotalEthInProtocol()` (L339–343) calls `getAssetPrice(asset)` for every supported LST and multiplies by total deposits to compute protocol TVL.
3. `LRTOracle._updateRsETHPrice()` (L250) derives `newRsETHPrice` from that TVL figure.
4. `LRTDepositPool.getRsETHAmountToMint()` (L520) computes `(amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()` — the numerator uses the live (stale) Chainlink price while the denominator uses the last stored rsETH price, which may not yet reflect the stale feed.
5. `LRTWithdrawalManager.getExpectedAssetAmount()` (L593) computes `amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset)` — a stale low price here causes withdrawers to receive fewer assets than owed.

The `pricePercentageLimit` guard in `_updateRsETHPrice()` only fires when `updateRSETHPrice()` is explicitly called; it does not intercept the direct `getAssetPrice()` call made during `depositAsset()`. No other guard in the deposit or withdrawal path validates oracle freshness.

## Impact Explanation
**High — Theft of unclaimed yield.**

When a Chainlink LST/ETH feed is stale at a price higher than the actual market price (e.g., stETH feed shows 1.05 ETH while actual price has dropped to 0.99 ETH due to a slashing event), an attacker calling `depositAsset(stETH, amount, 0)` receives `amount × 1.05 / rsETHPrice` rsETH instead of the correct `amount × 0.99 / rsETHPrice`. The excess rsETH is backed by no real ETH value and dilutes all existing rsETH holders proportionally, constituting theft of unclaimed yield from existing holders. The inverse (stale price below actual) causes withdrawers to receive fewer assets than owed, constituting temporary freezing of the difference.

## Likelihood Explanation
Chainlink LST/ETH feeds (e.g., stETH/ETH) have heartbeat intervals of up to 24 hours. During network congestion or oracle node failures, the feed can remain stale for the entire heartbeat window without any on-chain revert. An attacker monitoring Chainlink feed `updatedAt` timestamps can detect the staleness condition and act within the same block. No privileged access is required — `depositAsset()` is callable by any user with the relevant LST token. The condition is passive and repeatable across any heartbeat window where the feed lags a real price move.

## Recommendation
Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral`, extended with a maximum-age bound, inside `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0) revert IncompleteRound();
if (price <= 0) revert InvalidPrice();
if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
```

`MAX_STALENESS` should be set per-feed (e.g., heartbeat + buffer) and stored as a configurable parameter alongside `assetPriceFeed`.

## Proof of Concept
1. The stETH/ETH Chainlink feed last updated at `T-20h` with price `1.05e18`. Actual stETH price has since dropped to `0.99e18` due to a slashing event; the feed has not yet triggered a deviation update.
2. `rsETHPrice` was last stored at `1.04e18` (correctly computed before the price drop).
3. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0)`.
4. `getRsETHAmountToMint(stETH, 100e18)` computes `100e18 × 1.05e18 / 1.04e18 ≈ 100.96e18` rsETH.
5. Correct amount based on actual price: `100e18 × 0.99e18 / 1.04e18 ≈ 95.19e18` rsETH.
6. Attacker receives `≈ 5.77` excess rsETH backed by no real ETH value, diluting all existing holders.
7. No admin action, no privileged role, and no oracle operator compromise is required.

**Foundry fork test plan:** Fork mainnet, mock the stETH/ETH Chainlink feed to return a stale `updatedAt` (e.g., `block.timestamp - 25 hours`) with an inflated price. Call `depositAsset(stETH, 100e18, 0)` as an unprivileged address. Assert that rsETH minted exceeds the amount that would be minted using the correct current price, and that the per-share NAV of existing holders decreases.