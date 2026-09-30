# [?] Fix checkpoint panic in estimation

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-06-28
Source: https://github.com/Conflux-Chain/conflux-rust/commit/db19ed2d519235c3b1a8a620d82fbe64d59f4f11
Type: security-commit

## Details
Fix checkpoint panic in estimation

## Patch
### core/src/state/mod.rs
```diff
@@ -360,7 +360,6 @@ impl<StateDbStorage: StorageStateTrait> StateOpsTrait
     /// Maintain `total_issued_tokens`. This is only used in the extremely
     /// unlikely case that there are a lot of partial invalid blocks.
     fn subtract_total_issued(&mut self, v: U256) {
-        assert!(self.world_statistics_checkpoints.get_mut().is_empty());
         self.world_statistics.total_issued_tokens -= v;
     }
 
```
