# [?] Avoid a rare panic when a connection is dropped (#6566)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-04-26
Source: https://github.com/ZcashFoundation/zebra/commit/a1b3246d0d7fc9c870a528d6af1aa1489ac55b82
Type: security-commit

## Details
Avoid a rare panic when a connection is dropped (#6566)

## Patch
### zebra-network/src/peer/client.rs
```diff
@@ -621,8 +621,13 @@ impl Service<Request> for Client {
             Ok(()) => {
                 // The receiver end of the oneshot is itself a future.
                 rx.map(|oneshot_recv_result| {
-                    oneshot_recv_result
-                        .expect("ClientRequest oneshot sender must not be dropped before send")
+                    // The ClientRequest oneshot sender should not be dropped before sending a
+                    // response. But sometimes that happens during process or connection shutdown.
+                    // So we just return a generic error here.
+                    match oneshot_recv_result {
+                        Ok(result) => result,
+                        Err(oneshot::Canceled) => Err(PeerError::ConnectionDropped.into()),
+                    }
                 })
                 .boxed()
             }
```
