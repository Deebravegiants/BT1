Audit Report

## Title
Unbounded Gas Consumption via Nested Loops in `getAssetUnstaking` on Public Deposit and Price-Update Paths - (File: contracts/NodeDelegator.sol, contracts/LRTOracle.sol, contracts/LRTDepositPool.sol)

## Summary
`NodeDelegator.getAssetUnstaking()` performs a nested loop over all EigenLayer queued withdrawals and their strategies on every call. This function is invoked once per NDC in both `getAssetDistributionData()` and `getETHDistributionData()`, which are themselves called on every user deposit (via `_checkIfDepositAmountExceedesCurrentLimit`) and on every invocation of the publicly accessible, unauthenticated `updateRSETHPrice()`. As the number of supported assets, NDCs, and queued EigenLayer withdrawals grows within normal operational bounds, the aggregate gas cost grows as O(assets × NDCs × queuedWithdrawals × strategiesPerWithdrawal), with no coordinated on-chain cap preventing the block gas limit from being exceeded.

## Finding Description

`LRTOracle.updateRSETHPrice()` is public with no access-control restriction beyond `whenNotPaused`:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

It calls `_getTotalEthInProtocol()`, which iterates over every supported asset and calls `ILRTDepositPool.getTotalAssetDeposits(asset)` for each:

```solidity
// contracts/LRTOracle.sol L336-341
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    ...
}
```

`getTotalAssetDeposits` delegates to `getAssetDistributionData` / `getETHDistributionData`, both of which loop over every NDC in `nodeDelegatorQueue` and call `getAssetUnstaking` for each:

```solidity
// contracts/LRTDepositPool.sol L446-456
for (uint256 i; i < ndcsCount;) {
    assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);
    ...
}
// contracts/LRTDepositPool.sol L484-492
for (uint256 i; i < ndcsCount;) {
    ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(LRTConstants.ETH_TOKEN);
    ...
}
```

`getAssetUnstaking` fetches the full list of queued withdrawals from EigenLayer's `DelegationManager` and iterates over them with a nested loop, making external calls per strategy:

```solidity
// contracts/NodeDelegator.sol L405-427
function getAssetUnstaking(address asset) external view returns (uint256 amount) {
    (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
        _getDelegationManager().getQueuedWithdrawals(address(this));
    for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
        for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
            ...
            strategy.sharesToUnderlyingView(sharesToUnstake); // external call
        }
    }
}
```

The same chain is triggered on every user deposit via `_checkIfDepositAmountExceedesCurrentLimit`:

```solidity
// contracts/LRTDepositPool.sol L676-682
function _checkIfDepositAmountExceedesCurrentLimit(address asset, uint256 amount) internal view returns (bool) {
    uint256 totalAssetDeposits = getTotalAssetDeposits(asset);
    ...
}
```

`maxNodeDelegatorLimit` caps NDC count and `maxUncompletedWithdrawalCount` caps queued withdrawals per NDC, but these two limits are independent of each other and of the number of supported assets. There is no enforced invariant that their product stays within block gas limits. Furthermore, `maxNodeDelegatorLimit` is admin-adjustable upward at any time.

## Impact Explanation

When the product of (supported assets) × (NDC count) × (queued withdrawals per NDC) × (strategies per withdrawal) grows large enough, both `depositETH`/`depositAsset` and `updateRSETHPrice` will revert with out-of-gas. This causes temporary freezing of deposits (users cannot deposit) and prevents price updates needed for correct withdrawal processing. This matches the allowed impact: **Medium — Unbounded gas consumption / Temporary freezing of funds**.

## Likelihood Explanation

`updateRSETHPrice()` is callable by any unprivileged external account with no cost beyond gas. With 5 supported assets, 10 NDCs (within `maxNodeDelegatorLimit`), and 50 queued withdrawals each (within `maxUncompletedWithdrawalCount`), the inner loop executes ≥2,500 times per call, each involving external calls to EigenLayer strategy contracts. This is realistic at production scale and requires no attacker action — normal protocol operation (staking, queuing withdrawals) naturally accumulates the state that causes the revert. No exploit is needed; the condition arises organically.

## Recommendation

1. **Cache `getAssetUnstaking` results per NDC**: Compute the total unstaking amount once per NDC across all assets in a single pass rather than calling it once per (NDC, asset) pair, eliminating the outer asset-loop multiplier.
2. **Decouple price update from full TVL scan**: Maintain a running TVL updated incrementally at queue/complete time rather than recomputed from scratch on every call.
3. **Coordinate caps**: Enforce an explicit on-chain invariant that `supportedAssets × maxNodeDelegatorLimit × maxUncompletedWithdrawalCount × maxStrategiesPerWithdrawal` stays within a safe gas budget at the admin configuration layer.
4. **Paginate or snapshot EigenLayer queued withdrawals**: Maintain internal accounting of unstaking amounts updated at queue/complete time instead of calling `getQueuedWithdrawals` (which returns the full unbounded list) on every view.

## Proof of Concept

**Call trace for `updateRSETHPrice()` (public, no auth):**

```
LRTOracle.updateRSETHPrice()                          // L87, public whenNotPaused
  └─ _getTotalEthInProtocol()                         // L331
       └─ for asset in supportedAssets (e.g. 5):      // L336
            getTotalAssetDeposits(asset)               // L341
              └─ getAssetDistributionData(asset)
                   └─ for i in [0..ndcsCount) (e.g. 10): // L447
                        getAssetUnstaking(asset)          // L451
                          └─ getQueuedWithdrawals(ndc)    // L406-407
                          └─ for w in withdrawals (e.g. 50): // L409
                               for s in strategies (e.g. 3): // L412
                                 strategy.sharesToUnderlyingView() // L424 external call
```

Total external calls: 5 × 10 × 50 × 3 = **7,500** per `updateRSETHPrice` invocation — sufficient to exceed the 30M gas block limit at realistic production scale.

**Call trace for `depositETH()`:**

```
LRTDepositPool.depositETH()
  └─ _beforeDeposit()
       └─ _checkIfDepositAmountExceedesCurrentLimit(ETH_TOKEN, msg.value) // L676
            └─ getTotalAssetDeposits(ETH_TOKEN)                           // L677
                 └─ getETHDistributionData()                              // L484-492
                      └─ [same nested loop as above, for ETH asset only]
```

A Foundry fork test can reproduce this by: (1) deploying with 5 supported assets and 10 NDCs, (2) queuing 50 EigenLayer withdrawals per NDC via the operator, (3) calling `updateRSETHPrice()` from an unprivileged EOA and measuring gas — expected result: out-of-gas revert.