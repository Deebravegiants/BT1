# [M] Missing validatorProof.length check in BeaconProofsLib.validateValidatorProof()

## Summary
Severity: Medium
Contest weight: 0.0919
Dataset id: 13972
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In BeaconProofsLib.validateValidatorProof(), there is no check on the length of validatorProof, which allows an attacker to freely specify the number of proof hashes to be used in verifyInclusionSha256().
If it is shorter than it should be, the number of times validatorRoot is hashed will be less. This could potentially cause validateValidatorProof() to pass with an invalid validatorRoot.

## Recommendation
The length of validatorProof should be the height of the merkleized Validator list + the height of the merkleized BeaconState container. Consider adding the following check:
```diff
- if (!Merkle.verifyInclusionSha256(validatorProof, beaconStateRoot, validatorRoot, index)) {
+ if (
+
    validatorProof.length != 32 * ((VALIDATOR_HEIGHT + 1) + BEACON_STATE_HEIGHT) ||
+
    !Merkle.verifyInclusionSha256(validatorProof, beaconStateRoot, validatorRoot, index)
+ ) {
    revert InvalidValidatorFieldsProof();
}
```
