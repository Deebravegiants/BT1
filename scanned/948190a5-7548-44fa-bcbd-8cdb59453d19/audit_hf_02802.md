# [M] Base contracts inherited by the upgradeable Vault contract need storage gaps

## Summary
Severity: Medium
Contest weight: 0.0838
Dataset id: 15243
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
For upgradeable contracts, there must be a storage gap to allow the addition of new state variables in the future without compromising the storage compatibility with existing deployments. Without a storage gap, if there are any new variables in the DivaBeaconOracle contract, they will override variables in the Vault contract, since Vault extends DivaBeaconOracle.
OpenZeppelin Reference here.

## Recommendation
```diff
@@ -11,6 +11,7 @@ contract DivaBeaconOracle {
/// @notice Mapping from validator index to validator struct
mapping(uint256 => BeaconOracleHelper.Validator) public validatorState;
+
uint256[50] __gap;
/// @notice Prove slashed & status epochs
function proveValidatorField(
BeaconOracleHelper.BeaconStateRootProofInfo calldata
_beaconStateRootProofInfo,
```
