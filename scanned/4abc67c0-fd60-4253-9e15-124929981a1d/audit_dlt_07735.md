# [?] fix: don't deadlock on repeated payloads (#22971)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-03-11
Source: https://github.com/paradigmxyz/reth/commit/ec59698ef63beabc5a27dd1d31eab50b81f61e6c
Type: security-commit

## Details
fix: don't deadlock on repeated payloads (#22971)

## Patch
### crates/payload/builder/src/service.rs
```diff
@@ -456,9 +456,11 @@ where
                                     // Clear stale cached payload for this id so
                                     // resolve() never returns an outdated result
                                     // from a previous job with the same id.
-                                    if let Some((cached_id, _, _)) =
-                                        &*this.cached_payload_rx.borrow() &&
-                                        *cached_id == id
+                                    if this
+                                        .cached_payload_rx
+                                        .borrow()
+                                        .as_ref()
+                                        .is_some_and(|(cached_id, _, _)| *cached_id == id)
                                     {
                                         trace!(target: "payload_builder", %id, "clearing stale cached payload for reused payload id");
                                         let _ = this.cached_payload_tx.send(None);
```
