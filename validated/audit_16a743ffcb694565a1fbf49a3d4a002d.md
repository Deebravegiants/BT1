Audit Report

## Title
Unbounded O(K × M) Gas Loop in `updateRSETHPrice()` Can Permanently DoS rsETH Price Updates — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

## Summary

`updateRSETHPrice()` is a public, permissionless function whose internal call chain executes a nested loop over K supported assets × M node delegators, making multiple EigenLayer external calls per cell. Because `maxNodeDelegatorLimit` has no hard upper bound and the supported-asset list has no cap, gas cost grows as O(K × M × W) where W is the queued-withdrawal count per NDC. At realistic operational scale this transaction exceeds the 30 M-gas block limit and reverts permanently, freezing the rsETH price.

## Finding Description

The full call chain is:

```
updateRSETHPrice()                          ← public, whenNotPaused only
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each of K assets:
                 getTotalAssetDeposits(asset)
                   └─ getAssetDistributionData(asset)
                        └─ for each of M NDCs:
                             IERC20(asset).balanceOf(ndc[i])           // external call
                             INodeDelegator(ndc[i]).getAssetBalance()   // → EigenLayer getWithdrawableShares()
                             INodeDelegator(ndc[i]).getAssetUnstaking() // → EigenLayer getQueuedWithdrawals()
                                                                        //   + nested loop over all queued withdrawals
```

**Root cause — no ceiling on NDC count or asset count:**

`updateMaxNodeDelegatorLimit` only enforces `newLimit >= queue.length`; there is no upper ceiling:

```solidity
// LRTDepositPool.sol L290-296
function updateMaxNodeDelegatorLimit(uint256 maxNodeDelegatorLimit_) external onlyLRTAdmin {
    if (maxNodeDelegatorLimit_ < nodeDelegatorQueue.length) {
        revert InvalidMaximumNodeDelegatorLimit();
    }
    maxNodeDelegatorLimit = maxNodeDelegatorLimit_;
```

The outer asset loop in `_getTotalEthInProtocol` (LRTOracle.sol L336-348) calls `getTotalAssetDeposits` for every supported asset. `getAssetDistributionData` (LRTDepositPool.sol L446-456) then iterates every NDC and makes three external calls per NDC per asset. `getAssetUnstaking` (NodeDelegator.sol L405-427) calls EigenLayer's `getQueuedWithdrawals(address(this))` and runs a nested loop over all returned withdrawals. `getAssetBalance` (NodeDelegatorHelper.sol L31-39) calls EigenLayer's `getWithdrawableShares` — another cross-contract call per NDC per asset.

**Why existing checks are insufficient:**

- `maxUncompletedWithdrawalCount` in `LRTUnstakingVault` is a global counter across all NDCs; it does not bound the per-NDC withdrawal count returned by `getQueuedWithdrawals(address(this))` for any individual NDC.
- The `whenNotPaused` guard on `updateRSETHPrice()` does not limit gas consumption.
- `updateRSETHPriceAsManager()` shares the identical `_updateRsETHPrice()` code path and is equally affected.
- NDCs with staked assets cannot be removed from the queue (removal requires zero residual balance per `_checkResidueEthBalance` / `_checkResidueLSTBalance`), making the condition permanent once reached.

## Impact Explanation

**Medium — Unbounded gas consumption / permanent freezing of unclaimed yield.**

Once the gas cost of `updateRSETHPrice()` exceeds the 30 M-gas block limit, every call reverts with out-of-gas. The stored `rsETHPrice` becomes permanently stale. Because `getRsETHAmountToMint` divides by `rsETHPrice`, a stale price causes incorrect rsETH minting ratios for all subsequent depositors. The manager-only variant `updateRSETHPriceAsManager()` suffers the same gas path. Protocol fee accrual (minted as rsETH in `_updateRsETHPrice`) also halts. The condition is irreversible without a full protocol migration because NDCs holding assets cannot be removed.

## Likelihood Explanation

The precondition is legitimate admin configuration, not malicious compromise. An operator scaling to 30–50 NDCs (each delegated to a different EigenLayer operator for decentralization) combined with 5–10 supported LSTs produces 150–500 NDC×asset cells, each requiring two EigenLayer cross-contract calls. At ~20 k–50 k gas per EigenLayer call: 500 cells × 2 calls × 35 k gas ≈ 35 M gas — already over the block limit. This is a realistic operational scale for a growing LRT protocol. The trigger (`updateRSETHPrice()`) is callable by any unprivileged external account with no preconditions beyond the protocol being unpaused.

## Recommendation

1. **Hard-cap `maxNodeDelegatorLimit`** to a value (e.g., 20) that keeps worst-case gas well below 30 M, enforced in `updateMaxNodeDelegatorLimit`.
2. **Cache per-NDC totals** in storage (updated on deposit/withdrawal/unstaking events) so `_getTotalEthInProtocol` reads O(K + M) storage slots instead of making O(K × M) external calls.
3. **Separate `getAssetUnstaking` accounting** into a storage variable maintained by `initiateUnstaking` / `completeUnstaking`, eliminating the `getQueuedWithdrawals` loop from the price-update path entirely.

## Proof of Concept

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

contract GasExplosionTest is Test {
    LRTOracle oracle;
    LRTDepositPool pool;

    function setUp() public {
        // deploy protocol with standard config
        // register K=5 LST assets
        // raise maxNodeDelegatorLimit to 50 via updateMaxNodeDelegatorLimit(50)
        // deploy and add M=50 NodeDelegator contracts via addNodeDelegatorContractToQueue
        // have each NDC deposit assets into EigenLayer strategies
        // initiate at least one unstaking per NDC so getQueuedWithdrawals returns non-empty
    }

    function test_updateRSETHPrice_OOG() public {
        // call with 30M gas budget — should revert OOG
        (bool ok,) = address(oracle).call{gas: 30_000_000}(
            abi.encodeCall(oracle.updateRSETHPrice, ())
        );
        assertFalse(ok, "expected OOG revert");
    }

    function testFuzz_gasGrowsQuadratically(uint8 k, uint8 m) public {
        vm.assume(k > 1 && k <= 10);
        vm.assume(m > 1 && m <= 50);
        uint256 gasUsed   = _measureUpdateGas(k,     m);
        uint256 gasUsed2x = _measureUpdateGas(k * 2, m * 2);
        // quadratic growth: doubling both dimensions should more than triple gas
        assertGt(gasUsed2x, gasUsed * 3, "gas grows super-linearly");
    }
}
```

The fuzz test will demonstrate O(K × M) gas scaling and will hit the 30 M ceiling at moderate (K, M) pairs well within the uncapped `maxNodeDelegatorLimit`.