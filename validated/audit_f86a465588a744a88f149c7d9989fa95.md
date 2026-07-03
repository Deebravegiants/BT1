Audit Report

## Title
Nested Loops in `getAssetUnstaking` Called Per-Asset Per-NDC in `updateRSETHPrice` Cause Unbounded Gas Consumption - (File: contracts/NodeDelegator.sol)

## Summary
`LRTOracle.updateRSETHPrice()` is a public function that triggers a call chain ending in `NodeDelegator.getAssetUnstaking()`, which fetches all EigenLayer queued withdrawals and iterates over them with two nested loops. Because `getAssetUnstaking` is called once per supported asset per NDC, the total gas cost scales as O(N_assets × M_NDCs × P_withdrawals × Q_strategies), with multiple external calls per iteration. The protocol's `maxUncompletedWithdrawalCount` cap does not account for the per-asset multiplication factor, making the mitigation insufficient to prevent gas exhaustion.

## Finding Description
The confirmed call chain is:

1. `LRTOracle.updateRSETHPrice()` (public, `whenNotPaused`) → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` — loops over every supported asset and calls `ILRTDepositPool.getTotalAssetDeposits(asset)`.
2. `getTotalAssetDeposits` → `getAssetDistributionData(asset)` — loops over every NDC in `nodeDelegatorQueue` and calls `INodeDelegator(ndc).getAssetUnstaking(asset)` per NDC per asset.
3. `getETHDistributionData()` (called for the ETH asset path) also loops over all NDCs and calls `getAssetUnstaking(ETH_TOKEN)` per NDC.
4. `getAssetUnstaking()` calls `_getDelegationManager().getQueuedWithdrawals(address(this))` — fetching the **full** withdrawal array from EigenLayer — then runs two nested loops: outer over `queuedWithdrawals.length`, inner over `withdrawal.strategies.length`, making external calls to `strategy.sharesToUnderlyingView()` inside.

The critical flaw is that `getAssetUnstaking` is invoked **once per asset per NDC**, yet each invocation independently fetches and iterates over **all** queued withdrawals for that NDC. With N_assets supported assets and M_NDCs node delegators, `getQueuedWithdrawals` is called N_assets × M_NDCs times, and the strategy loop executes N_assets × Σ(P_withdrawals_per_NDC × Q_strategies) times.

The `maxUncompletedWithdrawalCount` cap (≤ 80 total) is enforced only at withdrawal initiation in `LRTUnstakingVault`. It does not bound the per-call gas because:
- `getAssetUnstaking` reads directly from EigenLayer without any protocol-level cap check.
- The protocol's own comment ("120 is the max number of uncompleted withdrawals that allows us to still perform update rsETH price") appears to calculate gas cost without accounting for the N_assets multiplier.
- Forced operator undelegations (acknowledged: "ndc count × asset count = 15") can temporarily push the total above 80 before the manager can call `setUncompletedWithdrawalCount`.

## Impact Explanation
If `updateRSETHPrice()` exceeds the block gas limit or becomes prohibitively expensive to call:
- `rsETHPrice` in `LRTOracle` becomes permanently stale.
- Protocol fee minting is blocked.
- Deposits and withdrawals continue using the stale price, causing incorrect rsETH minting and incorrect withdrawal asset amounts.
- The price-deviation circuit breaker (pause-on-drop) cannot trigger, removing a key safety mechanism.

This matches **Medium — Unbounded gas consumption**.

## Likelihood Explanation
`updateRSETHPrice()` is public and must be called regularly. With 4 assets (stETH, ETHx, sfrxETH, ETH), 5 NDCs, 80 total queued withdrawals (16 per NDC), and 3 strategies per withdrawal: 4 × 5 × 16 × 3 = **960 external `sharesToUnderlyingView` calls** plus 20 `getQueuedWithdrawals` calls (each allocating and returning a full withdrawal array). Memory expansion costs grow quadratically with array size. This is reachable under normal protocol operation as unstaking activity accumulates, without any attacker action — the protocol's own scaling causes the issue.

## Recommendation
1. **Cache `getQueuedWithdrawals` once per NDC** and reuse the result across all asset queries within a single `updateRSETHPrice` call, eliminating the N_assets multiplication factor.
2. **Maintain a running TVL accumulator** updated on each deposit/withdrawal event ("push" pattern), so `updateRSETHPrice()` reads a single cached value per asset rather than iterating on-chain.
3. **Enforce a per-NDC withdrawal count cap** at the `NodeDelegator` level, not just a global total in `LRTUnstakingVault`, to bound the inner loop independently of the number of NDCs.
4. Revise the comment in `LRTUnstakingVault.setMaxUncompletedWithdrawalCount` to account for the N_assets multiplier when calculating the safe maximum.

## Proof of Concept
**Foundry fork test plan:**

```solidity
// Fork mainnet, configure: 4 assets, 5 NDCs, queue 16 withdrawals per NDC (80 total), 3 strategies each
// Call updateRSETHPrice() and measure gas:
function test_updateRSETHPrice_gasExhaustion() public {
    // Setup: 4 assets, 5 NDCs, 16 queued withdrawals per NDC, 3 strategies per withdrawal
    // Expected: 4 * 5 * 16 * 3 = 960 sharesToUnderlyingView calls
    uint256 gasBefore = gasleft();
    lrtOracle.updateRSETHPrice();
    uint256 gasUsed = gasBefore - gasleft();
    // Assert gasUsed approaches or exceeds block gas limit (~30M on L1)
    assertGt(gasUsed, 20_000_000);
}
```

**Minimal call sequence demonstrating the multiplication:**
```
updateRSETHPrice()                          // public, no auth
└── _getTotalEthInProtocol()
    └── [loop: 4 assets]
        └── getAssetDistributionData(asset) / getETHDistributionData()
            └── [loop: 5 NDCs]
                └── getAssetUnstaking(asset)          // 20 total calls
                    └── getQueuedWithdrawals(ndc)     // 20 EigenLayer calls
                        └── [loop: 16 withdrawals]
                            └── [loop: 3 strategies]
                                └── sharesToUnderlyingView()  // 960 external calls
```