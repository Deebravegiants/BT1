### Title
Permissionless `verifyStaleBalance` + `verifyCheckpointProofs` Sequence Triggers Auto-Pause, Temporarily Freezing Pending Unlocked Withdrawals — (`contracts/LRTOracle.sol`, `contracts/external/eigenlayer/interfaces/IEigenPod.sol`)

---

### Summary

An unprivileged attacker can call `IEigenPod.verifyStaleBalance` and `IEigenPod.verifyCheckpointProofs` directly on the NDC's EigenPod (both are explicitly permissionless), finalize a checkpoint that reflects a slashed validator's reduced balance, then call the public `LRTOracle.updateRSETHPrice()` to trigger the downside auto-pause. This pauses `LRTWithdrawalManager`, blocking `completeWithdrawal` for users who already have unlocked requests. The freeze is **temporary** (admin can unpause), not permanent, so the impact is **Medium — temporary freezing of funds**, not Critical insolvency.

---

### Finding Description

**Permissionless EigenPod entry points**

`IEigenPod.verifyStaleBalance` is explicitly documented as callable by anyone:

> *"Note that this method allows anyone to start a checkpoint as soon as a slashing occurs on the beacon chain. This is intended to make it easier for external watchers to keep a pod's balance up to date."* [1](#0-0) 

`IEigenPod.verifyCheckpointProofs` is similarly permissionless:

> *"Anyone can call this method to submit proofs towards the current checkpoint."* [2](#0-1) 

**Share reduction propagates to rsETH price**

After the checkpoint finalizes, EigenLayer calls `recordBeaconChainETHBalanceUpdate`, reducing the NDC's withdrawable shares. `NodeDelegator.getEffectivePodShares()` reads those shares directly: [3](#0-2) 

`LRTDepositPool.getETHDistributionData()` sums `getEffectivePodShares()` across all NDCs: [4](#0-3) 

`LRTOracle._getTotalEthInProtocol()` uses this sum to compute `newRsETHPrice`.

**Auto-pause on price drop**

`LRTOracle._updateRsETHPrice()` compares `newRsETHPrice` against `highestRsethPrice`. If the drop exceeds `pricePercentageLimit`, it pauses `LRTDepositPool`, `LRTWithdrawalManager`, and itself: [5](#0-4) 

`updateRSETHPrice()` is a public, permissionless function: [6](#0-5) 

**Withdrawal completion blocked**

`completeWithdrawal` carries `whenNotPaused`: [7](#0-6) 

Users with already-unlocked requests (whose `expectedAssetAmount` was fixed at `unlockQueue` time) cannot complete them while the pause is active.

---

### Impact Explanation

The impact is **Medium — temporary freezing of funds**, not Critical/permanent:

- `LRTWithdrawalManager.unpause()` is callable by `onlyLRTAdmin` at any time, restoring access.
- `completeWithdrawal` uses the `request.expectedAssetAmount` fixed at unlock time, so users receive the amount they were promised once unpaused — no value is lost.
- The slashing loss itself is real and would eventually be reflected regardless; the attacker only accelerates the price update. [8](#0-7) 

The claimed "permanent freezing / protocol insolvency" is **not reachable**: the admin unpause path is always available and does not require any price condition to be met first.

---

### Likelihood Explanation

Requires a real beacon-chain slashing event on one of the NDC's validators (not attacker-controlled), plus the `pricePercentageLimit` being set to a value the slashing drop exceeds. Both conditions are plausible in production. The three attacker calls (`verifyStaleBalance`, `verifyCheckpointProofs`, `updateRSETHPrice`) are all permissionless and can be batched in a single transaction.

---

### Recommendation

1. **Delay price-drop auto-pause**: Instead of pausing immediately on a single `updateRSETHPrice` call, require the price to remain below the threshold for N consecutive updates or a time window before pausing.
2. **Separate withdrawal completion from oracle pause**: Allow `completeWithdrawal` for already-unlocked requests (where `expectedAssetAmount` is already fixed) even when the oracle/withdrawal-manager is paused, since those requests carry no price risk.
3. **Access-gate `verifyStaleBalance` effects**: Consider wrapping the NDC's EigenPod interaction so that only the operator can trigger checkpoints, or monitor for unexpected checkpoint starts off-chain and respond before `updateRSETHPrice` is called.

---

### Proof of Concept

```solidity
// Fork test (mainnet fork, post-slashing block)
function testAttackerTriggersAutoPause() external {
    // Preconditions: NDC has ACTIVE slashed validator, no active checkpoint,
    // pricePercentageLimit set, LRTWithdrawalManager has unlocked requests.

    address attacker = makeAddr("attacker");
    IEigenPod pod = NodeDelegator(ndc).eigenPod();

    vm.startPrank(attacker);
    // Step 1: start checkpoint via staleness proof
    pod.verifyStaleBalance(beaconTimestamp, stateRootProof, validatorProof);
    // Step 2: finalize checkpoint with slashed balance
    pod.verifyCheckpointProofs(balanceContainerProof, balanceProofs);
    // Step 3: trigger auto-pause
    LRTOracle(oracle).updateRSETHPrice();
    vm.stopPrank();

    assertTrue(LRTWithdrawalManager(withdrawalManager).paused());

    // Step 4: user cannot complete their unlocked withdrawal
    vm.prank(user);
    vm.expectRevert("Pausable: paused");
    LRTWithdrawalManager(withdrawalManager).completeWithdrawal(asset, "");
}
```

### Citations

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L175-191)
```text
    /**
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

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L215-250)
```text
    /**
     * @dev Prove that one of this pod's active validators was slashed on the beacon chain. A successful
     * staleness proof allows the caller to start a checkpoint.
     *
     * @dev Note that in order to start a checkpoint, any existing checkpoint must already be completed!
     * (See `_startCheckpoint` for details)
     *
     * @dev Note that this method allows anyone to start a checkpoint as soon as a slashing occurs on the beacon
     * chain. This is intended to make it easier to external watchers to keep a pod's balance up to date.
     *
     * @dev Note too that beacon chain slashings are not instant. There is a delay between the initial slashing event
     * and the validator's final exit back to the execution layer. During this time, the validator's balance may or
     * may not drop further due to a correlation penalty. This method allows proof of a slashed validator
     * to initiate a checkpoint for as long as the validator remains on the beacon chain. Once the validator
     * has exited and been checkpointed at 0 balance, they are no longer "checkpoint-able" and cannot be proven
     * "stale" via this method.
     * See https://eth2book.info/capella/part3/transition/epoch/#slashings for more info.
     *
     * @param beaconTimestamp the beacon chain timestamp sent to the 4788 oracle contract. Corresponds
     * to the parent beacon block root against which the proof is verified.
     * @param stateRootProof proves a beacon state root against a beacon block root
     * @param proof the fields of the beacon chain "Validator" container, along with a merkle proof against
     * the beacon state root. See the consensus specs for more details:
     * https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#validator
     *
     * @dev Staleness conditions:
     * - Validator's last checkpoint is older than `beaconTimestamp`
     * - Validator MUST be in `ACTIVE` status in the pod
     * - Validator MUST be slashed on the beacon chain
     */
    function verifyStaleBalance(
        uint64 beaconTimestamp,
        BeaconChainProofs.StateRootProof calldata stateRootProof,
        BeaconChainProofs.ValidatorProof calldata proof
    )
        external;
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

**File:** contracts/LRTDepositPool.sol (L484-493)
```text
        for (uint256 i; i < ndcsCount;) {
            ethLyingInNDCs += nodeDelegatorQueue[i].balance;

            ethStakedInEigenLayer += INodeDelegator(nodeDelegatorQueue[i]).getEffectivePodShares();
            ethUnstakingFromEigenLayer += INodeDelegator(nodeDelegatorQueue[i])
                .getAssetUnstaking(LRTConstants.ETH_TOKEN);
            unchecked {
                ++i;
            }
        }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
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
```

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L351-354)
```text
    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```
