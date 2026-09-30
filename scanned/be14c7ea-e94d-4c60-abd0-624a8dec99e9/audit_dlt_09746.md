# [?] fix(client): crash possibility

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-03-19
Source: https://github.com/fedimint/fedimint/commit/c7cd1c03cc16d61645a3986b133f351335eafc5c
Type: security-commit

## Details
fix(client): crash possibility

Just because someone requested huge limit, doesn't mean there are that
many matching entries, and we want to allocate whole system memory
in anticipation.

## Patch
### fedimint-client/src/oplog.rs
```diff
@@ -117,7 +117,7 @@ impl OperationLog {
         };
 
         let mut dbtx = self.db.begin_transaction_nc().await;
-        let mut operation_log_keys = Vec::with_capacity(limit);
+        let mut operation_log_keys = Vec::with_capacity(32);
 
         // Find all the operation log keys in the requested window. Since we decided to
         // not introduce a find_by_range_rev function we have to jump through some
```
