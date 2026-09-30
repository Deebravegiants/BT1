# [?] Fix a panic if recovery takes too long. (#1087)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-03-19
Source: https://github.com/Conflux-Chain/conflux-rust/commit/f5684f45d040b8e7840aed63dba4a5eea04c776d
Type: security-commit

## Details
Fix a panic if recovery takes too long. (#1087)

* Fix a panic if recovery takes too long.

## Patch
### core/src/sync/synchronization_protocol_handler.rs
```diff
@@ -1431,6 +1431,12 @@ impl SynchronizationProtocolHandler {
     pub fn expire_block_gc(
         &self, io: &dyn NetworkContext, timeout: u64,
     ) -> Result<(), Error> {
+        if self.in_recover_from_db_phase() {
+            // In recover_from_db phase, this will be done at the end of
+            // recovery, and if we allow `resolve_outside_dependencies` here,
+            // it will cause inconsistency.
+            return Ok(());
+        }
         let need_to_relay = self.graph.resolve_outside_dependencies(
             false, /* recover_from_db */
             self.insert_header_to_consensus(),
```
