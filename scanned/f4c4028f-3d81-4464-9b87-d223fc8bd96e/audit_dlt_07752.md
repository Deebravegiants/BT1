# [?] fix: Prevent potential underflow in static file header healing (#18628)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-09-23
Source: https://github.com/paradigmxyz/reth/commit/8eaadf52d80ec490fc996659d2b4d7775a929ae0
Type: security-commit

## Details
fix: Prevent potential underflow in static file header healing (#18628)

## Patch
### crates/storage/provider/src/providers/static_file/writer.rs
```diff
@@ -201,7 +201,8 @@ impl<N: NodePrimitives> StaticFileProviderRW<N> {
         } else {
             self.user_header().tx_len().unwrap_or_default()
         };
-        let pruned_rows = expected_rows - self.writer.rows() as u64;
+        let actual_rows = self.writer.rows() as u64;
+        let pruned_rows = expected_rows.saturating_sub(actual_rows);
         if pruned_rows > 0 {
             self.user_header_mut().prune(pruned_rows);
         }
```
