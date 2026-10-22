# [H] Missing increment for node.activeValidatorCount in NativeVault.validateWithdrawalCredentials()

## Summary
Severity: High
Contest weight: 0.7419
Dataset id: 13957
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Node owners call NativeVault.validateWithdrawalCredentials() to add active validators to their native node:
```solidity
for (uint256 i = 0; i < validatorFieldsProofs.length; i++) {
totalRestakedWei += self.validateWithdrawalCredentials(
nodeOwner,
beaconStateRootProof.timestamp,
_getParentBlockRoot(beaconStateRootProof.timestamp),
validatorFieldsProofs[i]
);
}
```
However, after calling NativeVaultLib.validateWithdrawalCredentials() to add all active validators in the loop above, the function does not increment node.activeValidatorCount (ie. the number of active validators in a native node) by the number of new validators added.
This makes it impossible to update the validator's balance in future snapshots as the number of active validators for all native nodes will always remain at 0.

## Recommendation
Increment node.activeValidatorCount by the number of active validators added as such:
```solidity
for (uint256 i = 0; i < validatorFieldsProofs.length; i++) {
totalRestakedWei += self.validateWithdrawalCredentials(
);
}
+ node.activeValidatorCount += validatorFieldsProofs.length;
```
