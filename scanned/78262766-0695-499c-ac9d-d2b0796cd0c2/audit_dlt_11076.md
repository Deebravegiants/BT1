# [?] Fix batcher panic

## Summary
Severity: Unknown
Chain: Kroma
Component: kroma-network/kroma
Published: 2023-10-31
Source: https://github.com/kroma-network/kroma/commit/fae4e077159712b29a6f93c85ad5e001037a6931
Type: security-commit

## Details
Fix batcher panic

## Patch
### op-batcher/batcher/service.go
```diff
@@ -290,8 +290,10 @@ func (bs *BatcherService) Stop(ctx context.Context) error {
 	bs.Log.Info("Stopping batcher")
 
 	var result error
-	if err := bs.driver.StopBatchSubmittingIfRunning(ctx); err != nil {
-		result = errors.Join(result, fmt.Errorf("failed to stop batch submitting: %w", err))
+	if bs.driver != nil {
+		if err := bs.driver.StopBatchSubmittingIfRunning(ctx); err != nil {
+			result = errors.Join(result, fmt.Errorf("failed to stop batch submitting: %w", err))
+		}
 	}
 
 	if bs.rpcServer != nil {
@@ -328,7 +330,7 @@ func (bs *BatcherService) Stop(ctx context.Context) error {
 
 	if result == nil {
 		bs.stopped.Store(true)
-		bs.driver.Log.Info("Batch Submitter stopped")
+		bs.Log.Info("Batch Submitter stopped")
 	}
 	return result
 }
```
