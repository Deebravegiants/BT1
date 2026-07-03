Audit Report

## Title
Unbounded `supportedAssets` Loop in `_getTotalEthInProtocol()` Can Permanently Block Price Updates — (File: `contracts/LRTOracle.sol`)

## Summary

`LRTOracle.updateRSETHPrice()` is a public, unpermissioned function that calls `_getTotalEthInProtocol()`, which iterates over every entry in `supportedAssets` — an array with no enforced upper bound. For each asset, it calls into `LRTDepositPool.getAssetDistributionData()`, which loops over every NDC in `nodeDelegatorQueue`, and for each NDC calls `NodeDelegator.getAssetUnstaking()`, which fetches and iterates all queued EigenLayer withdrawals. As the protocol adds supported assets through normal governance, the combined gas cost grows multiplicatively. If it exceeds the block gas limit, `updateRSETHPrice()` becomes permanently uncallable, freezing the rsETH price and disabling fee accrual and downside-protection mechanisms.

## Finding Description

**Entry point** — `updateRSETHPrice()` at `contracts/LRTOracle.sol` L87–89 is `public whenNotPaused` with no role restriction. It unconditionally calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`.

**Outer loop (unbounded)** — `_getTotalEthInProtocol()` at `contracts/LRTOracle.sol` L331–349 fetches `lrtConfig.getSupportedAssetList()` and iterates over every entry. `LRTConfig.addNewSupportedAsset()` at `contracts/LRTConfig.sol` L99–118 is callable by `TIME_LOCK_ROLE` with no cap check on `supportedAssetList.length`.

**Inner loop (bounded but multiplied)** — For each asset, `LRTDepositPool.getAssetDistributionData()` at `contracts/LRTDepositPool.sol` L446–456 loops over every entry in `nodeDelegatorQueue` (bounded by `maxNodeDelegatorLimit`, default 10, admin-settable upward). For each NDC it calls `INodeDelegator.getAssetUnstaking(asset)`.

**Innermost loop** — `NodeDelegator.getAssetUnstaking()` at `contracts/NodeDelegator.sol` L405–427 calls EigenLayer's `getQueuedWithdrawals(address(this))` and iterates over all returned withdrawal structs and their strategy arrays.

Combined gas cost is `O(supportedAssets × nodeDelegatorQueue × queuedWithdrawals × strategies)`. The outer dimension has no cap. Existing guards (`maxNodeDelegatorLimit`, `maxUncompletedWithdrawalCount`) bound only the inner dimensions; they do not prevent the outer loop from growing without limit through normal governance.

## Impact Explanation

If `_getTotalEthInProtocol()` exhausts the block gas limit, every call to `updateRSETHPrice()` and `updateRSETHPriceAsManager()` reverts. Consequences:
- `rsETHPrice` is never updated; all deposits and withdrawals use a stale price, causing incorrect rsETH minting and incorrect asset-out calculations.
- Protocol fees are minted inside `_updateRsETHPrice()`; a permanently broken update loop means no fees are ever collected.
- The automatic pause triggered when `newRsETHPrice < highestRsethPrice` beyond the threshold can never fire, removing a critical safety mechanism.

**Impact: Medium — Unbounded gas consumption**, matching the allowed scope.

## Likelihood Explanation

No malicious actor is required. The `supportedAssets` array grows through normal governance as the protocol adds LSTs (e.g., rETH, cbETH, sfrxETH, osETH). With 20 assets, 10 NDCs, and 10 queued withdrawals per NDC, the innermost `getAssetUnstaking` is called 200 times per `updateRSETHPrice()` invocation; each call involves multiple EigenLayer storage reads and strategy share conversions. At realistic parameter values the cumulative gas cost approaches the 30M block gas limit. The condition worsens monotonically as the protocol expands and cannot be reversed without removing supported assets (which itself requires deposits to be near zero).

## Recommendation

1. **Cap `supportedAssets`**: Add a `maxSupportedAssets` limit in `LRTConfig._addNewSupportedAsset()`, analogous to `maxNodeDelegatorLimit` in `LRTDepositPool`.
2. **Cache or snapshot TVL**: Maintain a running TVL accumulator updated incrementally on deposit/withdrawal events rather than recomputing the full nested loop on every `updateRSETHPrice()` call.
3. **Batch TVL computation**: Allow `_getTotalEthInProtocol()` to be called per-asset in separate transactions and aggregate results, so no single transaction must traverse the entire array.

## Proof of Concept

**Call path (no privilege required):**
```
anyone → LRTOracle.updateRSETHPrice()          [public, whenNotPaused]
           └─ _updateRsETHPrice()
                └─ _getTotalEthInProtocol()
                     └─ for each asset in supportedAssets (NO CAP):
                          └─ LRTDepositPool.getTotalAssetDeposits(asset)
                               └─ getAssetDistributionData(asset)
                                    └─ for each NDC in nodeDelegatorQueue (≤ maxNodeDelegatorLimit):
                                         └─ INodeDelegator.getAssetUnstaking(asset)
                                              └─ DelegationManager.getQueuedWithdrawals()
                                                   └─ for each withdrawal × strategy
```

**Foundry fork test plan:**
1. Fork mainnet; deploy or reuse the live LRT contracts.
2. Via `TIME_LOCK_ROLE`, call `addNewSupportedAsset()` repeatedly until `supportedAssetList.length` reaches a target (e.g., 20).
3. Add NDCs up to `maxNodeDelegatorLimit`; queue withdrawals from each NDC via `initiateUnstaking()` up to `maxUncompletedWithdrawalCount`.
4. Call `updateRSETHPrice()` with `gasleft()` instrumentation and assert that gas consumed exceeds 30M, or that the call reverts with out-of-gas.
5. Confirm `rsETHPrice` is not updated after the revert.