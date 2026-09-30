# [?] prevent overflow in port allocation logic for tests (#5889)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-04-19
Source: https://github.com/anza-xyz/agave/commit/13985083f1f6e7ef84302e4e7c1a65bcc8761a61
Type: security-commit

## Details
prevent overflow in port allocation logic for tests (#5889)

prevent overflow in port allocation logic on test-runners with > 59 cores

Co-authored-by: Alex Pyattaev <alex.pyattaev@anza.xyz>

## Patch
### gossip/tests/gossip.rs
```diff
@@ -155,7 +155,7 @@ fn retransmit_to(
 #[test]
 fn gossip_ring() {
     solana_logger::setup();
-    run_gossip_topo(50, |listen| {
+    run_gossip_topo(40, |listen| {
         let num = listen.len();
         for n in 0..num {
             let y = n % listen.len();
```

### net-utils/src/sockets.rs
```diff
@@ -5,9 +5,11 @@ use {
         sync::atomic::{AtomicU16, Ordering},
     },
 };
-
+// base port for deconflicted allocations
 const BASE_PORT: u16 = 5000;
-
+// how much to allocate per individual process.
+// we expect to have at most 64 concurrent tests in CI at any moment on a given host.
+const SLICE_PER_PROCESS: u16 = (u16::MAX - BASE_PORT) / 64;
 /// Retrieve a free 20-port slice for unit tests
 ///
 /// When running under nextest, this will try to provide
@@ -25,15 +27,14 @@ pub fn localhost_port_range_for_tests() -> (u16, u16) {
             Ok(slot) => {
                 let slot: u16 = slot.parse().unwrap();
                 assert!(
-                    offset < 1000,
-                    "Overrunning into the port range of another test!"
+                    offset < SLICE_PER_PROCESS,
+                    "Overrunning into the port range of another test! Consider using fewer ports per test."
                 );
-
-                BASE_PORT + slot * 1000
+                BASE_PORT + slot * SLICE_PER_PROCESS
             }
             Err(_) => BASE_PORT,
         };
-    assert!(start < 65500, "ran out of port numbers!");
+    assert!(start < u16::MAX - 20, "ran out of port numbers!");
     (start, start + 20)
 }
 
```

### nextest.toml
```diff
@@ -5,6 +5,9 @@ dir = "target/nextest"
 failure-output = "immediate-final"
 slow-timeout = { period = "60s", terminate-after = 1 }
 retries = { backoff = "fixed", count = 3, delay = "1s" }
+# Prevent nextest from using > 64 processes at once
+# setting this higher may break port allocation logic in net-utils
+max-threads = 64
 
 [profile.ci.junit]
 path = "junit.xml"
```
