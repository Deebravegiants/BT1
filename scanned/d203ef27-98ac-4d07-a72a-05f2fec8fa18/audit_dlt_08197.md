# [?] alpenglow: fix race condition in setting genesis info for migration (#11727)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-04-02
Source: https://github.com/anza-xyz/agave/commit/f0ceb8a852feb4191961d6d597915cfc97615ec4
Type: security-commit

## Details
alpenglow: fix race condition in setting genesis info for migration (#11727)

## Patch
### votor-messages/src/migration.rs
```diff
@@ -475,22 +475,29 @@ impl MigrationStatus {
     /// received a genesis certificate and it matches.
     pub fn set_genesis_block(&self, discovered_genesis_block @ (slot, _): Block) {
         let mut phase = self.phase.write().unwrap();
+        if phase.is_pre_feature_activation() {
+            unreachable!(
+                "{}: Programmer error, attempting to set genesis cert while pre migration",
+                self.my_pubkey()
+            );
+        }
+
         let MigrationPhase::Migration {
             migration_slot,
             genesis_block,
             genesis_cert,
         } = &mut *phase
         else {
-            unreachable!(
-                "{}: Programmer error, attempting to set genesis block while not in migration",
-                self.my_pubkey()
-            );
+            // We've already transitioned to `ReadyToEnable` or further, no action needed
+            return;
         };
-        assert!(
-            genesis_block.is_none(),
-            "Attempting to overwrite genesis block to {discovered_genesis_block:?}. Programmer \
-             error"
-        );
+
+        if let Some(prev_genesis_block) = genesis_block {
+            assert_eq!(
+                *prev_genesis_block, discovered_genesis_block,
+                "We have discovered two different alpenglow genesis blocks. Something is wrong",
+            );
+        }
 
         assert!(
             slot < *migration_slot,
@@ -534,17 +541,23 @@ impl MigrationStatus {
     /// Transitions to `ReadyToEnable` if we have already received a genesis block and it matches.
     pub fn set_genesis_certificate(&self, cert: Arc<Certificate>) {
         let mut phase = self.phase.write().unwrap();
+        if phase.is_pre_feature_activation() {
+            unreachable!(
+                "{}: Programmer error, attempting to set genesis cert while pre migration",
+                self.my_pubkey()
+            );
+        }
+
         let MigrationPhase::Migration {
             migration_slot,
             genesis_block,
             genesis_cert,
         } = &mut *phase
         else {
-            unreachable!(
-                "{}: Programmer error, attempting to set genesis cert while not in migration",
-                self.my_pubkey()
-            );
+            // We've already transitioned to `ReadyToEnable` or further, no action needed
+            return;
         };
+
         let CertificateType::Genesis(slot, block_id) = cert.cert_type else {
             unreachable!("Programmer error adding invalid genesis certificate");
         };
```
