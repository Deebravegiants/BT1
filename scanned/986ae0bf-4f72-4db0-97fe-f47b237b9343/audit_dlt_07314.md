# [?] fix(ICP_Rosetta): Avoid panicking when trying to increment metrics (#7417)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-10-24
Source: https://github.com/dfinity/ic/commit/59e3c12f741e74143c50d1f5a259dd8067dc1721
Type: security-commit

## Details
fix(ICP_Rosetta): Avoid panicking when trying to increment metrics (#7417)

In case of an error fetching blocks, do not call `unwrap()` on the
result for incrementing the metrics, since this will cause a panic.

## Patch
### rs/rosetta-api/icp/ledger_canister_blocks_synchronizer/src/ledger_blocks_sync.rs
```diff
@@ -374,8 +374,10 @@ impl<B: BlocksAccess> LedgerBlocksSynchronizer<B> {
                     .await
                     .map_err(Error::InternalError);
                 if batch.is_ok() || retry == MAX_RETRY {
-                    self.rosetta_metrics
-                        .add_blocks_fetched(batch.as_ref().unwrap().len() as u64);
+                    if let Ok(encoded_blocks) = &batch {
+                        self.rosetta_metrics
+                            .add_blocks_fetched(encoded_blocks.len() as u64);
+                    }
                     break batch;
                 }
                 self.rosetta_metrics.inc_fetch_retries();
```
