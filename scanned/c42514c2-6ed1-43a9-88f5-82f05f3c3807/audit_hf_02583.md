# [H] Wrong use of the beacon block root instead of the beacon state root in NativeVault.validateWithdrawalCredentials().

## Summary
Severity: High
Contest weight: 0.5379
Dataset id: 13954
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
NativeVaultLib.validateWithdrawalCredentials() expects the parameter bytes32 beaconStateRoot. In NativeVault.validateWithdrawalCredentials(), beaconStateRootProof.beaconStateRoot is verified, however, It is the beacon block root that is passed to NativeVaultLib.validateWithdrawalCredentials(), which is incorrect. The beacon state root should be supplied instead.

## Recommendation
```solidity
@@ -183,7 +186,7 @@ contract NativeVault is ERC4626, IBeacon, Pauser, INativeVault,
OwnableRoles, Re
totalRestakedWei += self.validateWithdrawalCredentials(
nodeOwner,
beaconStateRootProof.timestamp,
_getParentBlockRoot(beaconStateRootProof.timestamp),
+ beaconStateRootProof.beaconStateRoot,
```
