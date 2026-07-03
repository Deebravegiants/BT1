Audit Report

## Title
Unbounded Nested Loops in `getAssetDistributionData` and `_getTotalEthInProtocol` Cause OOG, Temporarily Freezing Deposits and Price Updates - (File: contracts/LRTDepositPool.sol, contracts/LRTOracle.sol)

## Summary
`LRTDepositPool.getAssetDistributionData()` and `LRTOracle._getTotalEthInProtocol()` contain nested unbounded loops that, for each NDC in `nodeDelegatorQueue`, call `NodeDelegator.getAssetUnstaking()`, which itself iterates over all queued EigenLayer withdrawals and their strategies fetched live from `DelegationManager.getQueuedWithdrawals()`. As the `queuedWithdrawals` array grows through routine operator `initiateUnstaking()` calls, the cumulative gas cost of these nested loops can exceed the block gas limit, causing `depositETH()`, `depositAsset()`, and the public `updateRSETHPrice()` to revert with out-of-gas.

## Finding Description
**Deposit path:** `depositETH()` / `depositAsset()` call `_beforeDeposit()`, which invokes `getTotalAssetDeposits()` → `getAssetDistributionData()`. Inside `getAssetDistributionData()`, a loop over `nodeDelegatorQueue` calls `INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset)` for every NDC:

```solidity
// LRTDepositPool.sol L446-456
uint256 ndcsCount = nodeDelegatorQueue.length;
for (uint256 i; i < ndcsCount;) {
    assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
    assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    unchecked { ++i; }
}
```

Each `getAssetUnstaking()` call fetches the full `queuedWithdrawals` array live from EigenLayer's `DelegationManager` and iterates over it with a nested strategy loop:

```solidity
// NodeDelegator.sol L405-427
(IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
    _getDelegationManager().getQueuedWithdrawals(address(this));
for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
    for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) { ... }
}
```

The `queuedWithdrawals` array is unbounded — it grows with every `initiateUnstaking()` call and shrinks only when `completeUnstaking()` is called.

**Price update path:** `updateRSETHPrice()` (public, only `whenNotPaused`) → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` loops over all supported assets and calls `getTotalAssetDeposits(asset)` for each, triggering the full NDC × queued-withdrawal nested loop per asset. This creates a quadruple-nested loop: `supportedAssets.length × nodeDelegatorQueue.length × queuedWithdrawals.length × strategies.length`, with each inner iteration performing external storage reads against `DelegationManager`.

No gas limit checks, pagination, or caching exist anywhere in this call chain. The `maxNodeDelegatorLimit` is initialized to 10, bounding the NDC count, but `queuedWithdrawals` per NDC is entirely unbounded.

## Impact Explanation
**Unbounded gas consumption (Medium):** The nested loop gas cost grows without bound as `queuedWithdrawals` accumulates. **Temporary freezing of funds (Medium):** When the gas cost exceeds the block gas limit, every call to `depositETH()` and `depositAsset()` reverts, preventing users from depositing. Simultaneously, `updateRSETHPrice()` reverts, leaving `rsETHPrice` stale and causing mispricing of new deposits and withdrawals. Both impacts are in the allowed scope.

## Likelihood Explanation
`initiateUnstaking()` is a routine operator operation triggered during validator exits and operator undelegation. With `maxNodeDelegatorLimit = 10` NDCs and even 20–30 queued withdrawals per NDC (each with 2 strategies), the gas cost of the nested loop across 3 supported assets becomes prohibitive. This is a realistic operational scenario during periods of high unstaking activity, not a theoretical edge case. The trigger functions (`depositETH`, `depositAsset`, `updateRSETHPrice`) are callable by any unprivileged user.

## Recommendation
1. **Cache `assetUnstaking` off-chain:** Store a per-asset unstaking amount updated by the operator via a privileged setter, rather than computing it live on every deposit and price-update call. The live computation can remain available as a view-only function.
2. **Paginate `getAssetDistributionData`:** Accept `from`/`to` index parameters for the NDC loop to allow partial computation.
3. **Decouple price update from full TVL scan:** Store per-asset TVL snapshots updated incrementally rather than recomputing the full sum on every `updateRSETHPrice()` call.

## Proof of Concept
1. Protocol has 3 supported assets, 5 NDCs (`nodeDelegatorQueue.length = 5`, within `maxNodeDelegatorLimit = 10`).
2. Operator calls `initiateUnstaking()` repeatedly; each NDC accumulates 30 queued withdrawals with 2 strategies each → 60 strategy iterations per NDC per asset.
3. User calls `depositETH(...)`.
4. Execution: `_beforeDeposit` → `getTotalAssetDeposits(ETH)` → `getETHDistributionData()` → loop over 5 NDCs → each NDC calls `getAssetUnstaking(ETH)` → fetches 30 withdrawals × 2 strategies = 60 iterations per NDC → 300 total inner iterations, each with external `DelegationManager` storage reads.
5. For `updateRSETHPrice()`: outer loop runs for 3 assets, each triggering the same 300-iteration inner loop → 900 total inner iterations plus 15 `getAssetBalance()` external calls.
6. At sufficient scale, both transactions revert with out-of-gas.

**Foundry fork test plan:**
- Fork mainnet/testnet with a deployed instance.
- Register 5 NDCs and queue 30 withdrawals per NDC via `initiateUnstaking()`.
- Call `depositETH{value: 1 ether}(0, "")` and `updateRSETHPrice()` with a fixed gas limit matching the block gas limit.
- Assert both revert with out-of-gas.