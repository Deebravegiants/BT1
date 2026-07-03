Audit Report

## Title
Missing Chainlink Price Feed Staleness Validation Allows Stale Prices to Corrupt rsETH Rate Computation - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, with no staleness, round-completeness, or positivity checks. A stale Chainlink feed silently returns an outdated price that propagates into `LRTOracle._updateRsETHPrice()`, enabling either a protocol-wide temporary freeze (stale price too low) or unearned fee minting to the treasury (stale price too high), both triggerable by any unprivileged caller via the public `updateRSETHPrice()`.

## Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol` at line 52, `getAssetPrice()` fetches the Chainlink price as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The five return values `(roundId, answer, startedAt, updatedAt, answeredInRound)` are all discarded except `answer`. There is no check that `updatedAt` is within an acceptable heartbeat window, that `answeredInRound >= roundId`, or that `price > 0`.

This oracle is the price source for all supported LST assets. `getAssetPrice()` is called inside `_getTotalEthInProtocol()` at `LRTOracle.sol` line 339, which feeds into `_updateRsETHPrice()` at line 231. `updateRSETHPrice()` at line 87 is `public` with only a `whenNotPaused` guard — any external caller can invoke it.

**Exploit path A — Temporary freeze:**
1. Chainlink stETH/ETH feed goes stale (heartbeat expires, low volatility, or node outage).
2. Any address calls `LRTOracle.updateRSETHPrice()`.
3. `_getTotalEthInProtocol()` returns an understated value using the stale (lower) price.
4. `newRsETHPrice` falls below `highestRsethPrice` by more than `pricePercentageLimit`.
5. Lines 277–281 execute: `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` — all user deposits and withdrawals are frozen.

**Exploit path B — Theft of unclaimed yield:**
1. Chainlink feed freezes at a price higher than the current true price (e.g., after a price peak).
2. Any address calls `updateRSETHPrice()`.
3. `totalETHInProtocol` is overstated; `totalETHInProtocol > previousTVL` is falsely satisfied at line 244.
4. `protocolFeeInETH` is computed on phantom yield at line 246, and rsETH is minted to the treasury at line 306, diluting existing holders.

Existing guards are insufficient: the `pricePercentageLimit` check at line 273 only triggers the pause — it does not prevent the stale price from being accepted. The daily fee mint cap at line 205 limits per-day exposure but does not prevent the issue.

## Impact Explanation

- **High — Theft of unclaimed yield**: A stale high price causes `totalETHInProtocol > previousTVL` to be falsely satisfied, minting unearned rsETH fees to the treasury and diluting all existing rsETH holders' yield.
- **Medium — Temporary freezing of funds**: A stale low price triggers the downside-protection pause at lines 277–281, freezing all deposits and withdrawals until an admin manually unpauses.

## Likelihood Explanation

`updateRSETHPrice()` is public with no access control beyond `whenNotPaused`. Any EOA or contract can call it at any time. Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for ETH/stETH); during low-volatility periods, feeds routinely approach the full heartbeat window without updating. Extended outages have occurred on mainnet. No special privileges, victim mistakes, or external protocol compromise are required — the attacker only needs to call a public function when the feed is stale.

## Recommendation

Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(price > 0, "Invalid price");
require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= MAX_STALENESS_DELAY, "Stale price");
```

`MAX_STALENESS_DELAY` should be set per-feed based on the Chainlink heartbeat (e.g., 3600 seconds for 1-hour feeds, with a small buffer). Consider storing it as a per-asset mapping set by the LRT manager alongside `assetPriceFeed`.

## Proof of Concept

**Scenario A (temporary freeze) — Foundry fork test outline:**
1. Fork mainnet; deploy/configure protocol with `pricePercentageLimit > 0`.
2. `vm.mockCall` on the stETH/ETH Chainlink feed to return a stale `updatedAt` (e.g., `block.timestamp - 2 hours`) with a price 5% below current.
3. Call `lrtOracle.updateRSETHPrice()` from an unprivileged address.
4. Assert `lrtDepositPool.paused() == true`, `withdrawalManager.paused() == true`, `lrtOracle.paused == true`.

**Scenario B (fee theft) — Foundry fork test outline:**
1. Fork mainnet; configure `maxFeeMintAmountPerDay > 0` and `protocolFeeInBPS > 0`.
2. `vm.mockCall` on the stETH/ETH feed to return a stale price 2% above the current true price with an old `updatedAt`.
3. Call `lrtOracle.updateRSETHPrice()` from an unprivileged address.
4. Assert treasury rsETH balance increased and `rsETHPrice` was updated using the inflated TVL.