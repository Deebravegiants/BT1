# [?] metrics: Fix race condition in stopwatch

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2019-11-18
Source: https://github.com/graphprotocol/graph-node/commit/206ac421e89cdef22019ecb45ad2334de0020666
Type: security-commit

## Details
metrics: Fix race condition in stopwatch

We've seen the `transact_block` section start
before `run_handler` ended because the section
was being dropped only after the result was sent.

## Patch
### runtime/wasm/src/mapping.rs
```diff
@@ -57,7 +57,7 @@ pub fn spawn_module(
                 )?;
                 section.end();
 
-                let _section = host_metrics.stopwatch.start_section("run_handler");
+                let section = host_metrics.stopwatch.start_section("run_handler");
                 let result = match trigger {
                     MappingTrigger::Log {
                         transaction,
@@ -87,6 +87,7 @@ pub fn spawn_module(
                         module.handle_ethereum_block(handler.handler.as_str())
                     }
                 };
+                section.end();
 
                 result_sender
                     .send((result, future::ok(Instant::now())))
```
