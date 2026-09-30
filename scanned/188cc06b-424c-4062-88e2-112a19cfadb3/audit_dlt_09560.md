# [?] fix feeHistoryCache get index underflow bug

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2024-09-20
Source: https://github.com/Conflux-Chain/conflux-rust/commit/e55c74cda91affa43edd2c6672ee6f8cb3fe3000
Type: security-commit

## Details
fix feeHistoryCache get index underflow bug

## Patch
### crates/client/src/rpc/impls/fee_history_cache.rs
```diff
@@ -124,14 +124,8 @@ impl FeeHistoryCache {
         &self, start_block: u64, end_block: u64,
     ) -> Vec<Option<FeeHistoryEntry>> {
         let inner = self.inner.read();
-        let lower_bound = inner.lower_bound;
         (start_block..=end_block)
-            .map(|block_number| {
-                inner
-                    .entries
-                    .get((block_number - lower_bound) as usize)
-                    .cloned()
-            })
+            .map(|block_number| inner.get(block_number))
             .collect()
     }
 }
@@ -197,7 +191,6 @@ impl FeeHistoryCacheInner {
 
     pub fn is_empty(&self) -> bool { self.entries.is_empty() }
 
-    #[allow(dead_code)]
     pub fn get(&self, height: u64) -> Option<FeeHistoryEntry> {
         if height < self.lower_bound || height > self.upper_bound() {
             return None;
```
