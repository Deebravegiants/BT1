# [H] NativeVault.validateExpiredSnapshot() cannot be called on a node owner with no active validators

## Summary
Severity: High
Contest weight: 0.7844
Dataset id: 13958
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
NativeVault.validateExpiredSnapshot() contains the following checks:
```solidity
NativeVaultLib.ValidatorDetails memory validatorDetails =
node.validatorPubkeyHashToDetails[validatorPubkey];
if (beaconStateRootProof.timestamp < validatorDetails.lastBalanceUpdateTimestamp +
Constants.SNAPSHOT_EXPIRY) {
revert SnapshotNotExpired();
}
if (validatorDetails.status != NativeVaultLib.ValidatorStatus.ACTIVE) revert
ValidatorNotActive();
```
As seen from above, validateExpiredSnapshot() can only be called when an active validator's lastBalanceUpdateTimestamp is more than 7 days ago. As such, it is not possible to call validateExpiredSnapshot() when a user has no active validators, even if his last snapshot has expired.
When slashing occurs, this would make it impossible to forcefully update a node owner's snapshot.
As a result, the node owner's balance will never be updated and slashStore might never receive the slashed funds.
For example:
• Node owner has one active validator with 32 ETH.
• Node owner performs a full withdrawal for his validator. Its status is now WITHDRAW and the 32 ETH is moved into his native node.
• Karak operator calls slashAssets() to perform slashing, which reduces his balance to 31 ETH.
• Since the node owner has no more active validators, validateExpiredSnapshot() cannot be called.
In this scenario, it is impossible to forcefully move 1 ETH from the node owner's native node into slashStore and update his balance. If the node owner chooses to withdraw his remaining 31 ETH and never calls startSnapshot(), slashStore will never receive the 1 ETH that was slashed.
Recomendation:
Consider checking if a node owner's last snapshot has expired with node.lastSnapshotTimestamp instead:
```solidity
function validateExpiredSnapshot(
address nodeOwner,
) external nodeExists(nodeOwner)
whenFunctionNotPaused(Constants.PAUSE_NATIVEVAULT_VALIDATE_EXPIRED_SNAPSHOT) {
NativeVaultLib.Storage storage self = _state();
NativeVaultLib.NativeNode storage node = self.ownerToNode[nodeOwner];
if (block.timestamp < node.lastSnapshotTimestamp + Constants.SNAPSHOT_EXPIRY) {
revert SnapshotNotExpired();
}
_startSnapshot(node, false, nodeOwner);
}
```

## Recommendation
No data
