### Title
Nested Loop Over `supportedAssets × nodeDelegatorQueue × getQueuedWithdrawals` in `updateRSETHPrice()` Causes Unbounded Gas Consumption — (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

`updateRSETHPrice()` is a public, permissionless function. Its internal call chain traverses three nested loops — supported assets, NDCs, and EigenLayer queued withdrawals — with no gas budget check. As the protocol scales (more assets, more NDCs, more queued withdrawals), the function can exceed the block gas limit, permanently preventing rsETH price updates.

---

### Finding Description

The call chain is:

```
updateRSETHPrice()                          [public, no role guard]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ for each asset in supportedAssets (N)          ← loop 1
                 └─ getTotalAssetDeposits(asset)
                      └─ getAssetDistributionData(asset)
                           └─ for each NDC in nodeDelegatorQueue (M)  ← loop 2
                                └─ getAssetUnstaking(asset)
                                     └─ delegationManager.getQueuedWithdrawals(NDC)
                                          └─ for each queued withdrawal (K)  ← loop 3
```

**Loop 1** — `_getTotalEthInProtocol()` iterates over every supported asset: [1](#0-0) 

**Loop 2** — `getAssetDistributionData()` iterates over every NDC in `nodeDelegatorQueue` and calls `getAssetUnstaking()` for each: [2](#0-1) 

**Loop 3** — `getAssetUnstaking()` calls `delegationManager.getQueuedWithdrawals(address(this))` (an external call returning all queued withdrawals for that NDC) and iterates over every withdrawal: [3](#0-2) 

The result is **N × M external calls** to `getQueuedWithdrawals`, each followed by **K iterations**. Total work is O(N × M × K).

The same `getQueuedWithdrawals(NDC_j)` is called **N times** (once per asset) for each NDC, even though the result is asset-independent — a redundancy that multiplies the gas cost by N.

---

### Impact Explanation

When N × M × K grows large enough to exceed the block gas limit (~30M gas on mainnet), `updateRSETHPrice()` reverts with out-of-gas on every call. Because `updateRSETHPrice()` is the only public path to refresh `rsETHPrice`, the stored price becomes permanently stale. Downstream effects include:

- `getRsETHAmountToMint()` uses the stale `rsETHPrice`, mispricing all deposits.
- `updateRSETHPriceAsManager()` (manager-only) calls the same `_updateRsETHPrice()` and OOGs identically.
- Protocol fee minting is blocked.

**Impact: Medium — Unbounded gas consumption / permanent freezing of price updates.**

---

### Likelihood Explanation

The setup requires only normal protocol operation:

1. Admin adds supported assets via `addNewSupportedAsset()` — legitimate scaling.
2. Admin adds NDCs via `addNodeDelegatorContractToQueue()` — `maxNodeDelegatorLimit` defaults to 10 but is admin-adjustable upward. [4](#0-3) 
3. Operator calls `initiateUnstaking()` repeatedly — each call creates one queued withdrawal, bounded by `maxUncompletedWithdrawalCount` in `LRTUnstakingVault`, but this is also admin-adjustable. [5](#0-4) 

None of these steps require malicious intent. With N=5 assets, M=20 NDCs, and K=50 queued withdrawals per NDC, the function makes 5×20=100 external calls to `getQueuedWithdrawals` and performs 5×1000=5000 inner iterations — well within OOG territory given EigenLayer's storage reads per call.

An unprivileged caller then simply calls `updateRSETHPrice()` and the function OOGs.

---

### Recommendation

1. **Cache `getQueuedWithdrawals` per NDC**: Call it once per NDC (not once per asset per NDC) and filter by asset in a single pass.
2. **Restructure `getAssetDistributionData`**: Aggregate all assets in a single NDC loop rather than calling the NDC loop once per asset.
3. **Add a gas guard**: Revert with a descriptive error if remaining gas falls below a safe threshold before entering the NDC loop.
4. **Cap `maxUncompletedWithdrawalCount` and `maxNodeDelegatorLimit`** at values that keep the worst-case gas within a safe fraction of the block limit, and document those bounds.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Fork test (Hardhat/Foundry, local fork)
// 1. Deploy N supported assets, M NDCs, queue K withdrawals per NDC via operator
// 2. Call updateRSETHPrice() and measure gas

contract PoC_UnboundedGas is Test {
    function test_updateRSETHPrice_OOG() public {
        // Setup: fork mainnet, impersonate admin
        // Add 5 supported assets
        // Add 20 NDCs (increase maxNodeDelegatorLimit first)
        // Operator calls initiateUnstaking() 50 times per NDC
        // Now call updateRSETHPrice() as unprivileged caller
        uint256 gasBefore = gasleft();
        try lrtOracle.updateRSETHPrice() {
            // may succeed with low N/M/K
        } catch {
            // OOGs with high N/M/K
        }
        uint256 gasUsed = gasBefore - gasleft();
        assertLt(gasUsed, 30_000_000, "Exceeded block gas limit");
    }
}
```

The fuzz target is `(N, M, K)` — assert that `updateRSETHPrice()` does not revert with OOG for any combination reachable under the current admin-configurable caps.

### Citations

**File:** contracts/LRTOracle.sol (L336-348)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
```

**File:** contracts/LRTDepositPool.sol (L49-50)
```text
        maxNodeDelegatorLimit = 10;
        lrtConfig = ILRTConfig(lrtConfigAddr);
```

**File:** contracts/LRTDepositPool.sol (L446-456)
```text
        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);

            assetStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetBalance(asset);
            assetUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getAssetUnstaking(asset);

            unchecked {
                ++i;
            }
        }
```

**File:** contracts/NodeDelegator.sol (L303-305)
```text
    {
        if (_getUnstakingVault().uncompletedWithdrawalCount() >= _getUnstakingVault().maxUncompletedWithdrawalCount()) {
            revert MaxUncompletedWithdrawalsReached();
```

**File:** contracts/NodeDelegator.sol (L405-427)
```text
    function getAssetUnstaking(address asset) external view returns (uint256 amount) {
        (IDelegationManager.Withdrawal[] memory queuedWithdrawals, uint256[][] memory withdrawalShares) =
            _getDelegationManager().getQueuedWithdrawals(address(this));

        for (uint256 withdrawalIndex = 0; withdrawalIndex < queuedWithdrawals.length; withdrawalIndex++) {
            IDelegationManager.Withdrawal memory withdrawal = queuedWithdrawals[withdrawalIndex];

            for (uint256 strategyIndex = 0; strategyIndex < withdrawal.strategies.length; strategyIndex++) {
                IStrategy strategy = withdrawal.strategies[strategyIndex];

                address strategyAsset = address(strategy) == address(lrtConfig.beaconChainETHStrategy())
                    ? LRTConstants.ETH_TOKEN
                    : address(strategy.underlyingToken());

                if (strategyAsset != asset) continue;

                uint256 sharesToUnstake = withdrawalShares[withdrawalIndex][strategyIndex];
                amount += strategyAsset == LRTConstants.ETH_TOKEN
                    ? sharesToUnstake
                    : strategy.sharesToUnderlyingView(sharesToUnstake);
            }
        }
    }
```
