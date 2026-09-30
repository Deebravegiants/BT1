# [?] fix data race in LocalFileStorageService pruning goroutine (#3659)

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-09-22
Source: https://github.com/OffchainLabs/nitro/commit/038a72e1d7cdaff7be6176af509734a792b2bec0
Type: security-commit

## Details
fix data race in LocalFileStorageService pruning goroutine (#3659)

## Patch
### daprovider/das/local_file_storage_service.go
```diff
@@ -94,9 +94,9 @@ func (s *LocalFileStorageService) start(ctx context.Context) error {
 	}
 	if s.config.EnableExpiry && !s.enableLegacyLayout {
 		err = s.stopWaiter.CallIterativelySafe(func(ctx context.Context) time.Duration {
-			err = s.layout.prune(time.Now())
-			if err != nil {
-				log.Error("error pruning expired batches", "error", err)
+			pruneErr := s.layout.prune(time.Now())
+			if pruneErr != nil {
+				log.Error("error pruning expired batches", "error", pruneErr)
 			}
 			return time.Minute * 5
 		})
```
