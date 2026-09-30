# [?] runtime: catch panic while handling trigger, fixes oneshot cancelled errors

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2023-05-17
Source: https://github.com/graphprotocol/graph-node/commit/a25233b58331c580a074c4f40081de5ca180da2f
Type: security-commit

## Details
runtime: catch panic while handling trigger, fixes oneshot cancelled errors

## Patch
### runtime/wasm/src/mapping.rs
```diff
@@ -9,8 +9,9 @@ use graph::data_source::{MappingTrigger, TriggerWithHandler};
 use graph::prelude::*;
 use graph::runtime::gas::Gas;
 use std::collections::BTreeMap;
+use std::panic::AssertUnwindSafe;
 use std::sync::Arc;
-use std::thread;
+use std::{panic, thread};
 
 /// Spawn a wasm module in its own thread.
 pub fn spawn_module<C: Blockchain>(
@@ -52,14 +53,32 @@ where
                     result_sender,
                 } = request;
 
-                let result = instantiate_module_and_handle_trigger(
-                    valid_module.cheap_clone(),
-                    ctx,
-                    trigger,
-                    host_metrics.cheap_clone(),
-                    timeout,
-                    experimental_features,
-                );
+                let result = panic::catch_unwind(AssertUnwindSafe(|| {
+                    instantiate_module_and_handle_trigger(
+                        valid_module.cheap_clone(),
+                        ctx,
+                        trigger,
+                        host_metrics.cheap_clone(),
+                        timeout,
+                        experimental_features,
+                    )
+                }));
+
+                let result = match result {
+                    Ok(result) => result,
+                    Err(panic_info) => {
+                        let err_msg = if let Some(payload) = panic_info
+                            .downcast_ref::<String>()
+                            .map(String::as_str)
+                            .or(panic_info.downcast_ref::<&str>().copied())
+                        {
+                            anyhow!("Subgraph panicked with message: {}", payload)
+                        } else {
+                            anyhow!("Subgraph panicked with an unknown payload.")
+                        };
+                        Err(MappingError::Unknown(err_msg))
+                    }
+                };
 
                 result_sender
                     .send(result)
```
