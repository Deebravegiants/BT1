### Title
Stale `getEffectivePodShares()` During Incomplete EigenLayer Checkpoint Inflates `highestRsethPrice`, Triggering Automatic Protocol Pause on Checkpoint Completion — (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle.updateRSETHPrice()` reads ETH TVL through `getEffectivePodShares()`, which queries EigenLayer's `DelegationManager.getWithdrawableShares()`. This value is only updated when an EigenPod checkpoint is **finalized**. During an incomplete checkpoint (after beacon-chain slashing, while `proofsRemaining > 0`), the withdrawable-share figure still reflects the pre-slashing balance. If `updateRSETHPrice()` is called during this window, it sets `highestRsethPrice` to an inflated value. When the checkpoint later finalizes and the true (lower) balance is reflected, the next `updateRSETHPrice()` call computes a price below `highestRsethPrice` by more than `pricePercentageLimit`, automatically pausing `LRTDepositPool` and `LRTWithdrawalManager`.

---

### Finding Description

**Step 1 — TVL source during an incomplete checkpoint**

`getETHDistributionData()` sums `getEffectivePodShares()` across all NodeDelegators: [1](#0-0) 

`getEffectivePodShares()` returns `stakedButUnverifiedNativeETH + withdrawableShare`, where `withdrawableShare` comes from EigenLayer's `DelegationManager.getWithdrawableShares()`: [2](#0-1) 

`getWithdrawableShares` is computed as `depositShares × depositScalingFactor × slashingFactor`. For beacon-chain ETH, `depositShares` equals `podOwnerDepositShares` in `EigenPodManager`, which is **only updated when a checkpoint is finalized** via `recordBeaconChainETHBalanceUpdate`. During an incomplete checkpoint, this value still reflects the last finalized (pre-slashing) balance. [3](#0-2) 

**Step 2 — `highestRsethPrice` is set from inflated TVL**

`_updateRsETHPrice()` computes `newRsETHPrice` from `_getTotalEthInProtocol()` (which calls `getEffectivePodShares()`), then updates `highestRsethPrice` if the new price exceeds it: [4](#0-3) 

If `updateRSETHPrice()` is called while the checkpoint is incomplete, `newRsETHPrice` is inflated (pre-slashing TVL), and `highestRsethPrice` is set to this inflated value.

**Step 3 — Checkpoint finalizes, price corrects, pause triggers**

Once all `verifyCheckpointProofs` calls are submitted and the checkpoint finalizes, `podOwnerDepositShares` drops to reflect the actual slashed balance. The next call to `updateRSETHPrice()` computes a lower `newRsETHPrice`. If the drop exceeds `pricePercentageLimit`: [5](#0-4) 

`LRTDepositPool.pause()` and `LRTWithdrawalManager.pause()` are called automatically, freezing all user deposits and withdrawals.

**Step 4 — No automated recovery**

`unpause()` on both contracts requires `onlyLRTAdmin`: [6](#0-5) [7](#0-6) 

There is no automated recovery path; admin must manually intervene.

---

### Impact Explanation

All user deposits (`LRTDepositPool.depositETH`, `depositAsset`) and all withdrawals (`LRTWithdrawalManager.initiateWithdrawal`, `claimWithdrawal`) are blocked until admin manually unpauses. This constitutes **temporary freezing of funds** for all protocol users.

---

### Likelihood Explanation

- Beacon-chain slashing is a real, documented event (correlation penalties can be significant).
- `startCheckpoint` is restricted to `onlyLRTOperator`, so the operator initiates it; with many active validators, completing all proofs takes time.
- `verifyCheckpointProofs` is permissionless (anyone can submit proofs), but gathering and submitting proofs for a large validator set takes multiple transactions and real time.
- `updateRSETHPrice()` is a public, permissionless function callable by anyone at any time, making it trivial to call it during the incomplete-checkpoint window.
- The combination of slashing + large validator set + public price update creates a realistic, non-contrived scenario.

---

### Recommendation

1. **Checkpoint-aware price guard**: In `_updateRsETHPrice()`, check whether any NodeDelegator's EigenPod has an active checkpoint (`currentCheckpointTimestamp() != 0`). If so, skip updating `highestRsethPrice` (or skip the entire price update) until the checkpoint is finalized.
2. **Separate `highestRsethPrice` update from the pause trigger**: Only update `highestRsethPrice` when the price increase is verified to be from real yield, not from a stale pre-checkpoint read.
3. **Operator tooling**: Ensure operators complete checkpoints promptly after slashing events to minimize the stale-data window.

---

### Proof of Concept

```
Fork test outline (Mainnet fork, no public-mainnet state changes):

1. Deploy/fork with a NodeDelegator that has N active validators (e.g., 100).
2. Simulate beacon-chain slashing: reduce podOwnerDepositShares in EigenPodManager
   to reflect a 10% slash (achievable in fork test by manipulating storage or
   using EigenLayer's test harness).
3. Call NodeDelegator.startCheckpoint(false) — checkpoint starts, proofsRemaining = N.
4. Call LRTOracle.updateRSETHPrice() — price is computed from inflated
   getEffectivePodShares() (pre-slashing podOwnerDepositShares).
   Assert: highestRsethPrice == inflated_price.
5. Submit all verifyCheckpointProofs — checkpoint finalizes,
   podOwnerDepositShares drops by 10%.
6. Call LRTOracle.updateRSETHPrice() again.
   Assert: newRsETHPrice < highestRsethPrice by > pricePercentageLimit.
   Assert: LRTDepositPool.paused() == true.
   Assert: LRTWithdrawalManager.paused() == true.
```

### Citations

**File:** contracts/LRTDepositPool.sol (L353-356)
```text
    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```

**File:** contracts/LRTDepositPool.sol (L484-489)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
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

**File:** contracts/NodeDelegatorHelper.sol (L52-65)
```text
    function getWithdrawableShare(
        ILRTConfig lrtConfig,
        IStrategy strategy
    )
        internal
        view
        returns (uint256 withdrawableShare)
    {
        IStrategy[] memory strategies = new IStrategy[](1);
        strategies[0] = strategy;

        uint256[] memory withdrawableShares = getWithdrawableShares(lrtConfig, strategies);
        return withdrawableShares[0];
    }
```

**File:** contracts/LRTOracle.sol (L250-296)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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
        }

        // downside protection — pause if price drops too far
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }

            // if price has decreased compared to the previous price, emit an event to reflect that
            if (previousPrice > newRsETHPrice) {
                emit RsETHPriceDecrease(newRsETHPrice, previousPrice);
            }

            // emit an event to notify that the price is currently below the peak (all time high) price
            emit RsETHPriceBelowPeak(highestRsethPrice, newRsETHPrice);
        }

        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L351-354)
```text
    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```
