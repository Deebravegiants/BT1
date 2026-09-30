# [?] fix(node/test): fix sequencer block building race condition (op-rs/kona#2783)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-08-27
Source: https://github.com/ethereum-optimism/optimism/commit/d5d8c5a454bb2ae68e89abe1e6b2d858d006028b
Type: security-commit

## Details
fix(node/test): fix sequencer block building race condition (op-rs/kona#2783)

## Description

We have a race condition in our sequencer block building process:
- When it starts building a block, the sequencer (through the CL node)
sends a `forkchoice_updated` RPC query to the EL
- The L2 EL starts building an empty payload as soon as we query the RPC
endpoint `forkchoice_updated`
- Right after, the CL node sends `get_payload` which seals a payload for
publication

We may have a race condition where the txs from the EL mempool never get
included inside the EL payloads because the blocks get sealed too fast.

## Patch
### .github/workflows/node_e2e_sysgo_tests.yaml
```diff
@@ -45,8 +45,5 @@ jobs:
       - name: restart tests for node with sysgo orchestrator
         run: just test-e2e-sysgo node/restart
 
-      - name: transfers tests for node with sysgo orchestrator
-        run: just test-e2e-sysgo node/transfers
-
 
 
```

### crates/node/engine/src/task_queue/tasks/build/error.rs
```diff
@@ -81,6 +81,9 @@ pub enum BuildTaskError {
     /// Error sending the built payload envelope.
     #[error(transparent)]
     MpscSend(#[from] Box<mpsc::error::SendError<OpExecutionPayloadEnvelope>>),
+    /// The clock went backwards.
+    #[error("The clock went backwards")]
+    ClockWentBackwards,
 }
 
 impl EngineTaskError for BuildTaskError {
@@ -112,6 +115,7 @@ impl EngineTaskError for BuildTaskError {
             Self::DepositOnlyPayloadFailed => EngineTaskErrorSeverity::Critical,
             Self::FromBlock(_) => EngineTaskErrorSeverity::Critical,
             Self::MpscSend(_) => EngineTaskErrorSeverity::Critical,
+            Self::ClockWentBackwards => EngineTaskErrorSeverity::Critical,
         }
     }
 }
```

### crates/node/engine/src/task_queue/tasks/build/task.rs
```diff
@@ -13,8 +13,11 @@ use kona_genesis::RollupConfig;
 use kona_protocol::{L2BlockInfo, OpAttributesWithParent};
 use op_alloy_provider::ext::engine::OpEngineApi;
 use op_alloy_rpc_types_engine::{OpExecutionPayload, OpExecutionPayloadEnvelope};
-use std::{sync::Arc, time::Instant};
-use tokio::sync::mpsc;
+use std::{
+    sync::Arc,
+    time::{Duration, Instant, SystemTime},
+};
+use tokio::{sync::mpsc, time::sleep};
 
 /// Task for building new blocks with automatic forkchoice synchronization.
 ///
@@ -263,6 +266,26 @@ impl EngineTaskExt for BuildTask {
 
         let fcu_duration = fcu_start_time.elapsed();
 
+        // Compute the time of the next block.
+        let next_block = Duration::from_secs(
+            self.attributes.parent().block_info.timestamp.saturating_add(self.cfg.block_time),
+        );
+
+        // Compute the time left to seal the next block.
+        let now = SystemTime::now()
+            .duration_since(SystemTime::UNIX_EPOCH)
+            .map_err(|_| BuildTaskError::ClockWentBackwards)?;
+
+        // Add a buffer to the time left to seal the next block.
+        const SEALING_BUFFER: Duration = Duration::from_millis(50);
+
+        let time_left_to_seal = next_block.saturating_sub(now).saturating_sub(SEALING_BUFFER);
+
+        // Wait for the time left to seal the next block.
+        if !time_left_to_seal.is_zero() {
+            sleep(time_left_to_seal).await;
+        }
+
         // Fetch the payload just inserted from the EL and import it into the engine.
         let block_import_start_time = Instant::now();
         let new_payload = self
```

### crates/node/service/src/actors/sequencer/actor.rs
```diff
@@ -288,15 +288,19 @@ impl<AB: AttributesBuilder> SequencerActorState<AB> {
                 }
             };
 
+        attributes.no_tx_pool = Some(false);
+
         if in_recovery_mode {
             attributes.no_tx_pool = Some(true);
         }
 
         // If the next L2 block is beyond the sequencer drift threshold, we must produce an empty
         // block.
-        attributes.no_tx_pool = (attributes.payload_attributes.timestamp >
-            l1_origin.timestamp + self.cfg.max_sequencer_drift(l1_origin.timestamp))
-        .then_some(true);
+        if attributes.payload_attributes.timestamp >
+            l1_origin.timestamp + self.cfg.max_sequencer_drift(l1_origin.timestamp)
+        {
+            attributes.no_tx_pool = Some(true);
+        }
 
         // Do not include transactions in the first Ecotone block.
         if self.cfg.is_first_ecotone_block(attributes.payload_attributes.timestamp) {
```

### tests/node/common/tx_inclusion_test.go
```diff
@@ -1,4 +1,4 @@
-package node_transfers
+package node
 
 import (
 	"testing"
```

### tests/node/transfers/init_test.go
```diff
@@ -1,13 +0,0 @@
-package node_transfers
-
-import (
-	"testing"
-
-	"github.com/ethereum-optimism/optimism/op-devstack/presets"
-	node_utils "github.com/op-rs/kona/node/utils"
-)
-
-// TestMain creates the test-setups against the shared backend
-func TestMain(m *testing.M) {
-	presets.DoMain(m, node_utils.WithMixedOpKona(0, 1, 0, 2))
-}
```
