# [?] fix(bench): fix deadlock in test data generation (#18321)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2025-09-08
Source: https://github.com/paradigmxyz/reth/commit/1a4b5eca3c56e70eb41d0e0d03bb098a106c5507
Type: security-commit

## Details
fix(bench): fix deadlock in test data generation (#18321)

## Patch
### crates/stages/stages/benches/setup/mod.rs
```diff
@@ -161,8 +161,9 @@ pub(crate) fn txs_testdata(num_blocks: u64) -> TestStageDB {
 
         let offset = transitions.len() as u64;
 
-        let provider_rw = db.factory.provider_rw().unwrap();
         db.insert_changesets(transitions, None).unwrap();
+
+        let provider_rw = db.factory.provider_rw().unwrap();
         provider_rw.write_trie_updates(&updates).unwrap();
         provider_rw.commit().unwrap();
 
```
