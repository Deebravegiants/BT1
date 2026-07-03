Audit Report

## Title
Missing Staleness Check on Chainlink Price Feed Allows Stale Prices to Drive Incorrect rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards `updatedAt` and `answeredInRound`, performing no time-based or round-based staleness validation. A stale Chainlink LST/ETH price feed (e.g., during a depeg event where the oracle lags at an inflated price) is accepted without revert and propagated directly into rsETH minting calculations, allowing a depositor to receive more rsETH than the deposited asset is worth and diluting all existing rsETH holders.

## Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol` at line 52, `getAssetPrice()` captures only the `price` field from `latestRoundData()`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

`updatedAt` (position 4) and `answeredInRound` (position 5) are both discarded. No check of the form `block.timestamp - updatedAt > heartbeat` is performed, and no `answeredInRound < roundId` guard is applied.

This price flows directly into `LRTOracle.getAssetPrice()` (line 157 of `contracts/LRTOracle.sol`), which delegates to the registered `IPriceFetcher` without any additional staleness gate. `LRTDepositPool.getRsETHAmountToMint()` (line 520 of `contracts/LRTDepositPool.sol`) then uses this price:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

This value is consumed by `_beforeDeposit()` (line 665) and ultimately drives `_mintRsETH()` (line 689), minting rsETH directly to the depositor.

The sibling contract `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` (lines 30–31) applies both `answeredInRound < roundID` and `timestamp == 0` checks, confirming the protocol is aware of the staleness-check pattern but failed to apply it in `ChainlinkPriceOracle`. Notably, even the sibling contract omits a time-based heartbeat check, but `ChainlinkPriceOracle` omits all staleness validation entirely.

Existing guards in `_beforeDeposit()` (deposit amount limits, minimum rsETH slippage) do not constrain the oracle price and are insufficient to prevent this exploit.

## Impact Explanation
If a Chainlink LST/ETH feed (e.g., stETH/ETH, rETH/ETH) goes stale at a price inflated relative to the actual current market price — a realistic scenario during an LST depeg event where the oracle lags — `getAssetPrice()` returns the stale high price without reverting. A depositor calling `depositAsset()` at that moment receives more rsETH than the deposited asset is actually worth. This over-issuance dilutes the rsETH holdings of all existing holders, constituting **theft of unclaimed yield** (High severity).

## Likelihood Explanation
Chainlink LST/ETH feeds carry 24-hour heartbeats and 0.5% deviation thresholds. During periods of network congestion, oracle node failures, or rapid LST price movement (depeg), the feed can lag beyond the heartbeat window. This is a well-documented, recurring risk class for Chainlink integrations. The entry path (`depositAsset`) is fully permissionless — no special role, no admin action, and no oracle operator compromise is required. Any external user can exploit this condition whenever the feed is stale.

## Recommendation
Add both a round-based and a time-based staleness check in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (answeredInRound < roundId) revert StalePrice();
if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice();
if (price <= 0) revert InvalidPrice();
```

`STALENESS_THRESHOLD` should be set per feed based on its documented heartbeat (e.g., 24 hours + a small buffer). Apply the same pattern to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which currently lacks the time-based check.

## Proof of Concept
1. Chainlink stETH/ETH feed last updated at `T - 25h` (heartbeat exceeded). Feed price is `1.01e18` (stale high; actual market is `0.99e18` due to a depeg).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.
3. `getRsETHAmountToMint(stETH, 100e18)` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns `1.01e18` (no revert).
4. `rsethAmountToMint = (100e18 * 1.01e18) / rsETHPrice` — attacker receives ~2% more rsETH than the deposited stETH is actually worth.
5. Existing rsETH holders are diluted; the attacker has extracted yield at their expense.
6. No admin action, no special role, no oracle operator compromise required.

**Foundry fork test plan**: Fork mainnet at a block where the stETH/ETH Chainlink feed's `updatedAt` is >24h behind `block.timestamp`. Call `depositAsset` with stETH and assert that `rsethAmountToMint` exceeds the fair value computed using the actual on-chain stETH/ETH spot rate, confirming over-issuance without revert.