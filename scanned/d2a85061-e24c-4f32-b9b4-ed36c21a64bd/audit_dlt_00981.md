# [?] fix: resolve TestAddMultipleGCLive race condition (#10916)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2025-08-18
Source: https://github.com/ipfs/kubo/commit/a81cc2928247829e12c2a76d8b7041232a9fe29c
Type: security-commit

## Details
fix: resolve TestAddMultipleGCLive race condition (#10916)

test was expecting immediate GC lock acquisition after pipe close,
but timing wasn't guaranteed. replaced blocking wait with 5-second
timeout to handle timing variations while still detecting deadlocks.

## Patch
### core/coreunix/add_test.go
```diff
@@ -93,8 +93,15 @@ func TestAddMultipleGCLive(t *testing.T) {
 	// finish write and unblock gc
 	pipew1.Close()
 
-	// Should have gotten the lock at this point
-	<-gc1started
+	// Wait for GC to acquire the lock
+	// The adder needs to finish processing file 'a' and call maybePauseForGC
+	// when starting file 'b' before GC can proceed
+	select {
+	case <-gc1started:
+		// GC got the lock as expected
+	case <-time.After(5 * time.Second):
+		t.Fatal("timeout waiting for GC to start - possible deadlock")
+	}
 
 	removedHashes := make(map[string]struct{})
 	for r := range gc1out {
@@ -123,7 +130,15 @@ func TestAddMultipleGCLive(t *testing.T) {
 
 	pipew2.Close()
 
-	<-gc2started
+	// Wait for second GC to acquire the lock
+	// The adder needs to finish processing file 'b' and call maybePauseForGC
+	// when starting file 'c' before GC can proceed
+	select {
+	case <-gc2started:
+		// GC got the lock as expected
+	case <-time.After(5 * time.Second):
+		t.Fatal("timeout waiting for second GC to start - possible deadlock")
+	}
 
 	for r := range gc2out {
 		if r.Error != nil {
```
