### Title
Permissionless `verifyCheckpointProofs` Allows Attacker to Steal Beacon-Chain Yield by Depositing Between Checkpoint Start and Finalization — (`contracts/external/eigenlayer/interfaces/IEigenPod.sol`, `contracts/LRTOracle.sol`, `contracts/NodeDelegator.sol`)

---

### Summary

An unprivileged attacker can deposit ETH into the protocol at the stale (pre-yield) rsETH price after the operator calls `NodeDelegator.startCheckpoint()`, then immediately finalize the checkpoint themselves via the permissionless `IEigenPod.verifyCheckpointProofs()`, and finally call the permissionless `LRTOracle.updateRSETHPrice()`. This causes the attacker's rsETH — minted at the old price — to be instantly worth more than the deposited ETH, stealing a portion of the beacon-chain consensus-layer yield that should accrue only to pre-existing rsETH holders.

---

### Finding Description

**Step 1 — Operator starts checkpoint (normal operation)**

`NodeDelegator.startCheckpoint()` is gated to `onlyLRTOperator` and delegates to `eigenPod.startCheckpoint()`. [1](#0-0) 

At this point the checkpoint is open but not yet finalized. The beacon-chain yield `Y` (accumulated validator balance increases or pod ETH) is **not yet reflected** in EigenLayer shares, because `EigenPodManager.recordBeaconChainETHBalanceUpdate()` is only called when the checkpoint is finalized.

**Step 2 — Attacker deposits at stale price**

`LRTDepositPool.depositETH()` is open to anyone. The rsETH minted is computed as:

```
rsethAmountToMint = depositAmount * getAssetPrice(ETH) / rsETHPrice
``` [2](#0-1) 

`rsETHPrice` is the **last stored price**, which does not yet include `Y`. So the attacker receives `D / P_old` rsETH for `D` ETH deposited.

**Step 3 — Attacker finalizes the checkpoint (permissionless)**

`IEigenPod.verifyCheckpointProofs()` has **no access control**: [3](#0-2) 

The EigenLayer documentation embedded in the interface explicitly states: *"Anyone can call this method to submit proofs towards the current checkpoint."* Calling this finalizes the checkpoint and credits `Y` ETH worth of new shares to the NDC's EigenLayer account via `recordBeaconChainETHBalanceUpdate`.

**Step 4 — Attacker triggers price update (permissionless)**

`LRTOracle.updateRSETHPrice()` has no access control: [4](#0-3) 

`_updateRsETHPrice()` calls `_getTotalEthInProtocol()`, which calls `getETHDistributionData()`, which calls `getEffectivePodShares()` on each NDC: [5](#0-4) 

`getEffectivePodShares()` reads `DelegationManager.getWithdrawableShares()`, which now reflects the newly credited `Y` ETH: [6](#0-5) 

The new price becomes:

```
newRsETHPrice = (N + D + Y - fee) / (S + D/P_old)
```

The attacker's rsETH value is `(D / P_old) * newRsETHPrice`, which exceeds `D` by a fraction of `Y` proportional to the attacker's share of the new total supply.

---

### Impact Explanation

**Impact: High — Theft of unclaimed beacon-chain yield.**

Existing rsETH holders earned yield `Y` through their pre-existing stake. The attacker, by depositing at the stale price and then triggering finalization + price update, dilutes the yield: a portion of `Y` accrues to the attacker's rsETH rather than to pre-existing holders. The attacker profits risk-free (they can immediately redeem/withdraw their rsETH at the new higher price).

---

### Likelihood Explanation

**Likelihood: Medium.**

- The operator must call `startCheckpoint()` before the attacker can act. This is a routine operational step.
- The window between `startCheckpoint()` and `verifyCheckpointProofs()` can be substantial (the operator may not immediately submit proofs).
- Both `verifyCheckpointProofs` and `updateRSETHPrice` are permissionless — no special access is needed.
- The attacker only needs to monitor the chain for `CheckpointCreated` events.

**Partial mitigation — `pricePercentageLimit`:**

`_updateRsETHPrice()` reverts for non-managers if the price increase exceeds `pricePercentageLimit`: [7](#0-6) 

However:
- If `pricePercentageLimit == 0`, this check is entirely skipped (`pricePercentageLimit > 0` is false).
- If the yield `Y` is small relative to TVL (e.g., a few days of staking rewards), the price increase stays within the limit and the attack succeeds fully.
- The attacker can also split across multiple `updateRSETHPrice` calls if needed.

---

### Recommendation

1. **Restrict `updateRSETHPrice` to operators/managers**, or add a time-lock / cooldown after a checkpoint is started before the price can be updated.
2. **Alternatively**, snapshot the rsETH supply at `startCheckpoint()` time and use that supply for yield distribution, so late depositors do not benefit from yield earned before their entry.
3. **Ensure `pricePercentageLimit` is always set to a non-zero value** as a defense-in-depth measure, and document that it is a required configuration.
4. Consider emitting a `CheckpointStarted` event from `NodeDelegator.startCheckpoint()` and pausing deposits until the checkpoint is finalized.

---

### Proof of Concept

```solidity
// Fork test (Holesky or mainnet fork)
// Preconditions:
//   - NDC has validators with accumulated yield Y (e.g., 1 ETH in pod balance)
//   - rsETH supply S = 1000 ether, rsETHPrice P = 1.05 ether, TVL N = 1050 ether
//   - pricePercentageLimit = 0 (or Y/N < limit)

// 1. Operator starts checkpoint
vm.prank(operator);
nodeDelegator.startCheckpoint(false);
// rsETHPrice is still 1.05 ether; Y not yet reflected

// 2. Attacker deposits 10 ETH at stale price
vm.prank(attacker);
lrtDepositPool.depositETH{value: 10 ether}(0, "");
// Attacker receives 10e18 / 1.05e18 ≈ 9.523 rsETH

// 3. Attacker finalizes checkpoint (permissionless)
eigenPod.verifyCheckpointProofs(balanceContainerProof, proofs);
// EigenLayer now credits Y = 1 ETH of new shares to NDC

// 4. Attacker triggers price update (permissionless)
lrtOracle.updateRSETHPrice();
// newTVL = 1050 + 10 + 1 = 1061 ETH (minus fee)
// newSupply = 1000 + 9.523 = 1009.523 rsETH
// newPrice ≈ 1061 / 1009.523 ≈ 1.051 ether

// 5. Assert attacker profit
uint256 attackerRsETH = rsETH.balanceOf(attacker); // ≈ 9.523 rsETH
uint256 attackerValue = attackerRsETH * lrtOracle.rsETHPrice() / 1e18; // ≈ 10.009 ETH
assertGt(attackerValue, 10 ether); // Attacker gained ~0.009 ETH of yield
// Pre-existing holders lost a proportional share of the 1 ETH yield
```

The attacker's gain scales with `Y * (attackerShare / totalSupply)`. For large yield accumulations (e.g., after a long period without checkpointing), the stolen amount is material.

### Citations

**File:** contracts/NodeDelegator.sol (L259-261)
```text
    function startCheckpoint(bool revertIfNoBalance) external onlyLRTOperator {
        eigenPod.startCheckpoint(revertIfNoBalance);
    }
```

**File:** contracts/NodeDelegator.sol (L556-562)
```text
    function getEffectivePodShares() external view override returns (uint256 ethStaked) {
        uint256 withdrawableShare =
            NodeDelegatorHelper.getWithdrawableShare(lrtConfig, IStrategy(lrtConfig.beaconChainETHStrategy()));

        // staker balances can no longer be negative
        return stakedButUnverifiedNativeETH + withdrawableShare;
    }
```

**File:** contracts/LRTDepositPool.sol (L487-488)
```text
            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L176-190)
```text
     * @dev Progress the current checkpoint towards completion by submitting one or more validator
     * checkpoint proofs. Anyone can call this method to submit proofs towards the current checkpoint.
     * For each validator proven, the current checkpoint's `proofsRemaining` decreases.
     * @dev If the checkpoint's `proofsRemaining` reaches 0, the checkpoint is finalized.
     * (see `_updateCheckpoint` for more details)
     * @dev This method can only be called when there is a currently-active checkpoint.
     * @param balanceContainerProof proves the beacon's current balance container root against a checkpoint's
     * `beaconBlockRoot`
     * @param proofs Proofs for one or more validator current balances against the `balanceContainerRoot`
     */
    function verifyCheckpointProofs(
        BeaconChainProofs.BalanceContainerProof calldata balanceContainerProof,
        BeaconChainProofs.BalanceProof[] calldata proofs
    )
        external;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
```
