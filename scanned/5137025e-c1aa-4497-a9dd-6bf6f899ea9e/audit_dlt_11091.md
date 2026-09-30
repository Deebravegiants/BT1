# [?] op-batcher: fix a deadlock (#13014)

## Summary
Severity: Unknown
Chain: Boba
Component: bobanetwork/boba
Published: 2024-11-22
Source: https://github.com/bobanetwork/boba/commit/5aa14b374ec906d32a824b4c7acbcb06366a88d0
Type: security-commit

## Details
op-batcher: fix a deadlock (#13014)

* fix a deadlock

* add comment

## Patch
### op-batcher/batcher/driver.go
```diff
@@ -557,8 +557,11 @@ func (l *BatchSubmitter) throttlingLoop(ctx context.Context) {
 			// We'd probably hit this error right after startup, so a short shutdown duration should suffice.
 			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
 			defer cancel()
-			// Always returns nil. An error is only returned to expose this function as an RPC.
-			_ = l.StopBatchSubmitting(ctx)
+			// Call StopBatchSubmitting in another goroutine to avoid deadlock.
+			go func() {
+				// Always returns nil. An error is only returned to expose this function as an RPC.
+				_ = l.StopBatchSubmitting(ctx)
+			}()
 			return
 		} else if err != nil {
 			l.Log.Error("SetMaxDASize rpc failed, retrying.", "err", err)
```
