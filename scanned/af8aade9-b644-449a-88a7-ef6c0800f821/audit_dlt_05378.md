# [?] Fix/issue 769 overflow protection (#780)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2025-12-30
Source: https://github.com/kaspanet/rusty-kaspa/commit/cea06453b0172ed7c02d19962836b5ebeb1dddec
Type: security-commit

## Details
Fix/issue 769 overflow protection (#780)

* fix: prevent integer overflow in estimate_block_count() (issue #769)

- Replace subtraction with saturating_sub() to prevent panic when
  virtual_score < retention_period_root_score during IBD UTXO import
- Add test to verify overflow protection works correctly
- Fixes: https://github.com/kaspanet/rusty-kaspa/issues/769

* Coder and freshair req

* test removed

* Removed

   daa_score: pruning_point_header.daa_score,
            bits: pruning_point_header.bits,
            past_median_time: pruning_point_header.timestamp,
            mergeset_non_daa: BlockHashSet::from_iter(std::iter::once(pruning_point)),

## Patch
### consensus/src/consensus/mod.rs
```diff
@@ -749,15 +749,16 @@ impl ConsensusApi for Consensus {
         // PRUNE SAFETY: retention root is always a current or past pruning point which its header is kept permanently
         let retention_period_root_score = self.headers_store.get_daa_score(self.get_retention_period_root()).unwrap();
         let virtual_score = self.get_virtual_daa_score();
+        // TODO(relaxed): change virtual's 0 daa initialization, and revert to normal subtraction
         let header_count = self
             .headers_store
             .get_daa_score(self.get_headers_selected_tip())
             .optional()
             .unwrap()
             .unwrap_or(virtual_score)
             .max(virtual_score)
-            - retention_period_root_score;
-        let block_count = virtual_score - retention_period_root_score;
+            .saturating_sub(retention_period_root_score);
+        let block_count = virtual_score.saturating_sub(retention_period_root_score);
         BlockCount { header_count, block_count }
     }
 
```
