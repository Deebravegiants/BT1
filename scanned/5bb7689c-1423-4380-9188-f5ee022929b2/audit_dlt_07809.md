# [?] Fix race condition in TestService_Initialized (#8597)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2021-03-11
Source: https://github.com/OffchainLabs/prysm/commit/fa2084330bdb128380ef3eee65aca56fb52f9c55
Type: security-commit

## Details
Fix race condition in TestService_Initialized (#8597)

## Patch
### beacon-chain/sync/initial-sync/service_test.go
```diff
@@ -443,7 +443,9 @@ func TestService_Resync(t *testing.T) {
 }
 
 func TestService_Initialized(t *testing.T) {
-	s := NewService(context.Background(), &Config{})
+	s := NewService(context.Background(), &Config{
+		StateNotifier: &mock.MockStateNotifier{},
+	})
 	s.chainStarted.Set()
 	assert.Equal(t, true, s.Initialized())
 	s.chainStarted.UnSet()
```
