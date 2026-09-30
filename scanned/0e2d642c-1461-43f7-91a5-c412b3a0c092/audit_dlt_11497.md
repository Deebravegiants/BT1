# [?] fix race condition that allows duplicate slot

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2025-03-12
Source: https://github.com/pyth-network/pyth-crosschain/commit/3fa049cb14342a3e08c3ea68c42c01089bdb2719
Type: security-commit

## Details
fix race condition that allows duplicate slot

## Patch
### apps/hermes/server/src/state/aggregate.rs
```diff
@@ -351,28 +351,27 @@ where
         // Update the aggregate state
         let mut aggregate_state = self.into().data.write().await;
 
-        // Send update event to subscribers. We are purposefully ignoring the result
-        // because there might be no subscribers.
-        let _ = match aggregate_state.latest_completed_slot {
+        // Atomic check and update
+        let event = match aggregate_state.latest_completed_slot {
             None => {
-                aggregate_state.latest_completed_slot.replace(slot);
-                self.into()
-                    .api_update_tx
-                    .send(AggregationEvent::New { slot })
+                aggregate_state.latest_completed_slot = Some(slot);
+                AggregationEvent::New { slot }
             }
             Some(latest) if slot > latest => {
                 self.prune_removed_keys(message_state_keys).await;
-                aggregate_state.latest_completed_slot.replace(slot);
-                self.into()
-                    .api_update_tx
-                    .send(AggregationEvent::New { slot })
+                aggregate_state.latest_completed_slot = Some(slot);
+                AggregationEvent::New { slot }
             }
-            _ => self
-                .into()
-                .api_update_tx
-                .send(AggregationEvent::OutOfOrder { slot }),
+            Some(latest) if slot == latest => {
+                // Don't send duplicate events for the same slot
+                return Ok(());
+            }
+            _ => AggregationEvent::OutOfOrder { slot },
         };
 
+        // Only send the event after the state has been updated
+        let _ = self.into().api_update_tx.send(event);
+
         aggregate_state.latest_completed_slot = aggregate_state
             .latest_completed_slot
             .map(|latest| latest.max(slot))
```
