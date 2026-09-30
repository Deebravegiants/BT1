# [?] fix: don't panic on wasmtime loading errors (#15751)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-05-18
Source: https://github.com/near/nearcore/commit/6ecc544e933bf2d29026776a9c24c03305accdde
Type: security-commit

## Details
fix: don't panic on wasmtime loading errors (#15751)

Wasmer didn't have cases where loading could fail after compilation was
successful.

Wasmtime may run into resource limits at load time. We should not panic
on those and instead treat them as deterministic execution errors.

## Patch
### runtime/near-test-contracts/src/lib.rs
```diff
@@ -249,6 +249,38 @@ pub fn function_with_a_lot_of_nop(nops: u64) -> Vec<u8> {
     module.finish()
 }
 
+/// Many zero-initialized globals.
+pub fn contract_with_num_globals(num_globals: u32) -> Vec<u8> {
+    use wasm_encoder::{
+        CodeSection, ConstExpr, ExportKind, ExportSection, Function, FunctionSection,
+        GlobalSection, GlobalType, Instruction, Module, TypeSection, ValType,
+    };
+    let mut module = Module::new();
+    let mut types = TypeSection::new();
+    types.ty().function([], []);
+    module.section(&types);
+    let mut funcs = FunctionSection::new();
+    funcs.function(0);
+    module.section(&funcs);
+    let mut globals = GlobalSection::new();
+    for _ in 0..num_globals {
+        globals.global(
+            GlobalType { val_type: ValType::I32, mutable: false, shared: false },
+            &ConstExpr::i32_const(0),
+        );
+    }
+    module.section(&globals);
+    let mut exports = ExportSection::new();
+    exports.export("main", ExportKind::Func, 0);
+    module.section(&exports);
+    let mut code = CodeSection::new();
+    let mut f = Function::new([]);
+    f.instruction(&Instruction::End);
+    code.function(&f);
+    module.section(&code);
+    module.finish()
+}
+
 /// Wrapper to get more useful Debug.
 pub struct ArbitraryModule(pub wasm_smith::Module);
 
```

### runtime/near-vm-runner/src/logic/errors.rs
```diff
@@ -54,14 +54,21 @@ pub enum FunctionCallError {
     /// A trap happened during execution of a binary
     WasmTrap(WasmTrap),
     HostError(HostError),
+    /// The compiled module was rejected by the VM host when instantiating it.
+    /// This covers host-side resource limits.
+    LoadingError {
+        msg: String,
+    },
 }
 
 impl FunctionCallError {
     pub fn size_bytes_approximate(&self) -> usize {
         const BASE_SIZE: usize = 4; // to roughly accommodate for static parts of the enum
         match self {
             FunctionCallError::CompilationError(e) => e.size_bytes_approximate(),
-            FunctionCallError::LinkError { msg } => BASE_SIZE + msg.len(),
+            FunctionCallError::LinkError { msg } | FunctionCallError::LoadingError { msg } => {
+                BASE_SIZE + msg.len()
+            }
             FunctionCallError::MethodResolveError(_)
             | FunctionCallError::WasmTrap(_)
             | FunctionCallError::HostError(_) => BASE_SIZE,
@@ -449,6 +456,7 @@ impl fmt::Display for FunctionCallError {
             FunctionCallError::MethodResolveError(e) => e.fmt(f),
             FunctionCallError::HostError(e) => e.fmt(f),
             FunctionCallError::LinkError { msg } => write!(f, "{}", msg),
+            FunctionCallError::LoadingError { msg } => write!(f, "Loading error: {}", msg),
             FunctionCallError::WasmTrap(trap) => write!(f, "WebAssembly trap: {}", trap),
         }
     }
```

