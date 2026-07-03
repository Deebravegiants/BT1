Audit Report

## Title
Unguarded `latestRoundData()` in `ChainlinkPriceOracle.getAssetPrice()` Freezes Deposits and Withdrawals on Feed Failure - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` with no `try/catch`, no zero/negative price guard, and no staleness check. If a Chainlink feed reverts (e.g., due to deprecation or a pause), every user-facing operation that depends on that price — `depositAsset`, `depositETH`, `initiateWithdrawal`, and `instantWithdrawal` — reverts for all users of that asset. The same project already applies proper guards in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, confirming awareness of the pattern.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` at lines 49–55 performs a bare external call:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

There is no `try/catch`, no `price > 0` check, and no `updatedAt` staleness guard. Contrast this with `ChainlinkOracleForRSETHPoolCollateral.getRate()` (lines 26–37), which checks `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` before proceeding.

The unguarded call propagates into all critical user paths:

- **Deposit**: `depositAsset`/`depositETH` → `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()`.
- **Withdrawal initiation**: `initiateWithdrawal` → `getExpectedAssetAmount` → `lrtOracle.getAssetPrice(asset)`.
- **Instant withdrawal**: `instantWithdrawal` → `getExpectedAssetAmount` → `lrtOracle.getAssetPrice(asset)`.
- **rsETH price update**: `updateRSETHPrice` → `_getTotalEthInProtocol` iterates all supported assets and calls `getAssetPrice(asset)` for each; a single failing feed blocks the price update.

Additionally, if `price` returns `0`, `getExpectedAssetAmount` computes `amount * rsETHPrice / 0`, causing a division-by-zero revert in the withdrawal path.

## Impact Explanation

If any supported LST's Chainlink feed reverts (paused, deprecated, or returning zero), all deposits and withdrawal initiations for that asset revert. Users holding rsETH backed by that asset cannot initiate new withdrawals or use instant withdrawal until an admin manually replaces the oracle via `updatePriceFeedFor`. This constitutes **temporary freezing of funds**, matching the Medium impact tier. If the feed is permanently deprecated and no admin action is taken, the freeze becomes permanent (Critical).

## Likelihood Explanation

Chainlink has a documented history of pausing or deprecating feeds during extreme market events (e.g., UST/ETH during the Terra collapse). The protocol supports multiple LST assets (stETH, ETHx, etc.), each with its own Chainlink feed. Any single feed going offline triggers the freeze for that asset's users. No attacker action is required — the trigger is an external Chainlink operational event, which is precedented and realistic. Any unprivileged user attempting a deposit or withdrawal at that moment will be affected.

## Recommendation

1. Wrap `latestRoundData()` in a `try/catch` and revert with a descriptive error (e.g., `OracleCallFailed()`) rather than propagating the Chainlink revert.
2. Add a zero/negative price check: `if (price <= 0) revert InvalidPrice();`.
3. Add a staleness check: `if (block.timestamp - updatedAt > maxStaleness) revert StalePrice();`.
4. Mirror the pattern already used in `ChainlinkOracleForRSETHPoolCollateral.getRate()` (lines 30–32).

## Proof of Concept

1. Chainlink pauses or deprecates the stETH/ETH feed; `latestRoundData()` begins reverting.
2. User calls `depositAsset(stETH, amount, minRSETH, "")`.
3. Execution: `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `priceFeed.latestRoundData()` → **reverts**.
4. All subsequent `depositAsset` calls for stETH revert.
5. Simultaneously, `initiateWithdrawal(stETH, rsETHAmount, "")` → `getExpectedAssetAmount` → `lrtOracle.getAssetPrice(stETH)` → same revert.
6. `instantWithdrawal(stETH, rsETHAmount, "")` → `getExpectedAssetAmount` → same revert.
7. Users holding rsETH backed by stETH cannot deposit, initiate withdrawals, or use instant withdrawal until an admin calls `updatePriceFeedFor` with a working feed.

**Foundry fork test plan**: Fork mainnet, use `vm.mockCallRevert` on the stETH/ETH Chainlink aggregator's `latestRoundData()` selector, then call `depositAsset` and `initiateWithdrawal` — both should revert, confirming the freeze.