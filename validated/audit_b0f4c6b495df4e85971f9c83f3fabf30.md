Audit Report

## Title
`RSETHPriceFeed.latestRoundData()` Returns Stale `updatedAt` That Does Not Reflect rsETH Price Freshness — (File: contracts/oracles/RSETHPriceFeed.sol)

## Summary
`RSETHPriceFeed.latestRoundData()` and `getRoundData()` compose `answer` from two independent sources — the ETH/USD Chainlink feed and `LRTOracle.rsETHPrice()` — but return `updatedAt` exclusively from the ETH/USD feed. Because `LRTOracle` stores no timestamp for when `rsETHPrice` was last written, and `RSETHPriceFeed` never queries one, any consumer performing a standard Chainlink staleness check will incorrectly conclude the rsETH/USD price is fresh even when the rsETH/ETH component is arbitrarily old or zero.

## Finding Description
`RSETHPriceFeed.latestRoundData()` (lines 63–70) fetches all five return values from `ETH_TO_USD.latestRoundData()` and then overwrites only `answer`:

```solidity
// contracts/oracles/RSETHPriceFeed.sol L68-69
(roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
```

`updatedAt` is therefore the timestamp of the most recent ETH/USD Chainlink round, which updates on its normal heartbeat (≤1 hour). The rsETH/ETH component comes from `LRTOracle.rsETHPrice` (line 28), a plain `uint256` storage variable with no associated timestamp. It is only updated when `updateRSETHPrice()` (lines 87–89) is explicitly called; that function is permissionless but has no keeper, no Chainlink Automation job, and no on-chain incentive. `LRTOracle` stores no `rsETHPriceLastUpdated` field (confirmed: no such variable exists in the contract). The identical flaw is present in `getRoundData()` (lines 53–61).

Two concrete exploit paths follow:

**Path 1 — Zero price before first update.** `rsETHPrice` is `0` by Solidity default until `updateRSETHPrice()` is called for the first time. `latestRoundData()` returns `answer = 0 * ethPrice / 1e18 = 0` while `updatedAt` reflects a recent ETH/USD round. A lending protocol whose only guard is `require(updatedAt >= block.timestamp - 3600)` passes the staleness check and sees rsETH worth $0, triggering mass liquidation of all rsETH-collateralised positions or freezing rsETH as collateral.

**Path 2 — Stale rsETH/ETH rate.** After a slashing or depeg event, `updateRSETHPrice()` is not called for several hours. ETH/USD continues to update normally, so `updatedAt` from `latestRoundData()` is always within the staleness window. A lending protocol accepts the inflated rsETH/USD price; borrowers draw excess debt against rsETH collateral. When `updateRSETHPrice()` is eventually called and the price corrects, those positions are undercollateralised and liquidated, with borrowers having extracted value at the expense of the protocol's liquidity providers.

Existing checks are insufficient: `whenNotPaused` on `updateRSETHPrice()` only prevents calls when the oracle is paused; it does not guarantee timely updates. There is no on-chain mechanism that bounds the age of `rsETHPrice`.

## Impact Explanation
The zero-price path directly causes **temporary freezing of funds** (rsETH collateral frozen or mass liquidations triggered by a $0 price) — a confirmed Medium impact. The stale-inflated-price path enables **direct theft of user funds** via forced liquidation of undercollateralised positions after the price corrects — a Critical impact. Both paths are reachable by any unprivileged external caller interacting with an integrated lending market; no privileged access is required.

## Likelihood Explanation
The zero-price scenario is reachable during any fresh deployment before the first `updateRSETHPrice()` call — a routine operational window. The stale-price scenario requires only that the permissionless keeper fails to call `updateRSETHPrice()` for longer than the integrating protocol's staleness window; network congestion, a keeper outage, or a protocol pause (which blocks `updateRSETHPrice()` via `whenNotPaused`) is sufficient. Both conditions are realistic and repeatable. Likelihood is **Medium**.

## Recommendation
1. Add `uint256 public rsETHPriceLastUpdated` to `LRTOracle` and set it to `block.timestamp` inside `_updateRsETHPrice()` at the point where `rsETHPrice` is written (line 313).
2. Expose `rsETHPriceLastUpdated` via the `ILRTOracle` interface so `RSETHPriceFeed` can read it.
3. In `RSETHPriceFeed.latestRoundData()` and `getRoundData()`, replace the returned `updatedAt` with `min(ethFeedUpdatedAt, RS_ETH_ORACLE.rsETHPriceLastUpdated())` so any consumer's staleness check reflects the freshness of both components.
4. Revert (or return a sentinel that downstream protocols will reject) when `RS_ETH_ORACLE.rsETHPrice() == 0` to prevent the zero-price scenario from propagating silently.

## Proof of Concept
**Zero-price path (Foundry fork test outline):**
1. Deploy `LRTOracle` (proxy); do not call `updateRSETHPrice()`. `rsETHPrice` is `0`.
2. Deploy `RSETHPriceFeed` pointing at the live Chainlink ETH/USD feed and the `LRTOracle` proxy.
3. Call `RSETHPriceFeed.latestRoundData()`. Assert `answer == 0` and `updatedAt >= block.timestamp - 3600` (staleness check passes).
4. Demonstrate that a lending protocol gated only on `updatedAt` would accept the $0 price.

**Stale-price path (Foundry fork test outline):**
1. Call `updateRSETHPrice()` at block T; record `rsETHPrice = P`.
2. `vm.warp(block.timestamp + 6 hours)`. Do not call `updateRSETHPrice()` again.
3. Call `RSETHPriceFeed.latestRoundData()`. Assert `updatedAt` is within the last hour (ETH/USD heartbeat) while `rsETHPrice` is still `P` from step 1.
4. Show that a `require(updatedAt >= block.timestamp - 3600)` staleness guard passes, accepting the 6-hour-old rsETH/ETH rate as current.