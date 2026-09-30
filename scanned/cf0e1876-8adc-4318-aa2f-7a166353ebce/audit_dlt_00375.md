# [?] [indexer] Fix potential overflow in ending version calculation (#18828)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-23
Source: https://github.com/aptos-labs/aptos-core/commit/1fa8dca6e867a8c01850a5595081f51676a6ac65
Type: security-commit

## Details
[indexer] Fix potential overflow in ending version calculation (#18828)

Use saturating_add instead of unchecked addition when computing
ending_version from starting_version + transactions_count, preventing
overflow when both values are large u64s.

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### ecosystem/indexer-grpc/indexer-grpc-data-service-v2/src/historical_data_service.rs
```diff
@@ -107,7 +107,7 @@ impl HistoricalDataService {
 
                 let ending_version = request
                     .transactions_count
-                    .map(|count| starting_version + count);
+                    .map(|count| starting_version.saturating_add(count));
 
                 scope.spawn(async move {
                     self.start_streaming(
```

### ecosystem/indexer-grpc/indexer-grpc-data-service-v2/src/live_data_service/mod.rs
```diff
@@ -122,7 +122,7 @@ impl<'a> LiveDataService<'a> {
 
                 let ending_version = request
                     .transactions_count
-                    .map(|count| starting_version + count);
+                    .map(|count| starting_version.saturating_add(count));
 
                 scope.spawn(async move {
                     self.start_streaming(
```
