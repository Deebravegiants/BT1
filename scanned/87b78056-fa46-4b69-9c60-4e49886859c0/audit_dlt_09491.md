# [?] fix race condition in contract runtime

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2023-02-03
Source: https://github.com/casper-network/casper-node/commit/26667a50aaf2225a2eb27e0e0de6a750fc26fcaf
Type: security-commit

## Details
fix race condition in contract runtime

## Patch
### node/src/components/contract_runtime.rs
```diff
@@ -452,8 +452,9 @@ impl ContractRuntime {
             } => {
                 let mut effects = Effects::new();
                 let exec_queue = Arc::clone(&self.exec_queue);
-                let next_block_height = self.execution_pre_state.lock().unwrap().next_block_height;
                 let finalized_block_height = finalized_block.height();
+                let current_pre_state = self.execution_pre_state.lock().unwrap();
+                let next_block_height = current_pre_state.next_block_height;
                 match finalized_block_height.cmp(&next_block_height) {
                     Ordering::Less => {
                         debug!(
@@ -470,13 +471,14 @@ impl ContractRuntime {
                         let protocol_version = self.protocol_version;
                         let engine_state = Arc::clone(&self.engine_state);
                         let metrics = Arc::clone(&self.metrics);
-                        let execution_pre_state = Arc::clone(&self.execution_pre_state);
+                        let shared_pre_state = Arc::clone(&self.execution_pre_state);
                         effects.extend(
                             Self::execute_finalized_block_or_requeue(
                                 engine_state,
                                 metrics,
                                 exec_queue,
-                                execution_pre_state,
+                                shared_pre_state,
+                                current_pre_state.clone(),
                                 effect_builder,
                                 protocol_version,
                                 finalized_block,
@@ -720,7 +722,8 @@ impl ContractRuntime {
         engine_state: Arc<EngineState<LmdbGlobalState>>,
         metrics: Arc<Metrics>,
         exec_queue: ExecQueue,
-        execution_pre_state: Arc<Mutex<ExecutionPreState>>,
+        shared_pre_state: Arc<Mutex<ExecutionPreState>>,
+        current_pre_state: ExecutionPreState,
         effect_builder: EffectBuilder<REv>,
         protocol_version: ProtocolVersion,
         finalized_block: FinalizedBlock,
@@ -735,7 +738,6 @@ impl ContractRuntime {
             + Send,
     {
         debug!("ContractRuntime: execute_finalized_block_or_requeue");
-        let current_execution_pre_state = execution_pre_state.lock().unwrap().clone();
         let contract_runtime_metrics = metrics.clone();
         let BlockAndExecutionResults {
             block,
@@ -748,7 +750,7 @@ impl ContractRuntime {
                 engine_state.as_ref(),
                 Some(contract_runtime_metrics),
                 protocol_version,
-                current_execution_pre_state,
+                current_pre_state,
                 finalized_block,
                 deploys,
             )
@@ -764,7 +766,7 @@ impl ContractRuntime {
             next_block_height = new_execution_pre_state.next_block_height,
             "ContractRuntime: updating new_execution_pre_state",
         );
-        *execution_pre_state.lock().unwrap() = new_execution_pre_state.clone();
+        *shared_pre_state.lock().unwrap() = new_execution_pre_state.clone();
         debug!("ContractRuntime: updated new_execution_pre_state");
 
         let current_era_id = block.header().era_id();
```
