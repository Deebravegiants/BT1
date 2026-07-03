Audit Report

## Title
Missing Staleness Validation in Chainlink Price Feed Allows Over-Minting of rsETH — (`contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all staleness-related return values (`updatedAt`, `answeredInRound`), accepting stale prices without any freshness check. When a supported LST's Chainlink feed is stale at an inflated price, any depositor can call `depositAsset()` and receive more rsETH than the deposited collateral is worth, diluting the rsETH/ETH exchange rate for all existing holders.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the price as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` is bound; `updatedAt` and `answeredInRound` are silently discarded. There is no check of the form `answeredInRound >= roundId` (round completeness) or `block.timestamp - updatedAt <= heartbeat` (price freshness).

The sibling contract `ChainlinkOracleForRSETHPoolCollateral.getRate()` performs exactly these checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle` has no equivalent guard, demonstrating an inconsistency in the protocol's own oracle safety standards.

The stale price flows into two critical paths:

**Path 1 — rsETH minting:** `LRTDepositPool.getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)` directly:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

`rsETHPrice` is a stored state variable updated separately via `updateRSETHPrice()`. At deposit time, `getAssetPrice(asset)` is fetched live from the stale feed while `rsETHPrice` reflects the last update — the numerator is inflated, the denominator is not, so the depositor receives excess rsETH.

**Path 2 — rsETH price update:** `LRTOracle._getTotalEthInProtocol()` sums `getAssetPrice(asset)` across all supported assets to compute `newRsETHPrice`: [4](#0-3) 

A stale inflated price here also inflates the computed TVL, potentially triggering incorrect fee minting.

## Impact Explanation

When a supported LST's Chainlink feed is stale at a price higher than the real market price, a depositor receives more rsETH than the deposited collateral is worth. The excess rsETH represents a claim on protocol ETH that was not contributed, directly diluting the redemption value of all existing rsETH holders. This constitutes **theft of unclaimed yield** from existing rsETH holders (High severity). The magnitude scales with the price deviation and deposit size; a 5–10% deviation on a large deposit causes proportional yield theft from all holders.

## Likelihood Explanation

Chainlink feeds become stale during L1 gas spikes (preventing oracle keeper transactions), Chainlink node outages, or rapid market moves that temporarily outpace the deviation threshold. These are documented, recurring real-world conditions. The affected `ChainlinkPriceOracle` is the primary price oracle for all LSTs in the protocol. Any staleness window is exploitable by any unprivileged depositor who monitors on-chain oracle state — no special access or governance role is required. The attack is repeatable for the duration of the staleness window.

## Recommendation

Add staleness validation in `ChainlinkPriceOracle.getAssetPrice()`, consistent with the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale price: round not complete");
require(updatedAt != 0, "Stale price: incomplete round");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price: price too old");
require(price > 0, "Invalid price");
```

`MAX_STALENESS` should be configured per-feed based on the Chainlink heartbeat (e.g., 3600 s for ETH/USD, 86400 s for some LST feeds). Consider storing it as a per-asset mapping alongside `assetPriceFeed`.

## Proof of Concept

1. Deploy a fork of mainnet with a supported LST (e.g., stETH) whose Chainlink feed has not been updated for > heartbeat seconds (simulate by warping `block.timestamp` forward or by mocking `latestRoundData()` to return a stale `updatedAt`).
2. Record the current `rsETHPrice` from `LRTOracle`.
3. Call `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")` as an unprivileged attacker.
4. Observe that `getRsETHAmountToMint()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns the stale inflated price (e.g., `1.05e18`) without revert.
5. Attacker receives `1000 * 1.05e18 / rsETHPrice` rsETH — more than the fair `1000 * realPrice / rsETHPrice`.
6. Call `LRTOracle.updateRSETHPrice()` after the oracle recovers; the new `rsETHPrice` is lower than it would have been without the over-mint, confirming dilution of existing holders.

Foundry fork test: mock `latestRoundData()` on the stETH price feed to return `updatedAt = block.timestamp - 2 hours` with `answeredInRound < roundId`, assert no revert occurs in `getAssetPrice`, and assert the minted rsETH amount exceeds the fair value computed using the real current price.

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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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
