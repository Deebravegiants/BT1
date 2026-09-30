# [?] graceful shutdown network runtimes in to avoid panic error log thread network- panicked at SelectNextSome polled after terminated

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-09-18
Source: https://github.com/move-language/move/commit/d718857f1214522d71e76f9b4299f2dc9b080215
Type: security-commit

## Details
graceful shutdown network runtimes in to avoid panic error log thread network- panicked at SelectNextSome polled after terminated

## Patch
### libra-node/src/main_node.rs
```diff
@@ -36,12 +36,20 @@ pub struct LibraHandle {
     _rpc: Runtime,
     _mempool: Runtime,
     _state_synchronizer: StateSynchronizer,
-    _network_runtimes: Vec<Runtime>,
+    network_runtimes: Vec<Runtime>,
     _consensus_runtime: Option<Runtime>,
     _debug: NodeDebugService,
     _backup: Runtime,
 }
 
+impl Drop for LibraHandle {
+    fn drop(&mut self) {
+        while self.network_runtimes.len() > 0 {
+            self.network_runtimes.remove(0).shutdown_background();
+        }
+    }
+}
+
 // Fetch chain ID from on-chain resource
 fn fetch_chain_id(db: &DbReaderWriter) -> ChainId {
     let blob = db
@@ -295,7 +303,7 @@ pub fn setup_environment(node_config: &NodeConfig, logger: Option<Arc<Logger>>)
     }
 
     LibraHandle {
-        _network_runtimes: network_runtimes,
+        network_runtimes,
         _rpc: rpc_runtime,
         _mempool: mempool,
         _state_synchronizer: state_synchronizer,
```
