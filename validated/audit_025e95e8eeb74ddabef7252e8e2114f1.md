Audit Report

## Title
Missing Chainlink Staleness Validation Enables Stale-Price-Triggered Auto-Pause, Freezing Withdrawals and Fee Minting — (`contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice` silently discards `updatedAt` and `answeredInRound` from `latestRoundData`, accepting any stale price without validation. When a Chainlink feed goes stale, the understated LST price causes `_updateRsETHPrice` to compute a `newRsETHPrice` below `highestRsethPrice` by more than `pricePercentageLimit`, triggering an auto-pause of the deposit pool, withdrawal manager, and oracle itself. The public `updateRSETHPrice()` function can be called by any unprivileged address to fire this pause once the feed is stale.

## Finding Description

**Root cause — no staleness check in `ChainlinkPriceOracle.getAssetPrice`:**

`contracts/oracles/ChainlinkPriceOracle.sol` line 52 discards all fields except `answer`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

The full return tuple is `(roundId, answer, startedAt, updatedAt, answeredInRound)`. There is no `require(updatedAt >= block.timestamp - maxStaleness)` or `require(answeredInRound >= roundId)` guard anywhere in the call chain.

**Propagation to auto-pause:**

`_getTotalEthInProtocol` (LRTOracle.sol L336–343) calls `getAssetPrice` for every supported asset. LST assets (stETH, cbETH, etc.) accrue value continuously. A stale feed returns the last-known (lower) price, understating `totalETHInProtocol`.

`_updateRsETHPrice` (LRTOracle.sol L270–282) then computes `newRsETHPrice` from that understated total and compares it against `highestRsethPrice`. If the difference exceeds `pricePercentageLimit`, it pauses all three contracts and returns early — `rsETHPrice` is never updated and `IRSETH.mint` is never reached:

```solidity
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;   // rsETHPrice not updated; fee not minted
}
```

`updateRSETHPrice()` (LRTOracle.sol L87) is public and gated only by `whenNotPaused`, so any unprivileged EOA can call it to trigger the pause once the feed is stale. `updateRSETHPriceAsManager()` bypasses the `whenNotPaused` guard but still hits the same early-return branch while the oracle is stale, so it cannot un-pause the deposit pool or withdrawal manager.

**Why existing checks are insufficient:**

- `pricePercentageLimit > 0` guard only prevents the pause when the limit is unset (zero); once configured, it is the trigger condition, not a protection.
- `_pause()` has an idempotency guard (`if (paused) return`) but does not prevent the deposit pool and withdrawal manager from being paused.
- Recovery requires explicit `onlyLRTAdmin` `unpause()` calls on three separate contracts, plus the oracle feed must be live again before `updateRSETHPrice()` can succeed without re-triggering the same pause.

## Impact Explanation

**Temporary freezing of funds (Medium).** Once the auto-pause fires, `withdrawalManager` is paused, blocking all pending withdrawal claims until an admin manually unpauses all three contracts and the oracle feed is live. Protocol fee minting is also blocked for the duration of the pause; however, because `rsETHPrice` is not updated during the pause (early return), the full LST appreciation is captured in the next successful fee mint after recovery, so unclaimed yield is not permanently lost. The primary concrete impact is temporary freezing of user withdrawal claims.

## Likelihood Explanation

`updateRSETHPrice()` is a public, permissionless function — no privileged role is required to trigger the pause. The required staleness duration depends on `pricePercentageLimit` and LST APY: for a 1% limit and 5% APY, approximately 73 days of feed staleness is needed; for a 5% limit, approximately 365 days. Extended staleness of this magnitude is unlikely for a properly maintained Chainlink feed under normal conditions. However, the threshold is reached immediately if the last captured round price reflects a depeg or sharp deviation event, making the depeg scenario the more realistic trigger. No oracle operator compromise is required — normal Chainlink liveness failure or a prior depeg round is sufficient.

## Recommendation

Add staleness and round-completeness checks in `ChainlinkPriceOracle.getAssetPrice` (`contracts/oracles/ChainlinkPriceOracle.sol`):

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale round");
require(updatedAt >= block.timestamp - maxStaleness, "Stale price");
require(price > 0, "Non-positive price");
```

Store a per-feed `maxStaleness` value in `ChainlinkPriceOracle` alongside `assetPriceFeed`, configurable by `onlyLRTManager`. Typical values: 3600 s for ETH/USD, 86 400 s for slower LST feeds.

## Proof of Concept

```solidity
// Foundry fork test outline
function testStaleOracleTriggersAutoPause() public {
    // 1. Fork mainnet at block B where stETH/ETH feed was last updated at T0
    // 2. vm.warp(T0 + 74 days);  // feed is now stale beyond 1% APY threshold
    // 3. Call lrtOracle.updateRSETHPrice() as an unprivileged EOA
    // 4. Assert lrtDepositPool.paused() == true
    // 5. Assert withdrawalManager.paused() == true
    // 6. Assert lrtOracle.paused() == true
    // 7. Assert lrtOracle.updateRSETHPrice() reverts with ContractPaused
    // 8. Assert pending withdrawal claims revert
}
```

For the immediate-trigger (depeg) variant: fork at a block where the last captured stETH/ETH round reflects a depeg event, warp forward by any amount, and call `updateRSETHPrice()`. The stale depeg price will be below `highestRsethPrice` by more than `pricePercentageLimit` immediately.