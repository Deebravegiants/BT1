# [?] fix(engine): avoid panic on payload stream termination (#27218)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-09-14
Source: https://github.com/paradigmxyz/reth/commit/ee845e317f903f14d7cb9ec47a7e3f387d95c8ec
Type: security-commit

## Details
fix(engine): avoid panic on payload stream termination (#27218)

## Patch
### crates/node/builder/src/launch/engine.rs
```diff
@@ -376,7 +376,7 @@ impl EngineNodeLauncher {
                             }
                         }
                     }
-                    payload = built_payloads.select_next_some(), if !built_payloads.is_terminated() => {
+                    Some(payload) = built_payloads.next(), if !built_payloads.is_terminated() => {
                         if let Some(executed_block) = payload.executed_block() {
                             debug!(target: "reth::cli", block=?executed_block.recovered_block.num_hash(),  "inserting built payload");
                             orchestrator.handler_mut().handler_mut().on_event(EngineApiRequest::InsertExecutedBlock(executed_block).into());
```
