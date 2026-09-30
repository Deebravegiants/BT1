# [?] Avoid `panic` on failure of flaky unit test.

## Summary
Severity: Unknown
Chain: Quorum
Component: Consensys-inc-archive/quorum
Published: 2021-07-29
Source: https://github.com/Consensys-inc-archive/quorum/commit/0ae73a1b915ad2b8e838a22a6dd584361b8b255b
Type: security-commit

## Details
Avoid `panic` on failure of flaky unit test.

## Patch
### consensus/istanbul/ibft/core/core_test.go
```diff
@@ -68,7 +68,7 @@ func TestNewRequest(t *testing.T) {
 
 	for _, backend := range sys.backends {
 		if len(backend.committedMsgs) != 2 {
-			t.Errorf("the number of executed requests mismatch: have %v, want 2", len(backend.committedMsgs))
+			t.Fatalf("the number of executed requests mismatch: have %v, want 2", len(backend.committedMsgs))
 		}
 		if !reflect.DeepEqual(request1.Number(), backend.committedMsgs[0].commitProposal.Number()) {
 			t.Errorf("the number of requests mismatch: have %v, want %v", request1.Number(), backend.committedMsgs[0].commitProposal.Number())
```
