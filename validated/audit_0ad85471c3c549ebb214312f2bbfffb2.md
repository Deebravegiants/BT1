Audit Report

## Title
Stale `rsETHPrice` Served as Fresh via `RSETHPriceFeed.latestRoundData` After Auto-Pause — (`contracts/oracles/RSETHPriceFeed.sol`)

## Summary

When `LRTOracle._updateRsETHPrice()` detects a price drop exceeding `pricePercentageLimit`, it pauses the protocol and returns early at line 281 — before the `rsETHPrice = newRsETHPrice` assignment at line 313. `RSETHPriceFeed.latestRoundData()` then serves this stale, inflated `rsETHPrice` paired with a fresh `updatedAt` timestamp sourced from the ETH/USD Chainlink feed, causing downstream lending protocols (e.g., Aave) to accept the stale price as current and allow over-borrowing against rsETH collateral.

## Finding Description

**Root cause — early `return` before price write:**

In `_updateRsETHPrice()`, when `isPriceDecreaseOffLimit` is true, the function pauses the protocol and returns at line 281:

```solidity
// LRTOracle.sol L277-282
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;   // ← exits before rsETHPrice = newRsETHPrice at L313
}
``` [1](#0-0) 

The assignment `rsETHPrice = newRsETHPrice` at line 313 is never reached, so the storage variable retains the pre-pause inflated value. [2](#0-1) 

**`updateRSETHPriceAsManager()` cannot recover the price either:**

`updateRSETHPriceAsManager()` (line 94) omits `whenNotPaused` and calls `_updateRsETHPrice()` directly, but as long as the TVL remains depressed (i.e., `isPriceDecreaseOffLimit` stays true), every invocation hits the same early `return`, keeping `rsETHPrice` frozen at the stale value. [3](#0-2) 

**`RSETHPriceFeed.latestRoundData()` blindly reads the stale value with a fresh timestamp:**

```solidity
// RSETHPriceFeed.sol L68-69
(roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
``` [4](#0-3) 

There is no staleness check on `RS_ETH_ORACLE.rsETHPrice()`. The `updatedAt` field is sourced entirely from the ETH/USD Chainlink heartbeat (typically ≤1 hour old), so external protocols' staleness guards pass even though the rsETH/ETH component has not been updated since the auto-pause.

## Impact Explanation

An attacker holding rsETH can deposit it as collateral on Aave (or any protocol consuming `RSETHPriceFeed`) and borrow against the stale, inflated rsETH/USD price. Because the real value of rsETH has dropped (e.g., 20–25%), the attacker extracts more debt than the collateral is worth, then walks away. The lending protocol is left with undercollateralized positions — **protocol insolvency** for any integration consuming this feed. This matches the Critical allowed impact: **Protocol insolvency**.

## Likelihood Explanation

The precondition (TVL drop exceeding `pricePercentageLimit`) is realistic: a slashing event on an underlying EigenLayer operator or a significant price drop in a supported LST (stETH, cbETH) can trigger it. `updateRSETHPrice()` is `public` with only a `whenNotPaused` guard — any unprivileged caller can invoke it once the TVL condition is met. The attacker requires no privileged role; they only need to observe on-chain state and act within the window before the price recovers.

## Recommendation

1. **Track a `rsETHPriceUpdatedAt` timestamp** in `LRTOracle` and update it every time `rsETHPrice` is written. Have `RSETHPriceFeed.latestRoundData()` return `min(ethUsdUpdatedAt, rsETHPriceUpdatedAt)` as `updatedAt`, so downstream protocols see the true composite staleness.
2. **Allow downward price writes during auto-pause** so the stored value reflects reality. The auto-pause is a circuit breaker for deposits/withdrawals, not a justification for freezing the price feed at an inflated level.
3. Alternatively, have `RSETHPriceFeed.latestRoundData()` revert (or return `updatedAt = 0`) when `LRTOracle` is paused, so downstream protocols treat the feed as unavailable rather than stale-but-fresh.

## Proof of Concept

```solidity
// Fork mainnet. Deploy/configure RSETHPriceFeed pointing at LRTOracle.

// 1. Record pre-pause price
uint256 stalePre = lrtOracle.rsETHPrice(); // e.g. 1.05e18

// 2. Simulate TVL drop > pricePercentageLimit (mock asset oracle returns lower value)
mockAssetOracle.setPrice(originalPrice * 75 / 100); // -25%

// 3. Anyone calls updateRSETHPrice() — triggers auto-pause, returns early
lrtOracle.updateRSETHPrice();
assert(lrtOracle.paused() == true);
assert(lrtOracle.rsETHPrice() == stalePre); // price NOT updated — confirmed by L281 early return

// 4. RSETHPriceFeed still returns the stale inflated price
(, int256 answer,, uint256 updatedAt,) = rsethPriceFeed.latestRoundData();
// updatedAt is from ETH/USD feed — within last hour, passes Aave's staleness check
// answer reflects stalePre * ethUsdPrice / 1e18 — inflated by ~25%

// 5. Attacker deposits rsETH on Aave, borrows at inflated price
// Undercollateralization ratio = 1.25x → attacker extracts 25% more debt than collateral value
// Aave left with bad debt → insolvency
```

### Citations

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L277-282)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/oracles/RSETHPriceFeed.sol (L68-69)
```text
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
```
