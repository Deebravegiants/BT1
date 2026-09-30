# [?] Fix race condition in TestRequestManager_RemoveStream (#4966)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2025-11-18
Source: https://github.com/harmony-one/harmony/commit/4126c2a221b0799025bff7fccd52ff1e98a73c8f
Type: security-commit

## Details
Fix race condition in TestRequestManager_RemoveStream (#4966)

## Patch
### p2p/stream/common/requestmanager/requestmanager_test.go
```diff
@@ -142,6 +142,17 @@ func TestRequestManager_RemoveStream(t *testing.T) {
 		t.Errorf("unexpected error: %v", errors.New("stream removed when doing request"))
 	}
 
+	// Wait for stream removal to be processed asynchronously in the event loop
+	// The removal happens in a separate goroutine, so we need to wait for it
+	maxWait := 10 * time.Second
+	deadline := time.Now().Add(maxWait)
+	for time.Now().Before(deadline) {
+		if ts.rm.streams.Length() == 2 && ts.rm.available.Length() == 2 {
+			break
+		}
+		time.Sleep(100 * time.Millisecond)
+	}
+
 	if l := ts.rm.streams.Length(); l != 2 {
 		t.Errorf("unexpected stream size, expected 2, got %d", l)
 	}
```
