# [?] fix(network): arithmetic overflow (#14875)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-01-15
Source: https://github.com/near/nearcore/commit/abbed2da82902cf468ef7fcb38d92c68ee6abda6
Type: security-commit

## Details
fix(network): arithmetic overflow (#14875)

See https://github.com/near/nearcore-private/pull/150

## Patch
### chain/network/src/peer/peer_actor.rs
```diff
@@ -1456,7 +1456,8 @@ impl PeerActor {
                     }
                 } else {
                     if msg.decrease_ttl() {
-                        *msg.num_hops_mut() += 1;
+                        let num_hops = msg.num_hops_mut();
+                        *num_hops = num_hops.saturating_add(1);
                         self.network_state.send_message_to_peer(&self.clock, conn.tier, msg);
                     } else {
                         #[cfg(test)]
```

### chain/network/src/stats/metrics.rs
```diff
@@ -431,13 +431,16 @@ fn record_routed_msg_latency(
     tier: tcp::Tier,
     fastest: bool,
 ) {
-    if let Some(created_at) = msg.created_at() {
-        let now = clock.now_utc().unix_timestamp();
-        let duration = now - created_at;
-        NETWORK_ROUTED_MSG_LATENCY
-            .with_label_values(&[msg.body_variant(), tier.as_ref(), bool_to_str(fastest)])
-            .observe(duration as f64);
-    }
+    let Some(created_at) = msg.created_at() else {
+        return;
+    };
+    let now = clock.now_utc().unix_timestamp();
+    let Some(duration) = now.checked_sub(created_at) else {
+        return;
+    };
+    NETWORK_ROUTED_MSG_LATENCY
+        .with_label_values(&[msg.body_variant(), tier.as_ref(), bool_to_str(fastest)])
+        .observe(duration as f64);
 }
 
 // The routed message reached its destination. If the number of hops is known, then update the
```
