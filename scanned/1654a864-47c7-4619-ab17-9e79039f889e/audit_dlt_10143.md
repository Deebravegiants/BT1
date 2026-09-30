# [?] fix: subtract overflow when try to get chain root for genesis block

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-10-28
Source: https://github.com/nervosnetwork/ckb/commit/3f043c1190909fb822d4f7cad55ecb47b6f1b9b9
Type: security-commit

## Details
fix: subtract overflow when try to get chain root for genesis block

## Patch
### util/light-client-protocol-server/src/lib.rs
```diff
@@ -122,7 +122,9 @@ impl LightClientProtocol {
         let tip_block = active_chain
             .get_block(&tip_hash)
             .expect("checked: tip block should be existed");
-        let parent_chain_root = {
+        let parent_chain_root = if tip_block.is_genesis() {
+            Default::default()
+        } else {
             let snapshot = self.shared.shared().snapshot();
             let mmr = snapshot.chain_root_mmr(tip_block.number() - 1);
             match mmr.get_root() {
```

### util/types/src/utilities/merkle_mountain_range.rs
```diff
@@ -216,7 +216,8 @@ impl VerifiableHeader {
 
     /// Checks if the current verifiable header is valid.
     pub fn is_valid(&self, mmr_activated_epoch: EpochNumber) -> bool {
-        let has_chain_root = self.header().epoch().number() >= mmr_activated_epoch;
+        let has_chain_root =
+            !self.header().is_genesis() && self.header().epoch().number() >= mmr_activated_epoch;
         if has_chain_root {
             let is_extension_beginning_with_chain_root_hash = self
                 .extension()
```
