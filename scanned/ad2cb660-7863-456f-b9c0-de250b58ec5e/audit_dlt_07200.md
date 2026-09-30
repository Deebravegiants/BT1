# [?] fix(panic): remove panic in `close_and_flush_next` fn (#4782)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2022-07-17
Source: https://github.com/ZcashFoundation/zebra/commit/ff1c8dd4a115b687291c36e9dd676cc8249ba197
Type: security-commit

## Details
fix(panic): remove panic in `close_and_flush_next` fn (#4782)

* remove panic in `close_and_flush_next` fn

* Explain that `try_next()`'s documentation is wrong

Co-authored-by: teor <teor@riseup.net>

## Patch
### zebra-network/src/peer/client.rs
```diff
@@ -201,7 +201,6 @@ impl ClientRequestReceiver {
     /// Closing the channel ensures that:
     /// - the request stream terminates, and
     /// - task notifications are not required.
-    #[allow(clippy::unwrap_in_result)]
     pub fn close_and_flush_next(&mut self) -> Option<InProgressClientRequest> {
         self.inner.close();
 
@@ -210,10 +209,10 @@ impl ClientRequestReceiver {
         // The request stream terminates, because the sender is closed,
         // and the channel has a limited capacity.
         // Task notifications are not required, because the sender is closed.
-        self.inner
-            .try_next()
-            .expect("channel is closed")
-            .map(Into::into)
+        //
+        // Despite what its documentation says, we've seen futures::channel::mpsc::Receiver::try_next()
+        // return an error after the channel is closed.
+        self.inner.try_next().ok()?.map(Into::into)
     }
 }
 
```
