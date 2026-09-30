# [?] rust: update to 1.56.1 to mitigate CVE-2021-42574

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-11-01
Source: https://github.com/move-language/move/commit/587ef788fe56276121c2251f84615d8c682200d8
Type: security-commit

## Details
rust: update to 1.56.1 to mitigate CVE-2021-42574

See the advisory for more info: https://blog.rust-lang.org/2021/11/01/cve-2021-42574.html

Closes: #9592

## Patch
### api/src/tests/test_context.rs
```diff
@@ -92,7 +92,7 @@ pub struct TestContext {
     pub db: Arc<DiemDB>,
     rng: rand::rngs::StdRng,
     root_keys: Arc<RootKeys>,
-    executor: Arc<Box<dyn BlockExecutor>>,
+    executor: Arc<dyn BlockExecutor>,
     expect_status_code: u16,
 }
 
@@ -111,7 +111,7 @@ impl TestContext {
             rng,
             root_keys: Arc::new(root_keys),
             validator_owner,
-            executor: Arc::new(executor),
+            executor: executor.into(),
             mempool: Arc::new(mempool),
             expect_status_code: 200,
             db,
```

### language/compiler/src/unit_tests/testutils.rs
```diff
@@ -21,7 +21,7 @@ macro_rules! instr_count {
             .code
             .iter()
             .filter(|ins| matches!(ins, $instr))
-            .count();
+            .count()
     };
 }
 
```

### language/move-model/src/builder/module_builder.rs
```diff
@@ -2991,7 +2991,7 @@ impl<'env, 'translator> ModuleBuilder<'env, 'translator> {
                     let struct_spec = self
                         .struct_specs
                         .remove(&name)
-                        .unwrap_or_else(Spec::default);
+                        .unwrap_or_default();
                     Some((
                         StructId::new(name),
                         self.parent.env.create_move_struct_data(
@@ -3027,7 +3027,7 @@ impl<'env, 'translator> ModuleBuilder<'env, 'translator> {
                 } else {
                     self.symbol_pool().make(name_str)
                 };
-                let fun_spec = self.fun_specs.remove(&name).unwrap_or_else(Spec::default);
+                let fun_spec = self.fun_specs.remove(&name).unwrap_or_default();
                 if let Some(entry) = self.parent.fun_table.get(&self.qualified_by_module(name)) {
                     let arg_names = project_1st(&entry.params);
                     let type_arg_names = project_1st(&entry.type_params);
```

### language/move-prover/bytecode/src/borrow_analysis.rs
```diff
@@ -62,10 +62,7 @@ impl BorrowInfo {
 
     /// Gets incoming edges (together with sources) of this node.
     pub fn get_incoming(&self, node: &BorrowNode) -> SetDomain<(BorrowNode, BorrowEdge)> {
-        self.borrows_from
-            .get(node)
-            .cloned()
-            .unwrap_or_else(SetDomain::default)
+        self.borrows_from.get(node).cloned().unwrap_or_default()
     }
 
     /// Returns true if this node is conditional, that is, it borrows from multiple parents,
```

### language/move-prover/bytecode/src/verification_analysis.rs
```diff
@@ -46,7 +46,7 @@ pub fn get_info(target: &FunctionTarget<'_>) -> VerificationInfo {
         .get_annotations()
         .get::<VerificationInfo>()
         .cloned()
-        .unwrap_or_else(VerificationInfo::default)
+        .unwrap_or_default()
 }
 
 /// A named tuple for holding the information on how an invariant is relevant to a function.
```

### language/move-prover/bytecode/src/verification_analysis_v2.rs
```diff
@@ -37,7 +37,7 @@ pub fn get_info(target: &FunctionTarget<'_>) -> VerificationInfoV2 {
         .get_annotations()
         .get::<VerificationInfoV2>()
         .cloned()
-        .unwrap_or_else(VerificationInfoV2::default)
+        .unwrap_or_default()
 }
 
 // Analysis info to save for global_invariant_instrumentation phase
```

### language/move-vm/types/src/values/values_impl.rs
```diff
@@ -1615,7 +1615,7 @@ impl VectorRef {
 
         macro_rules! err_pop_empty_vec {
             () => {
-                return Err(PartialVMError::new(StatusCode::ABORTED).with_sub_status(POP_EMPTY_VEC));
+                return Err(PartialVMError::new(StatusCode::ABORTED).with_sub_status(POP_EMPTY_VEC))
             };
         }
 
```

### language/testing-infra/test-generation/src/transitions.rs
```diff
@@ -1355,7 +1355,7 @@ macro_rules! state_stack_bin_op {
         Box::new(move |state| stack_bin_op(state, crate::transitions::StackBinOpResult::Right))
     };
     () => {
-        state_stack_bin_op!(#left);
+        state_stack_bin_op!(#left)
     };
     ($e: expr) => {
         Box::new(move |state| stack_bin_op(state, crate::transitions::StackBinOpResult::Other($e)))
```

### rust-toolchain
```diff
@@ -1 +1 @@
-1.54.0
+1.56.1
```

### state-sync/state-sync-v2/data-streaming-service/src/stream_progress_tracker.rs
```diff
@@ -31,7 +31,7 @@ macro_rules! invalid_client_request {
         panic!(
             "Invalid client request {:?} found for the data stream tracker {:?}",
             $client_request, $stream_tracker
-        );
+        )
     };
 }
 
@@ -40,7 +40,7 @@ macro_rules! invalid_response_type {
         panic!(
             "The client response is type mismatched: {:?}",
             $client_response
-        );
+        )
     };
 }
 
@@ -49,7 +49,7 @@ macro_rules! invalid_stream_request {
         panic!(
             "Invalid stream request found {:?}",
             format!("{:?}", $stream_request)
-        );
+        )
     };
 }
 
```

### testsuite/cluster-test/src/tx_emitter.rs
```diff
@@ -699,10 +699,11 @@ impl SubmissionWorker {
                 }
             }
             if self.params.wait_committed {
+                let end_time = (Instant::now() - start_time).as_millis() as u64;
+
                 if let Err(uncommitted) =
                     wait_for_accounts_sequence(&self.client, &mut self.accounts).await
                 {
-                    let end_time = (Instant::now() - start_time).as_millis() as u64;
                     let num_committed = (num_requests - uncommitted.len()) as u64;
                     let latency = end_time - tx_offset_time / num_requests as u64;
                     self.stats
@@ -728,7 +729,6 @@ impl SubmissionWorker {
                         self.client, uncommitted
                     );
                 } else {
-                    let end_time = (Instant::now() - start_time).as_millis() as u64;
                     let latency = end_time - tx_offset_time / num_requests as u64;
                     self.stats
                         .committed
```

### testsuite/forge/src/txn_emitter/mod.rs
```diff
@@ -169,10 +169,11 @@ impl SubmissionWorker {
                 }
             }
             if self.params.wait_committed {
+                let total_duration = (Instant::now() - start_time).as_millis() as u64;
+
                 if let Err(uncommitted) =
                     wait_for_accounts_sequence(&self.client, &mut self.accounts).await
                 {
-                    let total_duration = (Instant::now() - start_time).as_millis() as u64;
                     let num_committed = (num_requests - uncommitted.len()) as u64;
                     // To avoid negative result caused by uncommitted tx occur
                     // Simplified from:
@@ -198,7 +199,6 @@ impl SubmissionWorker {
                         self.client, uncommitted
                     );
                 } else {
-                    let total_duration = (Instant::now() - start_time).as_millis() as u64;
                     let latency = total_duration - txn_offset_time / num_requests as u64;
                     self.stats
                         .committed
```