### runtime/near-vm-runner/src/tests/runtime_errors.rs
```diff
@@ -1,7 +1,55 @@
 use super::test_builder::test_builder;
+use crate::logic::errors::VMRunnerError;
+use crate::logic::mocks::mock_external::MockedExternal;
+use crate::runner::VMKindExt;
 use expect_test::expect;
+use near_parameters::RuntimeFeesConfig;
+use near_parameters::vm::VMKind;
+use near_primitives_core::code::ContractCode;
 use near_primitives_core::types::Gas;
 use std::fmt::Write;
+use std::sync::Arc;
+
+/// Compile and load a contract with 100k globals.
+///
+/// Each global produces 8 bytes of instance data, so globals alone add 800kB.
+/// In total, that breaches the (default) limit of 1MiB for
+/// `max_core_instance_size` for the Wasmtime pooling allocator.
+///
+/// This must return `VMRunnerError::LoadingError` and not panic / crash the node.
+///
+/// Other VM backends don't use a pooling allocator with this limit, so they should
+/// run the contract successfully.
+#[test]
+fn test_max_core_instance_size_breached() {
+    let wasm = near_test_contracts::contract_with_num_globals(100_000);
+
+    super::with_vm_variants(|vm_kind| {
+        let code = ContractCode::new(wasm.clone(), None);
+        let config = Arc::new(super::test_vm_config(Some(vm_kind)));
+        let fees = Arc::new(RuntimeFeesConfig::test());
+        let mut ext = MockedExternal::with_code(code.clone_for_tests());
+        let context = super::create_context(vec![]);
+        let gas_counter = context.make_gas_counter(&config);
+
+        let result = vm_kind
+            .runtime(config)
+            .unwrap()
+            .prepare(&ext, None, gas_counter, "main")
+            .run(&mut ext, &context, fees);
+
+        match vm_kind {
+            VMKind::Wasmtime => assert!(
+                matches!(result, Err(VMRunnerError::LoadingError(_))),
+                "Wasmtime: expected LoadingError for oversized instance, got: {result:?}",
+            ),
+            _ => assert!(
+                result.as_ref().is_ok_and(|outcome| outcome.aborted.is_none()),
+                "{vm_kind:?}: expected clean success for many-globals contract, got: {result:?}",
+            ),
+        }
+    });
+}
 
 const FIX_CONTRACT_LOADING_COST: u32 = 129;
 
```

### runtime/runtime/src/conversions.rs
```diff
@@ -80,6 +80,9 @@ mod function_call_error {
                 // on specific types in Rust code.
                 From::HostError(ref _e) => Self::ExecutionError(outer_err.to_string()),
                 From::LinkError { msg } => Self::ExecutionError(format!("Link Error: {}", msg)),
+                From::LoadingError { msg } => {
+                    Self::ExecutionError(format!("Loading Error: {}", msg))
+                }
                 From::WasmTrap(ref _e) => Self::ExecutionError(outer_err.to_string()),
             }
         }
```

### runtime/runtime/src/function_call.rs
```diff
@@ -108,7 +108,12 @@ pub(crate) fn action_function_call(
                     .with_label_values::<&str>(&[err.into()])
                     .inc();
             }
-            FunctionCallError::LinkError { .. } => (),
+            FunctionCallError::LinkError { .. } => {
+                metrics::FUNCTION_CALL_PROCESSED_LINK_ERRORS.inc();
+            }
+            FunctionCallError::LoadingError { .. } => {
+                metrics::FUNCTION_CALL_PROCESSED_LOADING_ERRORS.inc();
+            }
             FunctionCallError::MethodResolveError(err) => {
                 metrics::FUNCTION_CALL_PROCESSED_METHOD_RESOLVE_ERRORS
                     .with_label_values::<&str>(&[err.into()])
@@ -323,7 +328,7 @@ pub(crate) fn execute_function_call(
             return Err(StorageError::StorageInconsistentState(err.to_string()).into());
         }
         Err(VMRunnerError::LoadingError(msg)) => {
-            panic!("Contract runtime failed to load a contract: {msg}")
+            return Ok(VMOutcome::nop_outcome(FunctionCallError::LoadingError { msg }));
         }
         Err(VMRunnerError::Nondeterministic(msg)) => {
             panic!("Contract runner returned non-deterministic error '{}', aborting", msg)
```

### runtime/runtime/src/metrics.rs
```diff
@@ -266,6 +266,20 @@ pub static FUNCTION_CALL_PROCESSED_HOST_ERRORS: LazyLock<IntCounterVec> = LazyLo
     )
     .unwrap()
 });
+pub static FUNCTION_CALL_PROCESSED_LINK_ERRORS: LazyLock<IntCounter> = LazyLock::new(|| {
+    try_create_int_counter(
+        "near_function_call_processed_link_errors",
+        "The number of function calls resulting in link errors, since starting this node",
+    )
+    .unwrap()
+});
+pub static FUNCTION_CALL_PROCESSED_LOADING_ERRORS: LazyLock<IntCounter> = LazyLock::new(|| {
+    try_create_int_counter(
+        "near_function_call_processed_loading_errors",
+        "The number of function calls resulting in loading errors, since starting this node",
+    )
+    .unwrap()
+});
 pub static FUNCTION_CALL_PROCESSED_CACHE_ERRORS: LazyLock<IntCounterVec> = LazyLock::new(|| {
     try_create_int_counter_vec(
         "near_function_call_processed_cache_errors",
```
