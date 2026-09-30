# [?] fix(prune): avoid panic in tx lookup (#21275)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-01-21
Source: https://github.com/paradigmxyz/reth/commit/72e1467ba3a6ea2396c49902793e7de3845faf41
Type: security-commit

## Details
fix(prune): avoid panic in tx lookup (#21275)

## Patch
### crates/prune/prune/src/segments/user/transaction_lookup.rs
```diff
@@ -84,7 +84,14 @@ where
         .into_inner();
         let tx_range = start..=
             Some(end)
-                .min(input.limiter.deleted_entries_limit_left().map(|left| start + left as u64 - 1))
+                .min(
+                    input
+                        .limiter
+                        .deleted_entries_limit_left()
+                        // Use saturating addition here to avoid panicking on
+                        // `deleted_entries_limit == usize::MAX`
+                        .map(|left| start.saturating_add(left as u64) - 1),
+                )
                 .unwrap();
         let tx_range_end = *tx_range.end();
 
```
