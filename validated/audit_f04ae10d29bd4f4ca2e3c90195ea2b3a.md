Audit Report

## Title
Unbounded Nested Loop in `NodeDelegator.getAssetUnstaking()` Propagates to All User-Facing Entry Points — (File: contracts/NodeDelegator.sol)

## Summary

`NodeDelegator.getAssetUnstaking()` performs an unbounded nested iteration over all EigenLayer queued withdrawals via `getQueuedWithdrawals()`. This function is called once per NDC inside `LRTDepositPool.getAssetDistributionData()`, which feeds `getTotalAssetDeposits()`, which is invoked on every deposit, withdrawal initiation, and the public `updateRSETHPrice()`. As the number of NDCs and pending EigenLayer withdrawals grows through normal protocol operation, the gas cost of these entry points grows without a hard ceiling, constituting unbounded gas consumption and risking temporary freezing of funds.

## Finding Description

`NodeDelegator.getAssetUnstaking()` fetches all pending EigenLayer withdrawals and iterates over them with a nested loop:

```solidity
// contracts/NodeDelegator.sol L405-427
function getAssetUnstaking(address asset) external view returns (uint256 amount) {
    (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
        _getDelegationManager().getQueuedWithdrawals(address(this));

    for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
        for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
            ...
        }
    }
}
```

This is called inside `LRTDepositPool.getAssetDistributionData()` once per NDC in `nodeDelegatorQueue`:

```solidity
// contracts/LRTDepositPool.sol L446-456
for (uint256 i; i < ndcsCount;) {
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    ...
}
```

`getAssetDistributionData()` feeds `getTotalAssetDeposits()`, which is called by:
- `_checkIfDepositAmountExceedesCurrentLimit()` on every `depositETH()` / `depositAsset()` call
- `LRTOracle._getTotalEthInProtocol()` (once per supported asset) on every `updateRSETHPrice()` call (public, permissionless)
- `getAvailableAssetAmount()` inside `LRTWithdrawalManager.initiateWithdrawal()`

The effective gas complexity is:

```
O(supportedAssets × NDCs × queuedWithdrawals × strategiesPerWithdrawal)
```

No gas cap, pagination, or bounding exists on any of these loops. Each dimension grows through normal, unprivileged or routine operator activity.

## Impact Explanation

The primary concrete impact is **Medium — Unbounded gas consumption**: any user calling `depositETH()`, `depositAsset()`, `initiateWithdrawal()`, or the permissionless `updateRSETHPrice()` pays gas proportional to the product of all four dimensions. At sufficient scale (e.g., 10 NDCs × 20 queued withdrawals × 3 strategies × 5 assets = 3,000 inner iterations plus 50 cold external calls to EigenLayer's `getQueuedWithdrawals()`), transactions revert with out-of-gas, constituting **Medium — Temporary freezing of funds** for the duration that the queue remains large. The claim of *permanent* freezing is overstated: operators can call `completeUnstaking()` to drain the queue and restore functionality, so the freeze is temporary rather than permanent.

## Likelihood Explanation

The conditions are reachable through normal protocol operation. Operators routinely call `initiateUnstaking()` to move assets from EigenLayer back to the protocol; each call adds an entry to the queued withdrawal list that persists for EigenLayer's withdrawal delay (~7 days). With 10 NDCs (the default `maxNodeDelegatorLimit`) each accumulating withdrawals faster than they are completed, the queue grows. No unprivileged attacker action is required — the degradation occurs passively as the protocol scales. Any user can trigger the out-of-gas condition simply by submitting a deposit or withdrawal when the queue is large enough.

## Recommendation

1. **Replace per-call iteration with incremental accounting**: maintain a storage variable `assetUnstaking[asset]` in each NDC, incremented in `initiateUnstaking()` and decremented in `completeUnstaking()`, eliminating the need to iterate over `getQueuedWithdrawals()` on every read.
2. **Bound the NDC loop**: add a hard cap on `maxNodeDelegatorLimit` that accounts for the block gas limit given worst-case queue depth.
3. **Decouple oracle price updates**: store a pre-computed TVL updated by operators off-chain rather than recomputing it inline on every `updateRSETHPrice()` call.
4. **Add a cap on uncompleted withdrawals per NDC**: enforce `maxUncompletedWithdrawalCount` to prevent unbounded queue growth.

## Proof of Concept

1. Deploy protocol with 5 supported assets, 10 NDCs (`maxNodeDelegatorLimit = 10`).
2. Operator calls `initiateUnstaking()` on each NDC repeatedly until each NDC has 20 queued EigenLayer withdrawals with 3 strategies each.
3. Any user calls `depositETH(1 ether, 0, "")`.
4. Execution: `depositETH` → `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits` → `getAssetDistributionData` → 10 iterations each calling `getAssetUnstaking` → `getQueuedWithdrawals` (cold external call) + 60 inner iterations per NDC.
5. For `updateRSETHPrice()`: `_getTotalEthInProtocol` loops over 5 assets, each triggering the above 10-NDC × 60-iteration path = 50 cold external calls + 3,000 inner iterations.
6. A Foundry fork test against a mainnet fork with a mocked EigenLayer `DelegationManager` returning arrays of the above sizes will demonstrate gas consumption exceeding 10M gas for `updateRSETHPrice()` and approaching block gas limits as queue depth increases.