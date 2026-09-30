# [?] [fix] #2787: Notify every listener to shutdown on panic (#2788)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2022-09-29
Source: https://github.com/hyperledger-iroha/iroha/commit/17ca4e62bba82c42b23a092bfab1eb42e8a85b8e
Type: security-commit

## Details
[fix] #2787: Notify every listener to shutdown on panic (#2788)

Signed-off-by: Shanin Roman <shanin1000@yandex.ru>

## Patch
### cli/src/lib.rs
```diff
@@ -180,7 +180,8 @@ where
 
             iroha_logger::error!(%panic_message, %location, "A panic occured, shutting down");
 
-            notify_shutdown.notify_one();
+            // NOTE: shutdown all currently listening waiters
+            notify_shutdown.notify_waiters();
         }));
     }
 
@@ -390,6 +391,7 @@ where
                 _ = sigterm.recv() => {},
             }
 
+            // NOTE: shutdown all currently listening waiters
             notify_shutdown.notify_waiters();
         });
 
@@ -408,24 +410,26 @@ fn domains(configuration: &Configuration) -> [Domain; 1] {
 
 #[cfg(test)]
 mod tests {
-    use std::{panic, thread};
+    use std::{iter::repeat, panic, thread};
 
+    use futures::future::join_all;
     use serial_test::serial;
 
     use super::*;
 
-    #[allow(clippy::panic)]
+    #[allow(clippy::panic, clippy::print_stdout)]
     #[tokio::test]
     #[serial]
     async fn iroha_should_notify_on_panic() {
         let notify = Arc::new(Notify::new());
         let hook = panic::take_hook();
         <crate::Iroha>::prepare_panic_hook(Arc::clone(&notify));
-        let _res = thread::spawn(move || {
+        let waiters: Vec<_> = repeat(()).take(10).map(|_| Arc::clone(&notify)).collect();
+        let handles: Vec<_> = waiters.iter().map(|waiter| waiter.notified()).collect();
+        thread::spawn(move || {
             panic!("Test panic");
-        })
-        .join();
-        notify.notified().await;
+        });
+        join_all(handles).await;
         panic::set_hook(hook);
     }
 }
```
