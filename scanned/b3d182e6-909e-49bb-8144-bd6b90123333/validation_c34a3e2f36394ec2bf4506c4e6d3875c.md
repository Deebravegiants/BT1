### Title
Validator Exiting Before Credential Verification Permanently Inflates `stakedButUnverifiedNativeETH`, Causing Temporary Fund Freeze and Post-Checkpoint Double-Counting — (`contracts/NodeDelegator.sol`)

---

### Summary

When a beacon chain validator initiates a voluntary exit after `stake32Eth` is called but before `verifyWithdrawalCredentials` is called, EigenLayer's `EigenPod.verifyWithdrawalCredentials` reverts with `ValidatorIsExitingBeaconChain`. Because `NodeDelegator.verifyWithdrawalCredentials` decrements `stakedButUnverifiedNativeETH` **before** the EigenPod call, the revert rolls back the decrement. There is no other code path that decrements `stakedButUnverifiedNativeETH`, so the 32 ETH is permanently stranded in that counter for the affected validator.

---

### Finding Description

**Step 1 — Staking increments the counter:**

`stake32Eth` unconditionally increments `stakedButUnverifiedNativeETH` by 32 ETH. [1](#0-0) 

**Step 2 — Credential verification decrements first, then calls EigenPod:**

`NodeDelegator.verifyWithdrawalCredentials` subtracts `validatorFields.length * 32 ether` from `stakedButUnverifiedNativeETH` **before** delegating to `eigenPod.verifyWithdrawalCredentials`. [2](#0-1) 

If the EigenPod call reverts (e.g., with `ValidatorIsExitingBeaconChain`), the entire transaction reverts and the decrement is rolled back. There is no alternative code path to decrement `stakedButUnverifiedNativeETH`.

**Step 3 — EigenLayer enforces the exit-epoch guard:**

EigenLayer's `IEigenPod` interface documents and declares the `ValidatorIsExitingBeaconChain` error, which is thrown when `verifyWithdrawalCredentials` is called for a validator whose beacon-chain exit epoch is already set. [3](#0-2) 

The NatDoc on the interface function also states: *"Validators proven via this method MUST NOT have an exit epoch set already."* [4](#0-3) 

**Step 4 — `getEffectivePodShares` adds `stakedButUnverifiedNativeETH` to actual EigenLayer shares:** [5](#0-4) 

**Step 5 — `getEffectivePodShares` feeds directly into rsETH price:**

`getETHDistributionData` sums `getEffectivePodShares()` across all NDCs and feeds it into `getTotalAssetDeposits`, which is used by `LRTOracle._getTotalEthInProtocol` to compute the rsETH price. [6](#0-5) [7](#0-6) 

---

### Impact Explanation

**Phase 1 — Temporary freeze (exit epoch set, validator not yet withdrawn):**

The 32 ETH is counted in `stakedButUnverifiedNativeETH` and therefore in `getEffectivePodShares()` and the rsETH price, but no EigenLayer deposit shares have been credited. The ETH cannot be unstaked via `initiateUnstaking` (no shares exist for it). It is inaccessible until the validator fully exits the beacon chain and a checkpoint is completed. Beacon chain exit queues can impose delays of days to weeks.

**Phase 2 — Double-counting after checkpoint (more severe):**

Once the validator fully exits, ETH lands in the EigenPod. After `startCheckpoint` + `verifyCheckpointProofs`, EigenLayer credits the pod ETH as `withdrawableRestakedExecutionLayerGwei`, increasing `withdrawableShare` by ~32 ETH. But `stakedButUnverifiedNativeETH` is **never decremented** for this validator. The result:

```
getEffectivePodShares() = stakedButUnverifiedNativeETH (32 ETH, stuck)
                        + withdrawableShare (32 ETH, from checkpoint)
                        = 64 ETH  ← double-counted
```

This permanently inflates `getEffectivePodShares()`, `getTotalAssetDeposits(ETH)`, and the rsETH price by 32 ETH per affected validator, diluting existing holders and allowing new depositors to receive fewer rsETH than they should.

---

### Likelihood Explanation

This is a realistic operational scenario. The window between `stake32Eth` and `verifyWithdrawalCredentials` can span hours to days (proof generation, operator scheduling). A validator can initiate a voluntary exit at any time. No attacker is required — a validator client misconfiguration, key rotation, or deliberate exit by the validator operator is sufficient. The scenario requires no admin compromise, no governance capture, and no external oracle manipulation.

---

### Recommendation

1. **Decrement after the EigenPod call, not before.** Move `stakedButUnverifiedNativeETH -= ...` to after `eigenPod.verifyWithdrawalCredentials(...)` succeeds. This prevents the counter from being stuck if EigenPod reverts.

2. **Add a recovery function.** Provide a permissioned function (e.g., `onlyLRTManager`) that allows manually decrementing `stakedButUnverifiedNativeETH` for validators that have exited without credential verification, guarded by a proof that the validator's status in EigenPod is `WITHDRAWN` or that the validator's exit epoch is finalized.

3. **Alternatively**, track per-validator state so that `stakedButUnverifiedNativeETH` can be decremented when a checkpoint marks the validator as `WITHDRAWN`.

---

### Proof of Concept

```solidity
// Fork test outline (Holesky or mainnet fork)
// 1. Deploy/use existing NodeDelegator with eigenPod
// 2. Fund NDC with 32 ETH, call stake32Eth(pubkey, sig, root)
//    → assert stakedButUnverifiedNativeETH == 32 ether
// 3. Simulate validator voluntary exit on beacon chain
//    (set exit epoch in beacon state via fork manipulation or use a validator
//     that has already initiated exit)
// 4. Call NodeDelegator.verifyWithdrawalCredentials(beaconTimestamp, ...)
//    → assert revert with IEigenPodErrors.ValidatorIsExitingBeaconChain
// 5. Assert stakedButUnverifiedNativeETH == 32 ether (unchanged)
// 6. Assert getEffectivePodShares() == 32 ether (no EigenLayer shares credited)
// 7. Fast-forward to validator full exit; ETH lands in EigenPod
// 8. Call startCheckpoint + verifyCheckpointProofs
//    → withdrawableShare increases by ~32 ETH
// 9. Assert getEffectivePodShares() == 64 ether (double-counted)
//    → rsETH price is inflated by 32 ETH
```

### Citations

**File:** contracts/NodeDelegator.sol (L165-168)
```text
        // tracks staked but unverified native ETH
        stakedButUnverifiedNativeETH += 32 ether;

        _getEigenPodManager().stake{ value: 32 ether }(pubkey, signature, depositDataRoot);
```

**File:** contracts/NodeDelegator.sol (L235-244)
```text
        if (stakedButUnverifiedNativeETH < validatorFields.length * (32 ether)) {
            revert InsufficientStakedBalance();
        }

        // reduce the eth amount that is verified
        stakedButUnverifiedNativeETH -= (validatorFields.length * (32 ether));

        eigenPod.verifyWithdrawalCredentials(
            beaconTimestamp, stateRootProof, validatorIndices, validatorFieldsProofs, validatorFields
        );
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

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L56-57)
```text
    /// @dev Thrown if a validator is exiting the beacon chain.
    error ValidatorIsExitingBeaconChain();
```

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L196-197)
```text
     * @dev Withdrawal credential proofs MUST NOT be older than `currentCheckpointTimestamp`.
     * @dev Validators proven via this method MUST NOT have an exit epoch set already.
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

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

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
    }
```
