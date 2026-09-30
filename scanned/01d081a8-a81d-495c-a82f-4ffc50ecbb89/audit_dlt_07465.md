# [?] Fix a deadlock in network crate. (#921)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-02-09
Source: https://github.com/Conflux-Chain/conflux-rust/commit/51ddca4f757ffc7ddb343af8a17b4d1f500ad442
Type: security-commit

## Details
Fix a deadlock in network crate. (#921)

* Fix a deadlock in network crate.

* Revert "Fix a deadlock in network crate."

This reverts commit cebcefbfdb75a6786722e7d3db17548fb0121e66.

* Move lock out of match.

lock will not be dropped until the body of match ends.

## Patch
### network/src/service.rs
```diff
@@ -392,13 +392,14 @@ impl DelayedQueue {
 
     fn send_delayed_messages(&self, network_service: &NetworkServiceInner) {
         let context = self.queue.lock().pop().unwrap();
-        match context.session.write().send_packet(
+        let r = context.session.write().send_packet(
             &context.io,
             Some(context.protocol),
             session::PACKET_USER,
             context.msg,
             context.priority,
-        ) {
+        );
+        match r {
             Ok(_) => {}
             Err(Error(ErrorKind::Expired, _)) => {
                 // If a connection is set expired, it should have been killed
```
