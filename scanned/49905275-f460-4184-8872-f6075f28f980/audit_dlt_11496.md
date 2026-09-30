# [?] fix race condition

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2025-03-12
Source: https://github.com/pyth-network/pyth-crosschain/commit/73376d4ac81e1430e53318bf08e636c5599915cb
Type: security-commit

## Details
fix race condition

## Patch
### apps/hermes/server/src/state/aggregate.rs
```diff
@@ -348,7 +348,23 @@ where
         tracing::info!(len = message_states.len(), "Storing Message States.");
         self.store_message_states(message_states).await?;
 
-        // Update the aggregate state
+        // First, get the data we need without holding the lock
+        let message_state_keys_clone = message_state_keys.clone();
+        let should_prune = {
+            let aggregate_state = self.into().data.read().await;
+            match aggregate_state.latest_completed_slot {
+                None => false,
+                Some(latest) if slot > latest => true,
+                _ => false,
+            }
+        };
+
+        // Do the pruning outside the critical section if needed
+        if should_prune {
+            self.prune_removed_keys(message_state_keys_clone).await;
+        }
+
+        // Now acquire the write lock for the state update and event sending
         let mut aggregate_state = self.into().data.write().await;
 
         // Atomic check and update
@@ -358,7 +374,6 @@ where
                 AggregationEvent::New { slot }
             }
             Some(latest) if slot > latest => {
-                self.prune_removed_keys(message_state_keys).await;
                 aggregate_state.latest_completed_slot = Some(slot);
                 AggregationEvent::New { slot }
             }
```
