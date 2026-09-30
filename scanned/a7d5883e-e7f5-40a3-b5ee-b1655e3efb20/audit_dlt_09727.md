# [?] fix(portalloc): reject overflowing port ranges

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-09-17
Source: https://github.com/fedimint/fedimint/commit/cd64cc66d1d840c7535119cf86271ca4439e3c2f
Type: security-commit

## Details
fix(portalloc): reject overflowing port ranges

### Summary

Port allocation now rejects any candidate whose exclusive range endpoint cannot be represented as a `u16`. Previously, endpoint addition could panic with overflow checks or wrap into an empty range, allowing an impossible request to appear successful. The allocator now propagates a descriptive error before persisting a reservation while preserving the existing half-open range representation and candidate-start policy.

### Details

Every candidate endpoint is checked as the allocator advances past reservations or unavailable ports, rather than relying on a one-time size limit. Exact endpoints at `u16::MAX` remain valid, so successful allocation behavior and the inclusive `LOW` through `HIGH` candidate-start policy are unchanged; port 65535 remains outside the half-open `u16` representation.

Regression coverage verifies oversized initial requests, overflow after advancing to a later candidate, exact representable endpoints, ordinary endpoint construction, and the absence of a new reservation on failure. Tests live in a standalone module rather than the production source file.

### Review

An independent review passed with no actionable findings. The reviewer checked arithmetic correctness, edge cases, scope, standalone test organization, and preservation of the existing allocation policy.

## Patch
### utils/portalloc/src/data/dto.rs
```diff
@@ -1,10 +1,14 @@
 use std::collections::BTreeMap;
 use std::net::{TcpListener, UdpSocket};
 
+use anyhow::{Result, anyhow};
 use fedimint_core::util::FmtCompact as _;
 use serde::{Deserialize, Serialize};
 use tracing::{debug, trace, warn};
 
+#[cfg(test)]
+mod tests;
+
 /// The lowest port number to try. Ports below 10k are typically used by normal
 /// software, increasing chance they would get in a way.
 const LOW: u16 = 10000;
@@ -53,7 +57,7 @@ impl Default for RootData {
 }
 
 impl RootData {
-    pub fn get_free_port_range(&mut self, range_size: u16) -> u16 {
+    pub fn get_free_port_range(&mut self, range_size: u16) -> Result<u16> {
         trace!(target: LOG_PORT_ALLOC, range_size, "Looking for port");
 
         self.reclaim();
@@ -65,7 +69,7 @@ impl RootData {
                 self.reclaim();
                 base_port = LOW;
             }
-            let range = base_port..base_port + range_size;
+            let range = port_range(base_port, range_size)?;
             if let Some(next_port) = self.contains(range.clone()) {
                 warn!(
                     base_port,
@@ -95,7 +99,7 @@ impl RootData {
 
             self.insert(range);
             debug!(target: LOG_PORT_ALLOC, base_port, range_size, "Allocated port range");
-            return base_port;
+            return Ok(base_port);
         }
     }
 
@@ -148,21 +152,9 @@ impl RootData {
     }
 }
 
-#[test]
-fn root_data_sanity() {
-    let mut r = RootData::default();
-
-    r.insert(2..4);
-    r.insert(6..8);
-    r.insert(100..108);
-    assert_eq!(r.contains(0..2), None);
-    assert_eq!(r.contains(0..3), Some(4));
-    assert_eq!(r.contains(2..4), Some(4));
-    assert_eq!(r.contains(3..4), Some(4));
-    assert_eq!(r.contains(3..5), Some(4));
-    assert_eq!(r.contains(4..6), None);
-    assert_eq!(r.contains(0..10), Some(8));
-    assert_eq!(r.contains(6..10), Some(8));
-    assert_eq!(r.contains(7..8), Some(8));
-    assert_eq!(r.contains(8..10), None);
+fn port_range(base_port: u16, range_size: u16) -> Result<std::ops::Range<u16>> {
+    let end = base_port.checked_add(range_size).ok_or_else(|| {
+        anyhow!("Port range starting at {base_port} with size {range_size} exceeds u16 bounds")
+    })?;
+    Ok(base_port..end)
 }
```

### utils/portalloc/src/data/dto/tests.rs
```diff
@@ -0,0 +1,54 @@
+use super::{LOW, RootData, port_range};
+
+#[test]
+fn root_data_sanity() {
+    let mut data = RootData::default();
+
+    data.insert(2..4);
+    data.insert(6..8);
+    data.insert(100..108);
+    assert_eq!(data.contains(0..2), None);
+    assert_eq!(data.contains(0..3), Some(4));
+    assert_eq!(data.contains(2..4), Some(4));
+    assert_eq!(data.contains(3..4), Some(4));
+    assert_eq!(data.contains(3..5), Some(4));
+    assert_eq!(data.contains(4..6), None);
+    assert_eq!(data.contains(0..10), Some(8));
+    assert_eq!(data.contains(6..10), Some(8));
+    assert_eq!(data.contains(7..8), Some(8));
+    assert_eq!(data.contains(8..10), None);
+}
+
+#[test]
+fn port_range_rejects_unrepresentable_endpoints() {
+    assert!(port_range(LOW, u16::MAX).is_err());
+}
+
+#[test]
+fn port_range_accepts_representable_endpoints() {
+    assert_eq!(port_range(LOW, 3).expect("range should fit"), LOW..10003);
+    assert_eq!(
+        port_range(LOW, u16::MAX - LOW).expect("range endpoint should fit exactly"),
+        LOW..u16::MAX
+    );
+}
+
+#[test]
+fn failed_range_allocation_does_not_reserve_ports() {
+    let mut data = RootData::default();
+
+    assert!(data.get_free_port_range(u16::MAX).is_err());
+    assert!(data.keys.is_empty());
+    assert_eq!(data.next, LOW);
+}
+
+#[test]
+fn range_allocation_checks_each_candidate_endpoint() {
+    let mut data = RootData::default();
+    data.insert(LOW..LOW + 1);
+    data.next = LOW;
+
+    assert!(data.get_free_port_range(u16::MAX - LOW).is_err());
+    assert_eq!(data.keys.len(), 1);
+    assert!(data.keys.contains_key(&LOW));
+}
```

### utils/portalloc/src/lib.rs
```diff
@@ -37,7 +37,7 @@ pub fn port_alloc(range_size: u16) -> anyhow::Result<u16> {
 
     data_dir.with_lock(|data_dir| {
         let mut data = data_dir.load_data()?;
-        let base_port = data.get_free_port_range(range_size);
+        let base_port = data.get_free_port_range(range_size)?;
         data_dir.store_data(&data)?;
         Ok(base_port)
     })
```
