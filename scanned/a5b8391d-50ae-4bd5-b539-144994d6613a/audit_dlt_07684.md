# [?] Caplin: fix smol panic (#13715)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-02-06
Source: https://github.com/erigontech/erigon/commit/e9875c0c0a19f1b9c6c47dbb4e6929cf6bad320a
Type: security-commit

## Details
Caplin: fix smol panic (#13715)

## Patch
### cl/cltypes/solid/validator_set.go
```diff
@@ -91,7 +91,7 @@ func (v *ValidatorSet) expandBuffer(newValidatorSetLength int) {
 func (v *ValidatorSet) Append(val Validator) {
 	offset := v.EncodingSizeSSZ()
 	// we are overflowing the buffer? append.
-	if offset >= len(v.buffer) {
+	if offset+validatorSize >= len(v.buffer) {
 		v.expandBuffer(v.l + 1)
 		v.phase0Data = append(v.phase0Data, Phase0Data{})
 	}
```
