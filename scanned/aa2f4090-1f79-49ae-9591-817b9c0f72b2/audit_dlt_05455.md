# [?] runtime/src/enclave_rpc/client: Fix panic on drop in async context

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2024-10-22
Source: https://github.com/oasisprotocol/oasis-core/commit/cd0f3bea3443d794cc3df13206c146485a64d3ea
Type: security-commit

## Details
runtime/src/enclave_rpc/client: Fix panic on drop in async context

The graceful shutdown of active sessions was removed, as they should
not be closed when the RPC client is dropped. Instead, we should
explicitly invoke the appropriate functions.

## Patch
### .changelog/5917.bugfix.md
```diff
@@ -0,0 +1,5 @@
+runtime/src/enclave_rpc/client: Fix panic on drop in async context
+
+The graceful shutdown of active sessions was removed, as they should
+not be closed when the RPC client is dropped. Instead, we should
+explicitly invoke the appropriate functions.
```

### runtime/src/enclave_rpc/client.rs
```diff
@@ -23,7 +23,6 @@ use crate::{
         time::insecure_posix_time,
     },
     enclave_rpc::{session::Builder, types},
-    future::block_on,
     protocol::Protocol,
 };
 
@@ -623,19 +622,6 @@ impl RpcClient {
     }
 }
 
-impl Drop for RpcClient {
-    fn drop(&mut self) {
-        // Close all sessions after the client is dropped.
-        block_on(async {
-            let sessions = {
-                let mut sessions = self.sessions.lock().await;
-                sessions.drain()
-            };
-            self.close_all(sessions).await;
-        });
-    }
-}
-
 #[cfg(test)]
 mod test {
     use std::sync::{
```
