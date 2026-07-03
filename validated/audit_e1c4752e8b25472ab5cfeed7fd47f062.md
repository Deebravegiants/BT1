Audit Report

## Title
Unbounded Gas Consumption in Public `updateRSETHPrice()` via Nested External Calls Across Assets × NDCs × Queued Withdrawals — (File: `contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

## Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function whose gas cost scales as `O(supportedAssets × NDCs × queuedWithdrawals × strategiesPerWithdrawal)` through a chain of nested external calls. The protocol's own soft cap on withdrawals (`maxUncompletedWithdrawalCount ≤ 80`) does not bound the actual number of withdrawals visible to `getQueuedWithdrawals()`, because EigenLayer operator-forced undelegations queue withdrawals entirely outside the protocol's tracking. The codebase explicitly acknowledges this scenario. If the total queued withdrawal count across all NDCs grows large enough, `updateRSETHPrice()` will exceed the block gas limit and become permanently uncallable.

## Finding Description

The full call chain is confirmed in the code:

1. `updateRSETHPrice()` (`LRTOracle.sol:87`) calls `_updateRsETHPrice()` which calls `_getTotalEthInProtocol()` (`LRTOracle.sol:331`).
2. `_getTotalEthInProtocol()` loops over every entry in `supportedAssets` and calls `ILRTDepositPool.getTotalAssetDeposits(asset)` per asset (`LRTOracle.sol:336–341`).
3. `getTotalAssetDeposits()` calls `getAssetDistributionData()` (`LRTDepositPool.sol:385–396`), which loops over every NDC in `nodeDelegatorQueue` and calls `INodeDelegator(ndc).getAssetUnstaking(asset)` per NDC (`LRTDepositPool.sol:446–456`). For ETH, `getETHDistributionData()` performs the same loop (`LRTDepositPool.sol:484–493`).
4. `getAssetUnstaking(asset)` (`NodeDelegator.sol:405–427`) calls `DelegationManager.getQueuedWithdrawals(address(this))` — an external call that returns **all** queued withdrawals for that NDC — then iterates over every withdrawal and every strategy within each withdrawal, making an additional external call to `strategy.sharesToUnderlyingView()` for non-ETH assets.

The total number of `getQueuedWithdrawals()` external calls equals `supportedAssets × NDCs`. With 5 assets and 10 NDCs, that is 50 external calls to EigenLayer, each returning up to 80+ withdrawal structs, each of which may contain multiple strategies requiring further external calls.

The protocol's `maxUncompletedWithdrawalCount` (capped at 80 by `setMaxUncompletedWithdrawalCount`) tracks only withdrawals initiated through the protocol's own `initiateUnstaking()` and `undelegate()` flows. EigenLayer operators can force undelegations that queue additional withdrawals directly in EigenLayer's `DelegationManager`, bypassing the protocol's counter entirely. The comment at `LRTUnstakingVault.sol:151–152` explicitly acknowledges this: *"120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price / Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)"*. This confirms the protocol is aware that forced undelegations can push the real queued withdrawal count beyond the soft cap.

There is no cooldown, rate limit, or access control on `updateRSETHPrice()` beyond `whenNotPaused`.

## Impact Explanation

**Medium — Unbounded gas consumption.** At maximum configured bounds (10 NDCs × 5 assets × 80+ withdrawals × multiple strategies), each invocation of `updateRSETHPrice()` executes hundreds of external calls. If forced undelegations push the per-NDC queued withdrawal count beyond the protocol's soft cap, the cumulative gas cost can exceed Ethereum's ~30M block gas limit. Once this threshold is crossed, `updateRSETHPrice()` becomes permanently uncallable, the stored `rsETHPrice` becomes stale, and the fee-minting and downside-protection pause mechanisms that depend on `_updateRsETHPrice()` stop functioning. This matches the explicitly listed allowed impact: **Medium. Unbounded gas consumption.**

## Likelihood Explanation

**Low-to-Medium.** Under normal operating conditions with few NDCs and assets, gas cost is manageable. However, the function is callable by any address with zero privilege; EigenLayer operator-forced undelegations are an explicitly acknowledged scenario in the codebase and are entirely outside the protocol's control; and as the protocol scales (more NDCs, more assets, more concurrent withdrawals), the gas cost grows multiplicatively. No rate limiting exists to prevent repeated calls.

## Recommendation

1. **Decouple `getAssetUnstaking()` from the price-update hot path.** Maintain a separately updated accounting variable for queued withdrawal amounts (updated by operators via a privileged function) rather than iterating over EigenLayer's live withdrawal queue on every price update.
2. **Cache per-NDC results.** Since `getQueuedWithdrawals(ndc)` is called once per asset per NDC, cache the result for each NDC and filter by asset in a single pass, reducing `getQueuedWithdrawals()` calls from `assets × NDCs` to `NDCs`.
3. **Add an explicit iteration cap** in `getAssetUnstaking()` to prevent a single forced-undelegation event from making the function uncallable.
4. **Add a cooldown / rate limit** on `updateRSETHPrice()` (e.g., one call per block) to prevent repeated invocations by unprivileged callers.

## Proof of Concept

```solidity
// Any external address can call this with no restriction (only whenNotPaused):
ILRTOracle(oracleAddress).updateRSETHPrice();

// Internally resolves to (confirmed by code):
// _getTotalEthInProtocol() [LRTOracle.sol:331]:
//   for each asset in supportedAssets (e.g., 5 assets) [LRTOracle.sol:336]:
//     getTotalAssetDeposits(asset) -> getAssetDistributionData(asset) [LRTDepositPool.sol:385]:
//       for each ndc in nodeDelegatorQueue (e.g., 10 NDCs) [LRTDepositPool.sol:447]:
//         ndc.getAssetUnstaking(asset) [NodeDelegator.sol:405]:
//           DelegationManager.getQueuedWithdrawals(ndc)  // external call
//           for each withdrawal in queuedWithdrawals (e.g., 80 protocol + N forced):
//             for each strategy in withdrawal.strategies:
//               strategy.sharesToUnderlyingView(shares)  // external call
//
// Worst-case (5 assets × 10 NDCs × 95 withdrawals × 3 strategies):
//   = 50 getQueuedWithdrawals() calls + 14,250 sharesToUnderlyingView() calls
//   At ~2,500 gas per STATICCALL: ~35M gas — exceeds the 30M block gas limit.
//
// Forced undelegation scenario (acknowledged in LRTUnstakingVault.sol:151-152):
//   An EigenLayer operator forces undelegation on all 10 NDCs, adding 15 extra
//   withdrawals outside the protocol's uncompletedWithdrawalCount tracking.
//   This pushes total queued withdrawals per NDC above the threshold at which
//   updateRSETHPrice() can no longer execute within the block gas limit.
```

A Foundry fork test can reproduce this by deploying the protocol against a mainnet fork, populating 10 NDCs each with 80 queued withdrawals via `initiateUnstaking()`, then simulating forced undelegations by directly calling EigenLayer's `DelegationManager.undelegate()` on each NDC from the operator address, and measuring the gas consumed by `updateRSETHPrice()`.