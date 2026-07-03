Audit Report

## Title
Unbounded Nested-Loop Gas Exhaustion in Public `updateRSETHPrice()` and Deposit Path - (File: contracts/LRTOracle.sol, contracts/LRTDepositPool.sol, contracts/NodeDelegator.sol)

## Summary
`LRTOracle.updateRSETHPrice()` is publicly callable with only a `whenNotPaused` modifier. It executes a multiplicative nested-loop chain across supported assets, NodeDelegators, and EigenLayer queued withdrawals, each involving external calls. As the protocol scales normally, the aggregate gas cost can exceed the block gas limit, permanently freezing price updates and, through the same code path, all user deposits.

## Finding Description
`updateRSETHPrice()` at `LRTOracle.sol:87-89` is `public whenNotPaused` with no role restriction. It calls `_updateRsETHPrice()` → `_getTotalEthInProtocol()` (`LRTOracle.sol:331-349`), which iterates over every entry in `lrtConfig.getSupportedAssetList()`. For each asset it calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)` (`LRTDepositPool.sol:426-462`), which iterates over every NDC in `nodeDelegatorQueue` (`LRTDepositPool.sol:446-456`). For each NDC it calls `INodeDelegator.getAssetUnstaking(asset)` (`NodeDelegator.sol:405-427`), which issues one external `staticcall` to `DelegationManager.getQueuedWithdrawals(address(this))` and then iterates over all returned withdrawals and their strategies in memory.

The combined iteration count is:

```
supportedAssets.length
  × nodeDelegatorQueue.length   [external getAssetUnstaking calls]
  × queuedWithdrawals.length    [in-memory, per NDC]
  × withdrawal.strategies.length
```

None of these dimensions has a hard protocol-wide ceiling: `supportedAssetList` has no cap in `LRTConfig`; `maxNodeDelegatorLimit` defaults to 10 but is freely raised by admin via `updateMaxNodeDelegatorLimit`; `maxUncompletedWithdrawalCount` is per-NDC and admin-settable, so the aggregate across all NDCs is unbounded. All three dimensions grow monotonically during normal protocol operation (more LSTs added, more NDCs deployed for TVL growth, more withdrawals queued during redemption periods).

The identical loop chain is also triggered on every user deposit: `depositAsset`/`depositETH` → `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits` → `getAssetDistributionData` → `getAssetUnstaking` (`LRTDepositPool.sol:676-682`). If the gas cost exceeds the block gas limit, all deposits revert as well.

## Impact Explanation
When the product of the four loop dimensions grows large enough to exceed the 30M gas block limit, every call to `updateRSETHPrice()` reverts. The stored `rsETHPrice` becomes permanently stale. Simultaneously, every call to `depositAsset` and `depositETH` reverts because they traverse the same path. This constitutes **temporary freezing of funds** (depositors cannot enter the protocol) and **unbounded gas consumption** on a public entry point. Both are listed Medium impacts. The freeze persists until the protocol state is reduced (withdrawals completed, NDCs removed, or assets delisted), none of which can be forced by users.

## Likelihood Explanation
No attacker action is required. The condition is reached through ordinary protocol growth: adding LSTs, deploying additional NDCs to handle growing TVL, and processing large redemption batches that queue many EigenLayer withdrawals. With 5 supported assets, 10 NDCs, and 20 queued withdrawals per NDC (each with 3 strategies), `getAssetUnstaking` is called 50 times and the inner loop body executes 3,000 times per `updateRSETHPrice()` invocation, each involving external calls with dynamic return-data allocation. These numbers are realistic for a mid-scale deployment. Likelihood is **Medium**.

## Recommendation
1. **Aggregate `getAssetUnstaking` off-chain or cache it**: Replace the per-call `getQueuedWithdrawals` loop with an incrementally maintained counter updated in `initiateUnstaking` and `completeUnstaking`, similar to how `uncompletedWithdrawalCount` is already tracked in the unstaking vault.
2. **Cap `supportedAssetList`**: Enforce a maximum length in `LRTConfig.addNewSupportedAsset`, analogous to `maxNodeDelegatorLimit`.
3. **Access-restrict `updateRSETHPrice`**: Restrict to `OPERATOR_ROLE` or `MANAGER` so the gas cost is borne by a trusted party who can size the transaction appropriately; the existing `updateRSETHPriceAsManager` pattern already demonstrates this intent.
4. **Enforce a global `maxUncompletedWithdrawalCount` ceiling**: Apply a protocol-wide cap across all NDCs, not just per-NDC.

## Proof of Concept
Call sequence executable by any unprivileged EOA:

```
// Step 1: Protocol reaches scale (normal operation)
//   - 5 supported assets in LRTConfig
//   - 10 NDCs in nodeDelegatorQueue (maxNodeDelegatorLimit = 10)
//   - 20 queued EigenLayer withdrawals per NDC, each with 3 strategies
//     (maxUncompletedWithdrawalCount = 20 per NDC)

// Step 2: Unprivileged caller triggers gas exhaustion
attacker.call(lrtOracle.updateRSETHPrice())
  // → _updateRsETHPrice()
  //   → _getTotalEthInProtocol()
  //     for each of 5 assets:                          // loop 1
  //       → LRTDepositPool.getTotalAssetDeposits(asset)
  //         → getAssetDistributionData(asset)
  //           for each of 10 NDCs:                     // loop 2 → 50 external calls
  //             → NodeDelegator.getAssetUnstaking(asset)
  //               → DelegationManager.getQueuedWithdrawals(ndc)  // external staticcall
  //               for each of 20 withdrawals:          // loop 3
  //                 for each of 3 strategies:          // loop 4
  //                   accumulate amount
  // Total inner iterations: 5 × 10 × 20 × 3 = 3,000
  // Total external calls: 5 × 10 = 50 getQueuedWithdrawals + 50 getAssetBalance + 50 balanceOf
  // → REVERT: out of gas

// Step 3: All subsequent deposits also revert
user.call(lrtDepositPool.depositAsset(asset, amount, minRSETH, ""))
  // → _beforeDeposit → _checkIfDepositAmountExceedesCurrentLimit
  //   → getTotalAssetDeposits → getAssetDistributionData → getAssetUnstaking
  // → REVERT: out of gas
```

Foundry fork test plan: deploy against a mainnet fork, configure 5 supported assets and 10 NDCs, mock `DelegationManager.getQueuedWithdrawals` to return 20 withdrawals with 3 strategies each for each NDC, then call `updateRSETHPrice()` with `gas: 30_000_000` and assert the call reverts with out-of-gas. Separately assert that `depositAsset` also reverts under the same state.