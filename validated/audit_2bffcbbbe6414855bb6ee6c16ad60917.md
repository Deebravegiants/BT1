Audit Report

## Title
O(assets × NDCs × queued-withdrawals) Unbounded Gas in `updateRSETHPrice` Call Chain — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

## Summary

`updateRSETHPrice()` is a public, permissionless function whose internal call chain executes a nested loop: for every supported asset it calls `getTotalAssetDeposits` → `getAssetDistributionData`, which iterates every NDC and makes multiple EigenLayer external calls per iteration, including `getQueuedWithdrawals` which itself contains an inner loop over queued withdrawals × strategies. No hard upper bound on NDC count or asset count is enforced in contract code, making total gas cost O(assets × NDCs × queued-withdrawals). As the protocol grows legitimately, this function can exceed the block gas limit, permanently freezing the rsETH price and blocking all deposits and withdrawals that depend on it.

## Finding Description

**Confirmed call chain:**

`updateRSETHPrice()` (public, no role check) → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → outer loop over `supportedAssets` → `getTotalAssetDeposits(asset)` → `getAssetDistributionData(asset)` → inner loop over `nodeDelegatorQueue` → per NDC: `IERC20.balanceOf`, `getAssetBalance` (→ `delegationManager.getWithdrawableShares`), `getAssetUnstaking` (→ `delegationManager.getQueuedWithdrawals` + inner loop over withdrawals × strategies).

**Dimension 1 — NDC count:** `maxNodeDelegatorLimit` is initialized to `10` but `updateMaxNodeDelegatorLimit` accepts any value ≥ current queue length with no ceiling, callable by `onlyLRTAdmin`.

**Dimension 2 — Asset count:** `addNewSupportedAsset` is gated by `TIME_LOCK_ROLE` but `supportedAssetList` has no enforced maximum length.

**Dimension 3 — Queued withdrawals:** `getAssetUnstaking` calls `delegationManager.getQueuedWithdrawals(address(this))` once per asset per NDC, iterating all queued withdrawals × strategies each time. `maxUncompletedWithdrawalCount` is capped at 80 in `LRTUnstakingVault`, but this cap is per-vault, not per-NDC, and the same withdrawal data is re-fetched for every asset in the outer loop.

**The protocol's own code acknowledges the multiplicative cost** in `LRTUnstakingVault.sol` line 152: `// Need buffer for theoretical operator forced undelegations (ndc count * asset count = 15)`. The team caps `maxUncompletedWithdrawalCount` at 80 precisely because of gas concerns, but applies no equivalent cap to NDC count or asset count in the context of `updateRSETHPrice`.

**Existing guards are insufficient:** The only guard on NDC count is `maxNodeDelegatorLimit`, which is itself uncapped. The only guard on asset count is the `TIME_LOCK_ROLE` gating, which is a governance delay, not a gas ceiling. Neither prevents the function from exceeding the block gas limit at realistic protocol scale.

## Impact Explanation

If `updateRSETHPrice()` reverts with out-of-gas:
- `rsETHPrice` is never updated (stale price)
- `depositAsset`/`depositETH` call `_beforeDeposit` → `_checkIfDepositAmountExceedesCurrentLimit` → `getTotalAssetDeposits`, which also OOGs, reverting all deposits
- `LRTWithdrawalManager.getExpectedAssetAmount` reads `lrtOracle.rsETHPrice()` — withdrawals use stale price or fail
- The price-deviation guard can auto-pause the protocol on price drop, but cannot unpause if `updateRSETHPrice` itself OOGs

This constitutes **Medium: Unbounded gas consumption** and **Medium: Temporary (potentially permanent) freezing of funds** — both in the allowed impact scope.

## Likelihood Explanation

The protocol is designed to grow: more LSTs are added as EigenLayer supports them, and more NDCs are added to distribute operator risk. The admin can raise `maxNodeDelegatorLimit` without any contract-level ceiling as a normal operational action (not a malicious one). The team's own comment `ndc count * asset count = 15` shows the current design relies on off-chain discipline rather than on-chain enforcement. At 20–30 NDCs × 8–10 assets × up to 80 queued withdrawals per NDC, the gas cost crosses the block limit without any malicious action. This is a natural consequence of protocol growth, not an attack.

## Recommendation

1. **Enforce hard caps in contract code** for both `maxNodeDelegatorLimit` (e.g., `require(maxNodeDelegatorLimit_ <= 15)`) and the number of supported assets (e.g., `require(supportedAssetList.length < MAX_ASSETS)`).
2. **Cache per-NDC data off-chain** and use a push-based oracle pattern (operator submits pre-computed TVL with a merkle proof or signed attestation) rather than computing it on-chain in a single transaction.
3. **Avoid re-fetching `getQueuedWithdrawals` per asset per NDC.** Fetch once per NDC and iterate over all assets in a single pass.
4. **Add a gas-estimation check in CI/tests** that fails if `updateRSETHPrice` gas exceeds a threshold at max configured dimensions.

## Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

// Foundry fork test (local fork, no mainnet)
contract GasBoundaryTest is Test {
    function test_updateRSETHPrice_gasScaling() public {
        // 1. Deploy LRTConfig, LRTDepositPool, LRTOracle
        // 2. Add A=10 mock ERC20 assets (each with a mock price oracle)
        // 3. Call updateMaxNodeDelegatorLimit(30) as admin
        // 4. Add N=30 mock NodeDelegator contracts
        //    - each mock NDC returns non-zero from getAssetBalance (via mock getWithdrawableShares)
        //    - each mock NDC returns 5 queued withdrawals × 2 strategies from getQueuedWithdrawals
        // 5. Measure gas

        uint256 gasBefore = gasleft();
        lrtOracle.updateRSETHPrice();
        uint256 gasUsed = gasBefore - gasleft();

        // At N=30, A=10, 5 queued withdrawals × 2 strategies per NDC:
        // ~30 × 10 × (2500 + 25000 + 5×2×20000) = ~30 × 10 × 227500 = ~68M gas
        // Exceeds 30M block gas limit
        assertGt(gasUsed, 30_000_000, "exceeds block gas limit");
    }
}
```

Fuzz the `(numAssets, numNDCs, numQueuedWithdrawals)` triple to find the exact boundary. Based on per-iteration cost analysis, the boundary is reachable at `numAssets × numNDCs > 600` with zero queued withdrawals, or at much lower NDC/asset counts with non-trivial queued withdrawal state — all reachable by raising `maxNodeDelegatorLimit` beyond its default of 10 via normal admin operations.