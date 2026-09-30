# [?] fix: prevent timestamp underflow in hole punching (#5324)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-09-09
Source: https://github.com/nervosnetwork/ckb/commit/835c3902e6c0031e21048f99e29fa24bab9e6b52
Type: security-commit

## Details
fix: prevent timestamp underflow in hole punching (#5324)

**Thanks Mohd Huzaifa for helping us finding this issue**

### What problem does this PR solve?

  Problem Summary:

The HolePunching protocol calculated elapsed time using direct `u64`
timestamp subtraction. Because these timestamps come from the system
clock, a backward clock adjustment could cause
  an integer underflow and panic, potentially shutting down the node.

  ### What is changed and how it works?

  What's Changed:

  - Add a shared `elapsed_millis` helper using `saturating_sub`.
- Use the helper when cleaning up pending deliveries and in-flight
requests.
  - Use the helper when checking the hole-punching request interval.
  - Use the helper when calculating the NAT traversal TTL.
  - Add a regression test covering backward clock adjustments.

  ### Related changes

  None.

  ### Check List

  Tests

  - [x] Unit test: `cargo test -p ckb-network --lib -- --test-threads=1`

## Patch
### network/src/protocols/hole_punching/component/connection_request.rs
```diff
@@ -16,6 +16,7 @@ use crate::{
         hole_punching::{
             ADDRS_COUNT_LIMIT, HOLE_PUNCHING_INTERVAL, HolePunching, MAX_HOPS,
             component::{forward_request, init_delivered},
+            elapsed_millis,
             status::{Status, StatusCode},
         },
     },
@@ -170,7 +171,7 @@ impl<'a> ConnectionRequestProcess<'a> {
     ) -> Status {
         if let Some((_, t)) = self.protocol.pending_delivered.get(&from_peer_id) {
             let now = unix_time_as_millis();
-            if now - t < HOLE_PUNCHING_INTERVAL {
+            if elapsed_millis(now, *t) < HOLE_PUNCHING_INTERVAL {
                 return StatusCode::Ignore
                     .with_context("a same message is already replied in a moment ago");
             }
```

### network/src/protocols/hole_punching/component/connection_request_delivered.rs
```diff
@@ -18,6 +18,7 @@ use crate::{
         hole_punching::{
             ADDRS_COUNT_LIMIT, HolePunching, MAX_HOPS,
             component::{forward_delivered, init_sync, try_nat_traversal},
+            elapsed_millis,
             status::{Status, StatusCode},
         },
     },
@@ -164,7 +165,7 @@ impl<'a> ConnectionRequestDeliveredProcess<'a> {
                                 return res;
                             }
                             let now = unix_time_as_millis();
-                            let ttl = now - start;
+                            let ttl = elapsed_millis(now, start);
 
                             self.try_nat_traversal(ttl, content.listen_addrs);
 
```

### network/src/protocols/hole_punching/mod.rs
```diff
@@ -29,6 +29,10 @@ const TIMEOUT: u64 = 5 * 60 * 1000; // 5 minutes
 const FORWARD_RATE_LIMIT_INTERVAL: u64 = 1000;
 pub(super) const MAX_FORWARD_RATE_LIMITER_KEYS: usize = 4096;
 
+fn elapsed_millis(now: u64, timestamp: u64) -> u64 {
+    now.saturating_sub(timestamp)
+}
+
 type PendingDeliveredInfo = (Vec<Multiaddr>, u64);
 type RateLimiter<T> = governor::RateLimiter<
     T,
@@ -217,8 +221,9 @@ impl ServiceProtocol for HolePunching {
 
         let now = unix_time_as_millis();
         self.pending_delivered
-            .retain(|_, (_, t)| (now - *t) < TIMEOUT);
-        self.inflight_requests.retain(|_, t| (now - *t) < TIMEOUT);
+            .retain(|_, (_, t)| elapsed_millis(now, *t) < TIMEOUT);
+        self.inflight_requests
+            .retain(|_, t| elapsed_millis(now, *t) < TIMEOUT);
         self.cleanup_rate_limiters();
 
         if status.non_whitelist_outbound < status.max_outbound && status.total > 0 {
@@ -374,3 +379,14 @@ impl HolePunching {
         self.forward_rate_limiter.shrink_to_fit();
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::elapsed_millis;
+
+    #[test]
+    fn elapsed_millis_saturates_when_clock_moves_backwards() {
+        assert_eq!(elapsed_millis(100, 200), 0);
+        assert_eq!(elapsed_millis(200, 100), 100);
+    }
+}
```
