# [?] indexer-alt: avoid panic in kv_protocol_configs (#21819)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-04-13
Source: https://github.com/MystenLabs/sui/commit/7d89f274f838e40c05c6f29a943231748f6b3258
Type: security-commit

## Details
indexer-alt: avoid panic in kv_protocol_configs (#21819)

## Description

Use `ProtocolConfig::get_for_version_if_supported` instead of
`ProtocolConfig::get_for_version`, so that if the version is not
supported, we don't panic and have a chance to propagate an error.

If this pipeline is running in the same process as other pipelines, this
will allow those other pipelines to continue making progress.

## Test plan

New unit test for this behaviour.

```
sui$ cargo nextest run -p sui-indexer-alt
```

---

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol: 
- [ ] Nodes (Validators and Full nodes): 
- [ ] gRPC:
- [ ] JSON-RPC: 
- [ ] GraphQL: 
- [ ] CLI: 
- [ ] Rust SDK:

## Patch
### crates/sui-indexer-alt/src/handlers/kv_feature_flags.rs
```diff
@@ -3,7 +3,7 @@
 
 use std::sync::Arc;
 
-use anyhow::{Context, Result};
+use anyhow::{bail, Context, Result};
 use diesel_async::RunQueryDsl;
 use sui_indexer_alt_framework::{
     db::{Connection, Db},
@@ -34,10 +34,15 @@ impl Processor for KvFeatureFlags {
             return Ok(vec![]);
         };
 
-        let protocol_config = ProtocolConfig::get_for_version(
+        let Some(protocol_config) = ProtocolConfig::get_for_version_if_supported(
             protocol_version,
             self.0.chain().context("Failed to identify chain")?,
-        );
+        ) else {
+            bail!(
+                "Protocol version {} is not supported",
+                protocol_version.as_u64()
+            );
+        };
 
         let protocol_version = protocol_version.as_u64() as i64;
         Ok(protocol_config
@@ -67,3 +72,50 @@ impl Handler for KvFeatureFlags {
             .await?)
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use sui_indexer_alt_framework::types::test_checkpoint_data_builder::TestCheckpointDataBuilder;
+    use sui_protocol_config::ProtocolVersion;
+
+    use super::*;
+
+    #[tokio::test]
+    async fn test_feature_flag_processing() {
+        let mut builder = TestCheckpointDataBuilder::new(0);
+        let genesis = Arc::new(builder.build_checkpoint());
+        let checkpoint =
+            Arc::new(builder.advance_epoch_and_protocol_upgrade(false, ProtocolVersion::MIN));
+
+        let stored_genesis = StoredGenesis {
+            genesis_digest: genesis.checkpoint_summary.digest().inner().to_vec(),
+            initial_protocol_version: ProtocolVersion::MIN.as_u64() as i64,
+        };
+
+        let feature_flags = KvFeatureFlags(stored_genesis).process(&checkpoint).unwrap();
+
+        assert!(!feature_flags.is_empty());
+        for flag in feature_flags {
+            assert_eq!(flag.protocol_version, ProtocolVersion::MIN.as_u64() as i64);
+        }
+    }
+
+    /// When the protocol version is too high, the pipeline should fail to process the checkpoint,
+    /// but not panic.
+    #[tokio::test]
+    async fn test_protocol_version_too_high() {
+        let mut builder = TestCheckpointDataBuilder::new(0);
+        let genesis = Arc::new(builder.build_checkpoint());
+        let checkpoint =
+            Arc::new(builder.advance_epoch_and_protocol_upgrade(false, ProtocolVersion::MAX + 1));
+
+        let stored_genesis = StoredGenesis {
+            genesis_digest: genesis.checkpoint_summary.digest().inner().to_vec(),
+            initial_protocol_version: ProtocolVersion::MIN.as_u64() as i64,
+        };
+
+        KvFeatureFlags(stored_genesis)
+            .process(&checkpoint)
+            .unwrap_err();
+    }
+}
```

### crates/sui-indexer-alt/src/handlers/kv_protocol_configs.rs
```diff
@@ -3,7 +3,7 @@
 
 use std::sync::Arc;
 
-use anyhow::{Context, Result};
+use anyhow::{bail, Context, Result};
 use diesel_async::RunQueryDsl;
 use sui_indexer_alt_framework::{
     db::{Connection, Db},
@@ -34,10 +34,15 @@ impl Processor for KvProtocolConfigs {
             return Ok(vec![]);
         };
 
-        let protocol_config = ProtocolConfig::get_for_version(
+        let Some(protocol_config) = ProtocolConfig::get_for_version_if_supported(
             protocol_version,
             self.0.chain().context("Failed to identify chain")?,
-        );
+        ) else {
+            bail!(
+                "Protocol version {} is not supported",
+                protocol_version.as_u64()
+            );
+        };
 
         let protocol_version = protocol_version.as_u64() as i64;
         Ok(protocol_config
@@ -67,3 +72,55 @@ impl Handler for KvProtocolConfigs {
             .await?)
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use sui_indexer_alt_framework::types::test_checkpoint_data_builder::TestCheckpointDataBuilder;
+    use sui_protocol_config::ProtocolVersion;
+
+    use super::*;
+
+    #[tokio::test]
+    async fn test_protocol_version_processing() {
+        let mut builder = TestCheckpointDataBuilder::new(0);
+        let genesis = Arc::new(builder.build_checkpoint());
+        let checkpoint =
+            Arc::new(builder.advance_epoch_and_protocol_upgrade(false, ProtocolVersion::MIN));
+
+        let stored_genesis = StoredGenesis {
+            genesis_digest: genesis.checkpoint_summary.digest().inner().to_vec(),
+            initial_protocol_version: ProtocolVersion::MIN.as_u64() as i64,
+        };
+
+        let protocol_configs = KvProtocolConfigs(stored_genesis)
+            .process(&checkpoint)
+            .unwrap();
+
+        assert!(!protocol_configs.is_empty());
+        for config in protocol_configs {
+            assert_eq!(
+                config.protocol_version,
+                ProtocolVersion::MIN.as_u64() as i64
+            );
+        }
+    }
+
+    /// When the protocol version is too high, the pipeline should fail to process the checkpoint,
+    /// but not panic.
+    #[tokio::test]
+    async fn test_protocol_version_too_high() {
+        let mut builder = TestCheckpointDataBuilder::new(0);
+        let genesis = Arc::new(builder.build_checkpoint());
+        let checkpoint =
+            Arc::new(builder.advance_epoch_and_protocol_upgrade(false, ProtocolVersion::MAX + 1));
+
+        let stored_genesis = StoredGenesis {
+            genesis_digest: genesis.checkpoint_summary.digest().inner().to_vec(),
+            initial_protocol_version: ProtocolVersion::MIN.as_u64() as i64,
+        };
+
+        KvProtocolConfigs(stored_genesis)
+            .process(&checkpoint)
+            .unwrap_err();
+    }
+}
```

### crates/sui-types/src/test_checkpoint_data_builder.rs
```diff
@@ -7,7 +7,7 @@ use move_core_types::{
     ident_str,
     language_storage::{StructTag, TypeTag},
 };
-use sui_protocol_config::ProtocolConfig;
+use sui_protocol_config::{ProtocolConfig, ProtocolVersion};
 use tap::Pipe;
 
 use crate::{
@@ -594,15 +594,25 @@ impl TestCheckpointDataBuilder {
         }
     }
 
+    /// Like `advance_epoch_and_protocol_upgrade`, but default the protocol version to the maximum.
+    pub fn advance_epoch(&mut self, safe_mode: bool) -> CheckpointData {
+        self.advance_epoch_and_protocol_upgrade(safe_mode, ProtocolVersion::MAX)
+    }
+
     /// Creates a transaction that advances the epoch, adds it to the checkpoint, and then builds
     /// the checkpoint. This increments the stored checkpoint sequence number and epoch. If
     /// `safe_mode` is true, the epoch end transaction will not include the `SystemEpochInfoEvent`.
-    pub fn advance_epoch(&mut self, safe_mode: bool) -> CheckpointData {
+    /// The `protocol_version` is used to set the protocol that we are going to follow in the
+    /// subsequent epoch.
+    pub fn advance_epoch_and_protocol_upgrade(
+        &mut self,
+        safe_mode: bool,
+        protocol_version: ProtocolVersion,
+    ) -> CheckpointData {
         let (committee, _) = Committee::new_simple_test_committee();
-        let protocol_config = ProtocolConfig::get_for_max_version_UNSAFE();
         let tx_kind = EndOfEpochTransactionKind::new_change_epoch(
             self.checkpoint_builder.epoch + 1,
-            protocol_config.version,
+            protocol_version,
             Default::default(),
             Default::default(),
             Default::default(),
@@ -626,7 +636,7 @@ impl TestCheckpointDataBuilder {
         let events = if !safe_mode {
             let system_epoch_info_event = SystemEpochInfoEvent {
                 epoch: self.checkpoint_builder.epoch,
-                protocol_version: protocol_config.version.as_u64(),
+                protocol_version: protocol_version.as_u64(),
                 ..Default::default()
             };
             let struct_tag = StructTag {
@@ -664,7 +674,7 @@ impl TestCheckpointDataBuilder {
         let mut checkpoint = self.build_checkpoint();
         let end_of_epoch_data = EndOfEpochData {
             next_epoch_committee: committee.voting_rights.clone(),
-            next_epoch_protocol_version: protocol_config.version,
+            next_epoch_protocol_version: protocol_version,
             epoch_commitments: vec![],
         };
         checkpoint.checkpoint_summary.end_of_epoch_data = Some(end_of_epoch_data);
```
