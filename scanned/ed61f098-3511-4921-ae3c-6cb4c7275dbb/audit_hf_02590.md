# [H] Calling validateWithdrawalCredentials() followed by startSnapshot()/validateExpiredSnapshot() will permanently DOS snapshots

## Summary
Severity: High
Contest weight: 0.8957
Dataset id: 13961
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
NativeVaultLib.validateWithdrawalCredentials() has the following checks for beaconStateRootProof.timestamp:
```solidity
if (
beaconStateRootProof.timestamp < node.lastSnapshotTimestamp
|| beaconStateRootProof.timestamp < node.currentSnapshotTimestamp
) revert BeaconTimestampTooOld();
```
As seen from above, only restriction on beaconStateRootProof.timestamp is that it cannot be older than the last/ongoing snapshot. This makes it possible for beaconStateRootProof.timestamp to be block.timestamp.
Later on in the function, the newly added validator's lastBalanceUpdateTimestamp is set to beaconStateRootProof.timestamp in NativeVaultLib.validateWithdrawalCredentials():
```solidity
validatorDetails.lastBalanceUpdateTimestamp = updateTimestamp;
```
However, if startSnapshot() or validateExpiredSnapshot() is called after validateWithdrawalCredentials() in the same block, the newly added validator cannot be proven with validateSnapshotProofs() due to the following check:
```solidity
if (validatorDetails.lastBalanceUpdateTimestamp >= node.currentSnapshotTimestamp) {
revert ValidatorAlreadyProved();
}
```
This will make it impossible to complete the snapshot as the newly added validator can never be proven, so snapshot.remainingProofs will never reach 0. For example:
• Assume a node owner has no validators.
• In the block where block.timestamp = 1000:
– validateWithdrawalCredentials() is called:
* Assume beaconStateRootProof.timestamp = block.timestamp.
* validator.lastBalanceUpdateTimestamp = 1000.
* node.activeValidatorCount is incremented to 1.
– startSnapshot() is called to start a new snapshot:
* snapshot.remainingProofs = 1
* node.currentSnapshotTimestamp = 1000
• When attempting to prove the validator with validateSnapshotProofs():
– Both validatorDetails.lastBalanceUpdateTimestamp and node.currentSnapshotTimestamp are 1000, so the check shown above reverts.
• As such, the validator can never be proven and snapshot.remainingProofs is forever stuck at 1.
If this occurs, snapshots will be forever DOSed for the node owner.

## Recommendation
Ensure that validateWithdrawalCredentials() cannot be called with beaconStateRootProof.timestamp as block.timestamp by adding the following check:
```solidity
if (beaconStateRootProof.timestamp == block.timestamp) {
revert BeaconTimestampIsCurrent();
}
```
Note that even without this check, it is unlikely for validateWithdrawalCredentials() to be called with block.timestamp as it is difficult to generate proofs for a block root returned by _getParentBlockRoot() in a future block.
