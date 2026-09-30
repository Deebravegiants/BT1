# [?] Fix AsyncSender so that the callback does not panic when the response future is dropped. (#10662)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-02-27
Source: https://github.com/near/nearcore/commit/db39fa2bb899b1afa41547ed8136e604d9efeabd
Type: security-commit

## Details
Fix AsyncSender so that the callback does not panic when the response future is dropped. (#10662)

Also add a test for this behavior.

Closes #10660

## Patch
### Cargo.lock
```diff
@@ -3425,6 +3425,7 @@ dependencies = [
  "serde_json",
  "time",
  "tokio",
+ "tokio-util 0.7.2",
 ]
 
 [[package]]
```

### core/async/Cargo.toml
```diff
@@ -28,6 +28,7 @@ near-performance-metrics.workspace = true
 
 [dev-dependencies]
 derive-enum-from-into.workspace = true
+tokio-util.workspace = true
 
 [features]
 nightly = [
```

### core/async/src/messaging.rs
```diff
@@ -87,7 +87,11 @@ impl<M, R: Send + 'static, A: CanSend<MessageWithCallback<M, R>> + ?Sized> SendA
         // Dropped error.
         let (sender, receiver) = oneshot::channel::<Result<R, AsyncSendError>>();
         let future = async move { receiver.await.unwrap_or_else(|_| Err(AsyncSendError::Dropped)) };
-        let responder = Box::new(move |r| sender.send(r).ok().unwrap());
+        let responder = Box::new(move |r| {
+            // It's ok for the send to return an error, because that means the receiver is dropped
+            // therefore the sender does not care about the result.
+            sender.send(r).ok();
+        });
         self.send(MessageWithCallback { message, callback: responder });
         future.boxed()
     }
@@ -207,3 +211,49 @@ impl<A, B: MultiSenderFrom<A>> IntoMultiSender<B> for A {
         B::multi_sender_from(Arc::new(self))
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use crate::messaging::{AsyncSendError, MessageWithCallback, Sender};
+    use tokio_util::sync::CancellationToken;
+
+    #[tokio::test]
+    async fn test_async_send_sender_dropped() {
+        // The handler drops the callback, making the response will never resolve.
+        let sender: Sender<MessageWithCallback<u32, u32>> = Sender::from_fn(|_| {});
+        let result = sender.send_async(4).await;
+        assert_eq!(result, Err(AsyncSendError::Dropped));
+    }
+
+    #[tokio::test]
+    async fn test_async_send_receiver_dropped() {
+        // Test that if the receiver is dropped, the sending side will not panic.
+        let result_blocker = CancellationToken::new();
+        let callback_done = CancellationToken::new();
+
+        let default_panic = std::panic::take_hook();
+        std::panic::set_hook(Box::new(move |info| {
+            default_panic(info);
+            std::process::abort();
+        }));
+
+        let sender = {
+            let result_blocker = result_blocker.clone();
+            let callback_done = callback_done.clone();
+            Sender::<MessageWithCallback<u32, u32>>::from_fn(move |msg| {
+                let MessageWithCallback { message, callback } = msg;
+                let result_blocker = result_blocker.clone();
+                let callback_done = callback_done.clone();
+                tokio::spawn(async move {
+                    result_blocker.cancelled().await;
+                    callback(Ok(message));
+                    callback_done.cancel();
+                });
+            })
+        };
+
+        drop(sender.send_async(4)); // drops the resulting future
+        result_blocker.cancel();
+        callback_done.cancelled().await;
+    }
+}
```
