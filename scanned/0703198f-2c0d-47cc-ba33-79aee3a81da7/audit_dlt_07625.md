# [?] tests: fix nil pointer panic on failure (#23053)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2021-06-18
Source: https://github.com/ethereum/go-ethereum/commit/58aeab77d219204af414602d30ae34d5adf10382
Type: security-commit

## Details
tests: fix nil pointer panic on failure (#23053)

## Patch
### tests/state_test.go
```diff
@@ -74,8 +74,10 @@ func TestState(t *testing.T) {
 				t.Run(key+"/snap", func(t *testing.T) {
 					withTrace(t, test.gasLimit(subtest), func(vmconfig vm.Config) error {
 						snaps, statedb, err := test.Run(subtest, vmconfig, true)
-						if _, err := snaps.Journal(statedb.IntermediateRoot(false)); err != nil {
-							return err
+						if snaps != nil && statedb != nil {
+							if _, err := snaps.Journal(statedb.IntermediateRoot(false)); err != nil {
+								return err
+							}
 						}
 						return st.checkFailure(t, err)
 					})
```
