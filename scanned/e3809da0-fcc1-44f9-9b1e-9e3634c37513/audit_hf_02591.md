# [H] Specifying validatorIndex as uint64 allows BeaconProofsLib.validateValidatorProof() to pass with incorrect proofs

## Summary
Severity: High
Contest weight: 0.8796
Dataset id: 13962
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In BeaconProofsLib.validateValidatorProof(), validatorIndex is declared as uint64:
```solidity
function validateValidatorProof(
uint64 validatorIndex,
```
However, validatorIndex should be uint40 instead as the maximum length of validators in BeaconState is 2 ** 40. Any index greater than type(uint40).max is invalid.
This becomes a problem as validatorIndex is OR-ed with the other bits in index:
```solidity
uint256 index = (CONTAINER_IDX « (VALIDATOR_HEIGHT + 1)) | uint256(validatorIndex);
```
Assuming the rightmost bit in index is bit 0, an attacker can set bits 41 to 45 of validatorIndex to switch from the validators field to certain fields after it in BeaconState. You can think of it as modifying CONTAINER_IDX to a different value, which would end up proving a different field in BeaconState.
For example, assume CONTAINER_IDX = 15 and validatorIndex = 0. index would be:
(15 « (VALIDATOR_HEIGHT + 1)) | uint256(0) = 0x1e0000000000
The same value can be reached with CONTAINER_IDX = 12 and validatorIndex = 0x1e0000000000, since:
(12 « (VALIDATOR_HEIGHT + 1)) | uint256(0x1e0000000000) = 0x1e0000000000
If validateValidatorProof() was called with validatorIndex = 0x1e0000000000, the function would end up validating validatorFields against the field at index 15 in BeaconState, which is previous_epoch_participation.
This makes it possible for validateValidatorProof() to pass with an invalid validatorFields.

## Recommendation
Declare validatorIndex as uint40 instead:
```solidity
function validateValidatorProof(
uint64 validatorIndex,
+ uint40 validatorIndex,
bytes32[] calldata validatorFields,
```
This change should be reflected throughout the codebase - any variable that represents the validator's index in the beacon chain should be changed to uint40:
• BeaconProofsLib.sol#L33-L34
• NativeVaultLib.sol#L20-L22
The unsafe cast from uint64 to uint40 at NativeVaultLib.sol#L120 can then be removed.
