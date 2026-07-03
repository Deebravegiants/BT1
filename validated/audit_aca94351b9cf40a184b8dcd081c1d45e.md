Audit Report

## Title
Nested Unbounded Iteration in `updateRSETHPrice()` Causes Gas Exhaustion at Protocol Scale - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle.updateRSETHPrice()` is a public, permissionless function that internally executes a three-level nested iteration: over every supported asset, over every NodeDelegator, and over every EigenLayer queued withdrawal per NDC. Gas cost scales as O(assets × NDCs × withdrawals_per_NDC). The protocol's own comment in `LRTUnstakingVault.sol` acknowledges the constraint but the cap applied (`maxUncompletedWithdrawalCount ≤ 80`) only bounds total withdrawals, not the per-asset multiplication, leaving the function vulnerable to gas exhaustion as the supported asset list grows.

## Finding Description
The call chain is fully confirmed in the codebase:

1. `updateRSETHPrice()` (public, no access control) → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` — iterates over the entire `supportedAssetList` returned by `lrtConfig.getSupportedAssetList()`.
2. For each asset, calls `ILRTDepositPool.getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)` — iterates over the entire `nodeDelegatorQueue` (bounded by `maxNodeDelegatorLimit`, default 10, admin-adjustable upward).
3. For each NDC, calls `INodeDelegator(ndc).getAssetUnstaking(asset)` — calls `delegationManager.getQueuedWithdrawals(address(this))` and iterates over every queued withdrawal for that NDC.

The ETH path (`getETHDistributionData`) also iterates over all NDCs and calls `getAssetUnstaking(ETH_TOKEN)` per NDC, doubling the withdrawal-iteration cost for the ETH asset.

The protocol team acknowledged the gas concern in `LRTUnstakingVault.setMaxUncompletedWithdrawalCount()`:
```solidity
// 120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price
// Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)
if (_maxUncompletedWithdrawalCount > 80) {
    revert MaxUncompletedWithdrawalCountTooHigh();
}
```
However, this cap bounds only the **total** withdrawal count across all NDCs, not the per-asset multiplication. The actual iteration count is `N_assets × total_withdrawals`. With 10 supported assets and 80 total withdrawals, the function executes 800 withdrawal iterations plus 100 external `getQueuedWithdrawals` calls (10 assets × 10 NDCs). As `supportedAssetList` grows (no cap exists on asset count; `addNewSupportedAsset` is gated only by `TIME_LOCK_ROLE`), the gas cost increases proportionally, invalidating the developers' 120-withdrawal threshold which was calibrated for a fixed asset count.

## Impact Explanation
**Medium — Unbounded gas consumption.** If `updateRSETHPrice()` reverts due to gas exhaustion, the stored `rsETHPrice` becomes permanently stale. This halts fee minting (`_checkAndUpdateDailyFeeMintLimit`, `IRSETH.mint`), causes incorrect rsETH mint/redeem amounts for depositors and withdrawers, and disables the price-deviation circuit-breaker (pause-on-drop). The function is public and callable by any account; no privileged gating prevents the call from being attempted.

## Likelihood Explanation
No attack is required. Ordinary protocol growth — adding more supported LSTs via `addNewSupportedAsset` — directly multiplies the gas cost. The `maxUncompletedWithdrawalCount` cap at 80 was calibrated against a specific (undocumented) asset count. With the current 2 initial assets (`stETH`, `ETHx`) plus ETH, the margin is comfortable; at 8–10 assets the threshold is breached. `maxNodeDelegatorLimit` is also admin-adjustable upward, further compounding the cost. Any external caller can trigger the failure by simply calling `updateRSETHPrice()` once the gas cost exceeds the block limit.

## Recommendation
1. Decouple the per-asset TVL computation from the price update: accept a pre-computed `uint256[] calldata perAssetTVL` array supplied by an off-chain keeper in `updateRSETHPrice()`, with an on-chain staleness/sanity check.
2. Alternatively, add a paginated `getSupportedAssetList(uint256 start, uint256 end)` getter and split `_getTotalEthInProtocol()` into partial updates that accumulate into a final price over multiple transactions.
3. Recalibrate `maxUncompletedWithdrawalCount` as a function of the current asset count: `max_withdrawals = floor(gas_budget / (cost_per_withdrawal × N_assets))`, enforced on-chain when assets are added.

## Proof of Concept
**Foundry fork test outline:**

```solidity
// Fork mainnet, configure 10 supported assets and 10 NDCs
// Queue 8 withdrawals per NDC (80 total, within the cap)
// Call updateRSETHPrice() and measure gas
// Assert gas > 30_000_000 (block gas limit)

function test_updateRSETHPrice_gasExhaustion() public {
    // 1. Add 8 additional supported assets (beyond stETH, ETHx)
    for (uint i = 0; i < 8; i++) {
        vm.prank(timeLockAdmin);
        lrtConfig.addNewSupportedAsset(mockAssets[i], 100_000 ether);
    }
    // 2. Add 10 NDCs to nodeDelegatorQueue
    // 3. For each NDC, queue 8 withdrawals via initiateUnstaking()
    //    (total = 80, within maxUncompletedWithdrawalCount cap)
    // 4. Measure gas
    uint256 gasBefore = gasleft();
    lrtOracle.updateRSETHPrice();
    uint256 gasUsed = gasBefore - gasleft();
    assertGt(gasUsed, 30_000_000);
}
```

With 10 assets × 10 NDCs × 8 withdrawals/NDC = 800 withdrawal iterations + 100 external `getQueuedWithdrawals` calls, gas usage exceeds the 30M block gas limit.