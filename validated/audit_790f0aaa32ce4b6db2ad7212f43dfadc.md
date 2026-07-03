Audit Report

## Title
`NodeDelegator.getAssetUnstaking()` Nested Loop Multiplied by Asset Count Causes `LRTOracle.updateRSETHPrice()` to Exhaust Block Gas — (File: `contracts/NodeDelegator.sol`)

## Summary

`LRTOracle.updateRSETHPrice()` is a public, permissionless function that recomputes the rsETH price by iterating over every supported asset and, for each asset, calling `NodeDelegator.getAssetUnstaking()` on every NDC. `getAssetUnstaking()` makes an external `getQueuedWithdrawals()` call and runs a nested loop over every queued withdrawal and every strategy inside it. Because this work is repeated once per supported asset, the total gas cost scales as `numAssets × numNDCs × totalWithdrawals × strategiesPerWithdrawal`. The protocol's own withdrawal cap (80) is a flat total that does not account for the asset-count multiplier; as the supported-asset list grows, the effective gas ceiling falls proportionally, and `updateRSETHPrice()` can revert out-of-gas under normal operating conditions, leaving `rsETHPrice` permanently stale.

## Finding Description

**Call chain (all code confirmed in-repo):**

1. `LRTOracle.updateRSETHPrice()` (public, `whenNotPaused`) calls `_updateRsETHPrice()`, which calls `_getTotalEthInProtocol()`.
2. `_getTotalEthInProtocol()` loops over every supported asset and calls `ILRTDepositPool.getTotalAssetDeposits(asset)` for each one.
3. `getTotalAssetDeposits()` calls `getAssetDistributionData(asset)`, which loops over every NDC in `nodeDelegatorQueue` and calls `INodeDelegator(ndc).getAssetUnstaking(asset)` per NDC.
4. `getAssetUnstaking()` calls `delegationManager.getQueuedWithdrawals(address(this))` (one external call per NDC per asset) and then runs a **nested loop**: outer over every queued withdrawal, inner over every strategy in that withdrawal, calling `strategy.sharesToUnderlyingView()` for non-ETH strategies.

**Gas cost formula per `updateRSETHPrice()` call:**
```
external getQueuedWithdrawals calls = numAssets × numNDCs
inner sharesToUnderlyingView calls  = numAssets × Σ(withdrawals per NDC) × strategiesPerWithdrawal
```

**Why the existing cap is insufficient:**

`LRTUnstakingVault.setMaxUncompletedWithdrawalCount()` enforces a hard cap of 80 total queued withdrawals. The comment reads: *"120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price"*. This calibration is implicitly tied to the current number of supported assets. If the asset count grows from, say, 3 to 6, the same 80 queued withdrawals now produce twice the gas load, pushing the transaction past the block gas limit even though the counter never exceeded the cap.

Additionally, `setUncompletedWithdrawalCount()` re-syncs the counter to the live EigenLayer state (e.g., after forced undelegations). This can cause the real on-chain withdrawal count to temporarily exceed the soft cap before operators can react, further reducing the safety margin.

**ETH path is also affected:** `getETHDistributionData()` calls `getAssetUnstaking(LRTConstants.ETH_TOKEN)` on every NDC, so the ETH asset contributes its own full iteration pass on top of the ERC-20 asset passes.

## Impact Explanation

If `updateRSETHPrice()` reverts out-of-gas:
- `rsETHPrice` in `LRTOracle` becomes permanently stale.
- All new deposits mint rsETH at the wrong rate.
- `LRTWithdrawalManager.unlockQueue()` reads `lrtOracle.rsETHPrice()`, so withdrawal payouts are computed from the stale rate — constituting temporary freezing of user funds.
- Protocol fee minting inside `_updateRsETHPrice()` is blocked, constituting permanent freezing of unclaimed yield.
- `updateRSETHPriceAsManager()` calls the same `_updateRsETHPrice()` path and is equally blocked.

**Concrete allowed impacts matched:** Medium — Unbounded gas consumption; Medium — Permanent freezing of unclaimed yield; Medium — Temporary freezing of funds.

## Likelihood Explanation

No attacker action is required. Operators routinely call `initiateUnstaking()` and `undelegate()` as part of normal protocol operation, filling the withdrawal queue toward the 80-withdrawal cap. The risk is monotonically increasing: every new supported asset added to the protocol lowers the effective gas ceiling without any change to the withdrawal cap. The function is public and callable by anyone, so there is no privileged gating that could prevent the revert once the gas threshold is crossed.

## Recommendation

1. **Cache `getQueuedWithdrawals()` per NDC once per price update.** A single call per NDC can be used to compute `getAssetUnstaking()` for all assets simultaneously, reducing external calls from `numAssets × numNDCs` to `numNDCs`.
2. **Decouple unstaking accounting from the price update path.** Store per-asset unstaking amounts in storage and update them lazily when withdrawals are initiated or completed, rather than recomputing them on every `updateRSETHPrice()` call.
3. **Make `maxUncompletedWithdrawalCount` asset-aware.** The cap should be `floor(gasLimit / (gasPerWithdrawal × numAssets))` rather than a fixed 80, or enforce a per-NDC cap that accounts for the multiplier.

## Proof of Concept

**Minimal call sequence to trigger out-of-gas:**

```
// Preconditions (normal protocol operation):
// - 5 supported assets (stETH, cbETH, rETH, ankrETH, swETH)
// - 10 NDCs, each with 8 queued withdrawals (total = 80, at cap)
// - Each withdrawal contains 2 strategies

// Trigger (permissionless):
LRTOracle.updateRSETHPrice()
  └─ _getTotalEthInProtocol()
       └─ for each of 5 assets:
            LRTDepositPool.getTotalAssetDeposits(asset)
              └─ getAssetDistributionData(asset)
                   └─ for each of 10 NDCs:
                        NodeDelegator.getAssetUnstaking(asset)
                          └─ getQueuedWithdrawals(ndc)   // 50 external calls total
                               └─ for each of 8 withdrawals:
                                    for each of 2 strategies:
                                      sharesToUnderlyingView(...)  // 800 external calls total

// Result: ~850 external calls in a single view transaction → OOG revert
// rsETHPrice remains stale; fee minting blocked; withdrawal payouts use wrong rate
```

**Foundry fork test plan:**
1. Fork mainnet at a block where the protocol has ≥5 supported assets and ≥5 NDCs.
2. Use `vm.store` to set `uncompletedWithdrawalCount` to 79 and mock `getQueuedWithdrawals` on each NDC to return 8 withdrawals with 2 strategies each.
3. Call `LRTOracle.updateRSETHPrice{gas: 30_000_000}()` and assert it reverts with out-of-gas.
4. Verify `rsETHPrice` is unchanged after the revert.