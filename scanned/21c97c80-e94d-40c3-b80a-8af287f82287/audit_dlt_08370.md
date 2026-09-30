# [?] [diem-node] Remove shutdown method after fixing network panic

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-01-14
Source: https://github.com/move-language/move/commit/ea931f8d0cb71fd18d18bafaf821886da0dd9f01
Type: security-commit

## Details
[diem-node] Remove shutdown method after fixing network panic

Closes: #7231

## Patch
### diem-node/src/lib.rs
```diff
@@ -48,28 +48,12 @@ pub struct DiemHandle {
     _rpc: Runtime,
     _mempool: Runtime,
     _state_synchronizer: StateSynchronizer,
-    network_runtimes: Vec<Runtime>,
+    _network_runtimes: Vec<Runtime>,
     _consensus_runtime: Option<Runtime>,
     _debug: NodeDebugService,
     _backup: Runtime,
 }
 
-impl DiemHandle {
-    pub fn shutdown(&mut self) {
-        // Shutdown network runtimes to avoid panic error log after DiemHandle is dropped:
-        // thread ‘network-’ panicked at ‘SelectNextSome polled after terminated’,...
-        // stack backtrace:
-        //    ......
-        //    8: network_simple_onchain_discovery::ConfigurationChangeListener::start::{{closure}}
-        //      at network/simple-onchain-discovery/src/lib.rs:175
-        //    ......
-        // Other runtimes don't have same problem.
-        while !self.network_runtimes.is_empty() {
-            self.network_runtimes.remove(0).shutdown_background();
-        }
-    }
-}
-
 pub fn start(config: &NodeConfig, log_file: Option<PathBuf>) {
     crash_handler::setup_panic_handler();
 
@@ -482,7 +466,7 @@ pub fn setup_environment(node_config: &NodeConfig, logger: Option<Arc<Logger>>)
         .spawn(periodic_state_dump(node_config.to_owned(), db_rw));
 
     DiemHandle {
-        network_runtimes,
+        _network_runtimes: network_runtimes,
         _rpc: rpc_runtime,
         _mempool: mempool,
         _state_synchronizer: state_synchronizer,
```

### json-rpc/tests/node.rs
```diff
@@ -9,16 +9,10 @@ use diem_logger::prelude::FileWriter;
 pub struct Node {
     pub config: NodeConfig,
     pub root_key: diem_crypto::ed25519::Ed25519PrivateKey,
-    node: diem_node::DiemHandle,
+    _node: diem_node::DiemHandle,
     _temp_dir: diem_temppath::TempPath,
 }
 
-impl Drop for Node {
-    fn drop(&mut self) {
-        self.node.shutdown();
-    }
-}
-
 impl Node {
     pub fn start() -> Result<Self> {
         let temp_dir = diem_temppath::TempPath::new();
@@ -53,7 +47,7 @@ impl Node {
         Ok(Self {
             root_key,
             config,
-            node,
+            _node: node,
             _temp_dir: temp_dir,
         })
     }
```
