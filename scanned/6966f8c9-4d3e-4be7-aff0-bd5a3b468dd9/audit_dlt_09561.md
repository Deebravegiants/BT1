# [?] Fix fee history cache overflow

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2024-09-19
Source: https://github.com/Conflux-Chain/conflux-rust/commit/e43ab634c99cc2bbc658b1fd37c160d3058c8d3b
Type: security-commit

## Details
Fix fee history cache overflow

## Patch
### crates/client/src/rpc/impls/fee_history_cache.rs
```diff
@@ -162,7 +162,7 @@ impl FeeHistoryCacheInner {
     // if the cached history is outdated, clear the cache
     fn check_and_clear_cache(&mut self, latest_block: u64) {
         if !self.is_empty()
-            && self.upper_bound() <= latest_block - self.max_blocks
+            && self.upper_bound() + self.max_blocks <= latest_block
         {
             self.clear_cache();
         }
```
