### Title
Permissionless `verifyStaleBalance` Enables Griefing of `NodeDelegator.verifyWithdrawalCredentials`, Temporarily Freezing 32 ETH per Unverified Validator — (`contracts/NodeDelegator.sol`)

---

### Summary

`IEigenPod.verifyStaleBalance()` is explicitly permissionless — any external caller can invoke it directly on the EigenPod to start a checkpoint whenever a slashed ACTIVE validator exists. Once a checkpoint is active, EigenLayer's `verifyWithdrawalCredentials` rejects any proof whose `beaconTimestamp < currentCheckpointTimestamp`. Because `NodeDelegator.verifyWithdrawalCredentials` does not check for an active checkpoint before proceeding, an attacker can force the operator's credential-verification transactions to revert, leaving 32 ETH per affected validator stranded in `stakedButUnverifiedNativeETH` until the checkpoint is completed and fresh proofs are obtained.

---

### Finding Description

**Permissionless checkpoint entry point**

`IEigenPod.verifyStaleBalance()` carries no access-control restriction. The interface NatDoc explicitly states:

> "Note that this method allows anyone to start a checkpoint as soon as a slashing occurs on the beacon chain." [1](#0-0) 

Any address can call `eigenPod.verifyStaleBalance(...)` directly — bypassing `NodeDelegator.startCheckpoint`, which is `onlyLRTOperator`. [2](#0-1) 

**EigenLayer's hard timestamp constraint**

Once a checkpoint is active with timestamp `T`, EigenLayer's `verifyWithdrawalCredentials` rejects any proof with `beaconTimestamp < T`. This is documented in both the EigenPod interface and the NodeDelegator NatDoc: [3](#0-2) [4](#0-3) 

**No active-checkpoint guard in `NodeDelegator.verifyWithdrawalCredentials`**

The function decrements `stakedButUnverifiedNativeETH` and then calls `eigenPod.verifyWithdrawalCredentials`. There is no pre-flight check for `currentCheckpointTimestamp`: [5](#0-4) 

If the EigenPod call reverts (because `beaconTimestamp < currentCheckpointTimestamp`), the whole transaction reverts, so `stakedButUnverifiedNativeETH` is not permanently decremented. However, the operator's prepared proofs are now stale and the call cannot succeed until:
1. The active checkpoint is fully completed (one `verifyCheckpointProofs` call per ACTIVE validator).
2. New proofs with `beaconTimestamp >= T` are generated and submitted.

**`stakedButUnverifiedNativeETH` inflates `getEffectivePodShares` without backing EigenLayer shares**

During the freeze window, `getEffectivePodShares` counts the stranded ETH: [6](#0-5) 

The ETH is included in TVL/share-price calculations but is not backed by credited EigenLayer deposit shares, creating a temporary accounting discrepancy.

---

### Impact Explanation

- **32 ETH per unverified validator** is temporarily locked in `stakedButUnverifiedNativeETH` and cannot be credited as EigenLayer restaking shares.
- The operator must complete the checkpoint (potentially expensive if many ACTIVE validators exist) and re-generate beacon-chain proofs before `verifyWithdrawalCredentials` can succeed.
- During this window, the ETH is counted in TVL but not usable for restaking, delegation, or withdrawal flows that depend on credited EigenLayer shares.
- Impact: **Medium — Temporary freezing of funds**.

---

### Likelihood Explanation

- **Precondition**: At least one ACTIVE validator in the pod must be slashed on the beacon chain. Slashings are uncommon but real production events; large operators with many validators face non-trivial cumulative probability.
- **Attack execution**: Permissionless — any EOA can call `eigenPod.verifyStaleBalance(beaconTimestamp, stateRootProof, proof)` directly. No privileged role, no capital, no front-running required (the attacker can act at any time after a slashing, before the operator submits credential proofs).
- **Repeatability**: The attacker can repeat the attack for every subsequent slashing event, continuously delaying credential verification.

---

### Recommendation

Add a pre-flight check in `NodeDelegator.verifyWithdrawalCredentials` that reverts with a descriptive error if an active checkpoint exists, so the operator is informed rather than receiving a cryptic EigenPod revert:

```solidity
if (eigenPod.currentCheckpointTimestamp() != 0) {
    revert ActiveCheckpointExists();
}
```

Additionally, document that operators must monitor for permissionless checkpoint starts (via `verifyStaleBalance`) and complete any active checkpoint before attempting credential verification.

---

### Proof of Concept

```solidity
// Fork test (Holesky or mainnet fork)
// Preconditions:
//   - NodeDelegator has staked 32 ETH for ValidatorA (stakedButUnverifiedNativeETH = 32 ether)
//   - ValidatorB is ACTIVE in the pod and has been slashed on the beacon chain

// Step 1: Attacker starts checkpoint via verifyStaleBalance (permissionless)
eigenPod.verifyStaleBalance(
    slashBeaconTimestamp,   // timestamp T of slashing proof
    stateRootProof,
    slashedValidatorProof
);
// currentCheckpointTimestamp() == T > 0

// Step 2: Operator attempts to verify ValidatorA's withdrawal credentials with old proof
// (beaconTimestamp < T)
vm.prank(lrtOperator);
vm.expectRevert(); // EigenPod rejects: beaconTimestamp < currentCheckpointTimestamp
nodeDelegator.verifyWithdrawalCredentials(
    oldBeaconTimestamp,     // < T
    stateRootProof,
    validatorIndices,
    validatorFieldsProofs,
    validatorFields
);

// Step 3: Assert stakedButUnverifiedNativeETH is unchanged (tx reverted)
assertEq(nodeDelegator.stakedButUnverifiedNativeETH(), 32 ether);

// Step 4: Complete checkpoint, obtain new proof with beaconTimestamp >= T
nodeDelegator.startCheckpoint(false); // or verifyCheckpointProofs directly
// ... submit checkpoint proofs for all ACTIVE validators ...

// Step 5: Now verifyWithdrawalCredentials succeeds with fresh proof
vm.prank(lrtOperator);
nodeDelegator.verifyWithdrawalCredentials(
    newBeaconTimestamp,     // >= T
    newStateRootProof,
    validatorIndices,
    validatorFieldsProofs,
    validatorFields
);
assertEq(nodeDelegator.stakedButUnverifiedNativeETH(), 0);
```

### Citations

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L222-223)
```text
     * @dev Note that this method allows anyone to start a checkpoint as soon as a slashing occurs on the beacon
     * chain. This is intended to make it easier to external watchers to keep a pod's balance up to date.
```

**File:** contracts/external/eigenlayer/interfaces/IEigenPod.sol (L304-305)
```text
    /// @notice The timestamp of the currently-active checkpoint. Will be 0 if there is not active checkpoint
    function currentCheckpointTimestamp() external view returns (uint64);
```

**File:** contracts/NodeDelegator.sol (L215-216)
```text
     * @dev Withdrawal credential proofs MUST NOT be older than `currentCheckpointTimestamp`.
     * @dev Validators proven via this method MUST NOT have an exit epoch set already.
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
