# [?] fix verWatcher race condition in tests

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2022-05-13
Source: https://github.com/0xsoniclabs/sonic/commit/60bdf4b746de7c9b6bba4fe3876b0905401a9c72
Type: security-commit

## Details
fix verWatcher race condition in tests

## Patch
### gossip/common_test.go
```diff
@@ -201,6 +201,7 @@ func newTestEnv(firstEpoch idx.Epoch, validatorsNum idx.Validator) *testEnv {
 }
 
 func (env *testEnv) Close() {
+	env.verWatcher.Stop()
 	env.store.Close()
 	env.tflusher.Stop()
 }
```
