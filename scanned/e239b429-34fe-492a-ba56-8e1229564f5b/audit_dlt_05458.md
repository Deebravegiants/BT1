# [?] backport: dex: hotfix for 2025-01-18 chain halt (#4996)

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2025-01-20
Source: https://github.com/penumbra-zone/penumbra/commit/74960589995bd46e5110f395c6ad9d427199c93a
Type: security-commit

## Details
backport: dex: hotfix for 2025-01-18 chain halt (#4996)

## Describe your changes

This PR backports #4993, which was made against the `release/v0.81.x`
branch, to the `main` branch, so it's included in ongoing development.

Co-authored-by: Henry de Valence <hdevalence@penumbralabs.xyz>

## Patch
### crates/core/component/dex/src/component/action_handler/position/close.rs
```diff
@@ -2,9 +2,8 @@ use anyhow::Result;
 use async_trait::async_trait;
 use cnidarium::StateWrite;
 use cnidarium_component::ActionHandler;
-use penumbra_proto::{DomainType as _, StateWriteProto as _};
 
-use crate::{component::PositionManager, event, lp::action::PositionClose};
+use crate::{component::PositionManager, lp::action::PositionClose};
 
 #[async_trait]
 /// Debits an opened position NFT and credits a closed position NFT.
@@ -22,15 +21,7 @@ impl ActionHandler for PositionClose {
         // lose the ability to do block-scoped JIT liquidity, where a single
         // transaction opens and closes a position, keeping liquidity live only
         // during that block's batch swap execution.
-        state.queue_close_position(self.position_id);
-
-        // queue position close you will...
-        state.record_proto(
-            event::EventQueuePositionClose {
-                position_id: self.position_id,
-            }
-            .to_proto(),
-        );
+        state.queue_close_position(self.position_id).await?;
 
         Ok(())
     }
```

### crates/core/component/dex/src/component/position_manager.rs
```diff
@@ -211,10 +211,37 @@ pub trait PositionManager: StateWrite + PositionRead {
     }
 
     /// Queues a position to be closed at the end of the block, after batch execution.
-    fn queue_close_position(&mut self, id: position::Id) {
-        let mut to_close = self.pending_position_closures();
-        to_close.push_back(id);
-        self.object_put(state_key::pending_position_closures(), to_close);
+    async fn queue_close_position(&mut self, id: position::Id) -> Result<()> {
+        tracing::debug!(
+            ?id,
+            "checking current position state before queueing for closure"
+        );
+        let current_state = self
+            .position_by_id(&id)
+            .await
+            .expect("fetching position should not fail")
+            .ok_or_else(|| anyhow::anyhow!("could not find position {} to close", id))?
+            .tap(|lp| tracing::trace!(prev_state = ?lp, "retrieved previous lp state"));
+
+        if current_state.state == position::State::Opened {
+            tracing::debug!(
+                ?current_state.state,
+                "queueing opened position for closure"
+            );
+            let mut to_close = self.pending_position_closures();
+            to_close.push_back(id);
+            self.object_put(state_key::pending_position_closures(), to_close);
+
+            // queue position close you will...
+            self.record_proto(event::EventQueuePositionClose { position_id: id }.to_proto());
+        } else {
+            tracing::debug!(
+                ?current_state.state,
+                "skipping queueing for closure of non-opened position"
+            );
+        }
+
+        Ok(())
     }
 
     /// Close all positions that have been queued for closure.
```
