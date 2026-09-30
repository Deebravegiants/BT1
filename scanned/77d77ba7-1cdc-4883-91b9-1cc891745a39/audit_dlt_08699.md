# [?] Merge branch 'master' into fix/panic-recovery

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2026-02-25
Source: https://github.com/OffchainLabs/nitro/commit/dbf709a2a4646630274fd4ff70bdffc9b677fff5
Type: security-commit

## Details
Merge branch 'master' into fix/panic-recovery

## Patch
### changelog/pmikolajczyk-nit-4465.md
```diff
@@ -0,0 +1,2 @@
+### Internal
+ - Cache precompiled wasm modules for repeated JIT validation
```

### crates/jit/src/lib.rs
```diff
@@ -10,7 +10,7 @@ use std::net::TcpStream;
 use std::path::PathBuf;
 use std::time::Duration;
 use validation::{BatchInfo, UserWasm};
-use wasmer::{FrameInfo, Pages};
+use wasmer::{FrameInfo, FunctionEnv, Instance, Pages, Store};
 
 mod arbcompress;
 mod arbcrypto;
@@ -23,6 +23,8 @@ mod test;
 mod wasip1_stub;
 mod wavmio;
 
+pub use machine::CompiledModule;
+
 #[derive(Clone, Debug, Parser)]
 pub struct Opts {
     /// General validator configuration
@@ -141,15 +143,34 @@ pub struct RunResult {
     pub socket: Option<BufWriter<TcpStream>>,
 }
 
+/// Runs JIT validation, compiling the binary fresh each time.
+///
+/// For repeated executions with the same binary, prefer [`run_with_module`]
+/// with a cached [`CompiledModule`].
 pub fn run(opts: &Opts) -> eyre::Result<RunResult> {
     let (instance, env, mut store) = machine::create(opts)?;
-    let outcome = instance
-        .exports
-        .get_function("_start")?
-        .call(&mut store, &[]);
+    run_instance(instance, env, &mut store)
+}
+
+/// Runs JIT validation using a pre-compiled module.
+///
+/// This avoids re-compiling the WASM binary on every call. The caller is
+/// responsible for caching the [`CompiledModule`] (e.g. per `module_root`).
+pub fn run_with_module(compiled: &CompiledModule, opts: &Opts) -> eyre::Result<RunResult> {
+    let (instance, env, mut store) = machine::instantiate(compiled, opts)?;
+    run_instance(instance, env, &mut store)
+}
+
+/// Runs a fully-instantiated WASM instance and collects the result.
+fn run_instance(
+    instance: Instance,
+    env: FunctionEnv<machine::WasmEnv>,
+    store: &mut Store,
+) -> eyre::Result<RunResult> {
+    let outcome = instance.exports.get_function("_start")?.call(store, &[]);
 
-    let memory_used = instance.exports.get_memory("memory")?.view(&store).size();
-    let env = env.as_mut(&mut store);
+    let memory_used = instance.exports.get_memory("memory")?.view(store).size();
+    let env = env.as_mut(store);
 
     let mut result = RunResult {
         memory_used,
```

### crates/jit/src/machine.rs
```diff
@@ -4,6 +4,7 @@
 use crate::{
     arbcompress, arbcrypto, prepare::prepare_env_from_json, program,
     stylus_backend::CothreadHandler, wasip1_stub, wavmio, InputMode, LocalInput, NativeInput, Opts,
+    ValidatorOpts,
 };
 use arbutil::{Bytes32, PreimageType};
 use caller_env::GoRuntimeState;
@@ -21,49 +22,93 @@ use std::{
 use thiserror::Error;
 use validation::BatchInfo;
 use wasmer::{
-    imports, CompilerConfig, Function, FunctionEnv, FunctionEnvMut, Instance, Memory, Module,
-    RuntimeError, Store,
+    imports, CompilerConfig, Engine, Function, FunctionEnv, FunctionEnvMut, Instance, Memory,
+    Module, RuntimeError, Store,
 };
 use wasmer_compiler_cranelift::Cranelift;
 
-pub fn create(opts: &Opts) -> Result<(Instance, FunctionEnv<WasmEnv>, Store)> {
-    let mut store = match opts.validator.cranelift {
-        true => get_store_with_cranelift_compiler(),
-        false => get_store_with_llvm_compiler(),
-    };
+/// A pre-compiled WASM module bundled with the Engine that produced it.
+///
+/// Cheap to clone (both `Module` and `Engine` are Arc-based internally).
+/// Safe to share across threads (`Send + Sync`).
+///
+/// Use [`compile_module`] to create one, then [`instantiate`] to create
+/// per-request instances cheaply.
+#[derive(Clone)]
+pub struct CompiledModule {
+    module: Module,
+    engine: Engine,
+}
+
+/// Compiles a WASM binary into a reusable [`CompiledModule`].
+///
+/// This is the expensive operation that should be done once and cached.
+/// The resulting `CompiledModule` can be passed to [`instantiate`] to create
+/// per-request instances without re-compiling.
+pub fn compile_module(validator: &ValidatorOpts) -> Result<CompiledModule> {
+    let engine = make_engine(validator.cranelift);
+    let wasm = std::fs::read(&validator.binary)?;
+    let module = Module::new(&engine, wasm)?;
+    Ok(CompiledModule { module, engine })
+}
+
+/// Creates a new WASM instance from a pre-compiled module and per-request options.
+///
+/// This is the cheap, per-request operation. It creates a fresh `Store` from the
+/// compiled module's `Engine`, builds the `WasmEnv`, and instantiates the module.
+pub fn instantiate(
+    compiled: &CompiledModule,
+    opts: &Opts,
+) -> Result<(Instance, FunctionEnv<WasmEnv>, Store)> {
+    let mut store = Store::new(compiled.engine.clone());
 
     let env = WasmEnv::try_from(opts)?;
     let func_env = FunctionEnv::new(&mut store, env);
 
-    let wasm = std::fs::read(&opts.validator.binary)?;
-    let module = Module::new(&store, wasm)?;
     let imports = imports(&mut store, &func_env);
-    let instance = Instance::new(&mut store, &module, &imports)?;
+    let instance = Instance::new(&mut store, &compiled.module, &imports)?;
 
     let memory = instance.exports.get_memory("memory")?.clone();
     func_env.as_mut(&mut store).memory = Some(memory);
 
     Ok((instance, func_env, store))
 }
 
-fn get_store_with_cranelift_compiler() -> Store {
+/// Creates a WASM instance by compiling the binary and instantiating it.
+///
+/// This is a convenience function that combines [`compile_module`] and [`instantiate`].
+/// For repeated executions with the same binary, prefer caching the result of
+/// `compile_module()` and calling `instantiate()` directly.
+pub fn create(opts: &Opts) -> Result<(Instance, FunctionEnv<WasmEnv>, Store)> {
+    let compiled = compile_module(&opts.validator)?;
+    instantiate(&compiled, opts)
+}
+
+fn make_engine(cranelift: bool) -> Engine {
+    match cranelift {
+        true => make_cranelift_engine(),
+        false => make_llvm_engine(),
+    }
+}
+
+fn make_cranelift_engine() -> Engine {
     let mut compiler = Cranelift::new();
     compiler.canonicalize_nans(true);
     compiler.enable_verifier();
-    Store::new(compiler)
+    Engine::from(compiler)
 }
 
 #[cfg(not(feature = "llvm"))]
-fn get_store_with_llvm_compiler() -> Store {
+fn make_llvm_engine() -> Engine {
     panic!("Please rebuild with the \"llvm\" feature for LLVM support");
 }
 #[cfg(feature = "llvm")]
-fn get_store_with_llvm_compiler() -> Store {
+fn make_llvm_engine() -> Engine {
     let mut compiler = wasmer_compiler_llvm::LLVM::new();
     compiler.canonicalize_nans(true);
     compiler.opt_level(wasmer_compiler_llvm::LLVMOptLevel::Aggressive);
     compiler.enable_verifier();
-    Store::new(compiler)
+    Engine::from(compiler)
 }
 
 fn imports(store: &mut Store, func_env: &FunctionEnv<WasmEnv>) -> wasmer::Imports {
```

### crates/validator/src/config.rs
```diff
@@ -9,39 +9,86 @@
 
 use anyhow::Result;
 use clap::{Parser, ValueEnum};
+use std::collections::HashMap;
 use std::net::SocketAddr;
 use std::path::PathBuf;
+use tracing::info;
 
 use crate::engine::machine::JitProcessManager;
 use crate::engine::machine_locator::MachineLocator;
+use crate::engine::{replay_binary, ModuleRoot, DEFAULT_JIT_CRANELIFT};
+
+/// Mode-specific execution state, built at startup.
+pub enum ExecutionMode {
+    Native {
+        module_cache: HashMap<ModuleRoot, CompiledModule>,
+    },
+    Continuous {
+        // Not wrapped in Arc<> since the caller of ServerState is already wrapped.
+        jit_manager: JitProcessManager,
+    },
+}
 
-#[derive(Debug)]
 pub struct ServerState {
-    pub mode: InputMode,
     /// Machine locator is responsible for locating replay.wasm binary and building
     /// a map of module roots to their respective location + binary
     pub locator: MachineLocator,
-    /// Jit manager is responsible for computing next GlobalState. Not wrapped
-    /// in Arc<> since the caller of ServerState is wrapped in Arc<>.
-    pub jit_manager: JitProcessManager,
     pub available_workers: usize,
+    pub execution: ExecutionMode,
 }
 
 impl ServerState {
     pub fn new(config: &ServerConfig, available_workers: usize) -> Result<Self> {
         let locator = MachineLocator::new(&config.root_path)?;
 
-        let jit_manager = match config.mode {
-            InputMode::Continuous => JitProcessManager::new(&locator)?,
-            InputMode::Native => JitProcessManager::new_empty(),
+        let execution = match config.mode {
+            InputMode::Continuous => ExecutionMode::Continuous {
+                jit_manager: JitProcessManager::new(&locator)?,
+            },
+            InputMode::Native => {
+                let mut module_cache = HashMap::new();
+                for meta in locator.module_roots() {
+                    let binary = replay_binary(&meta.path);
+                    let validator_opts = jit::ValidatorOpts {
+                        binary: binary.clone(),
+                        cranelift: DEFAULT_JIT_CRANELIFT,
+                        debug: false,
+                        require_success: false,
+                    };
+                    match jit::machine::compile_module(&validator_opts) {
+                        Ok(compiled) => {
+                            info!(
+                                "Pre-compiled module for root 0x{} from {binary:?}",
+                                meta.module_root
+                            );
+                            module_cache.insert(meta.module_root, compiled);
+                        }
+                        Err(err) => {
+                            warn!(
+                                "Failed to pre-compile module for root 0x{}: {err}",
+                                meta.module_root
+                            );
+                        }
+                    }
+                }
+                ExecutionMode::Native { module_cache }
+            }
         };
+
         Ok(ServerState {
-            mode: config.mode,
             locator,
-            jit_manager,
             available_workers,
+            execution,
         })
     }
+
+    /// Gracefully shuts down mode-specific resources.
+    pub async fn shutdown(&self) -> Result<()> {
+        match &self.execution {
+            ExecutionMode::Continuous { jit_manager } => jit_manager.complete_machines().await,
+            ExecutionMode::Native { .. } => Ok(()),
+        }
+    }
 }
 
 #[derive(Copy, Clone, Debug, ValueEnum)]
@@ -56,6 +103,7 @@ pub enum LoggingFormat {
     Text,
     Json,
 }
+use jit::CompiledModule;
 use tracing::warn;
 
 const DEFAULT_NUM_WORKERS: usize = 4;
```

### crates/validator/src/engine/execution.rs
```diff
@@ -16,18 +16,24 @@
 //!    validation, isolating the execution environment and allowing for specific
 //!    binary version targeting.
 
+use std::collections::HashMap;
+
 use axum::Json;
+use jit::CompiledModule;
 use tracing::info;
 use validation::{local_target, BatchInfo, GoGlobalState};
 
 use crate::{
-    config::ServerState,
-    engine::{replay_binary, DEFAULT_JIT_CRANELIFT},
+    engine::{
+        machine::JitProcessManager, machine_locator::MachineLocator, replay_binary, ModuleRoot,
+        DEFAULT_JIT_CRANELIFT,
+    },
     spawner_endpoints::ValidationRequest,
 };
 
 pub async fn validate_native(
-    server_state: &ServerState,
+    locator: &MachineLocator,
+    module_cache: &HashMap<ModuleRoot, CompiledModule>,
     request: ValidationRequest,
 ) -> Result<Json<GoGlobalState>, String> {
     let delayed_inbox = match request.validation_input.has_delayed_msg {
@@ -38,21 +44,17 @@ pub async fn validate_native(
         false => vec![],
     };
 
-    let binary_path = if let Some(module_root) = request.module_root {
-        server_state.locator.get_machine_path(module_root)?
-    } else {
-        server_state
-            .locator
-            .latest_wasm_module_root()
-            .path
-            .to_path_buf()
-    };
-    let binary = replay_binary(binary_path);
-    info!("validate native serving request with module root at {binary:?}");
+    let module_root = request
+        .module_root
+        .unwrap_or(locator.latest_wasm_module_root().module_root);
+
+    let binary_path = locator.get_machine_path(module_root)?;
+    let binary = replay_binary(&binary_path);
+    info!("validate native serving request with module root 0x{module_root}");
 
     let opts = jit::Opts {
         validator: jit::ValidatorOpts {
-            binary,
+            binary: binary.clone(),
             cranelift: DEFAULT_JIT_CRANELIFT,
             debug: false, // JIT's debug messages are using printlns, which would clutter the server logs
             require_success: false, // Relevant for JIT binary only.
@@ -66,7 +68,13 @@ pub async fn validate_native(
         }),
     };
 
-    let result = jit::run(&opts).map_err(|error| format!("{error}"))?;
+    let result = match module_cache.get(&module_root) {
+        Some(compiled) => {
+            jit::run_with_module(compiled, &opts).map_err(|error| format!("{error}"))?
+        }
+        None => return Err(format!("module root 0x{module_root} not in cache")),
+    };
+
     if let Some(err) = result.error {
         Err(format!("{err}"))
     } else {
@@ -75,17 +83,17 @@ pub async fn validate_native(
 }
 
 pub async fn validate_continuous(
-    server_state: &ServerState,
+    locator: &MachineLocator,
+    jit_manager: &JitProcessManager,
     request: ValidationRequest,
 ) -> Result<Json<GoGlobalState>, String> {
     let module_root = request
         .module_root
-        .unwrap_or_else(|| server_state.locator.latest_wasm_module_root().module_root);
+        .unwrap_or_else(|| locator.latest_wasm_module_root().module_root);
 
     info!("validate continuous serving request with module_root 0x{module_root}");
 
-    let new_state = server_state
-        .jit_manager
+    let new_state = jit_manager
         .feed_machine_with_root(&request.validation_input, module_root)
         .await
         .map_err(|error| format!("{error:?}"))?;
```

### crates/validator/src/engine/machine.rs
```diff
@@ -135,21 +135,13 @@ pub struct JitProcessManager {
 }
 
 impl JitProcessManager {
-    pub fn new_empty() -> Self {
-        Self {
-            wasm_memory_usage_limit: DEFAULT_WASM_MEMORY_USAGE_LIMIT,
-            machines: RwLock::new(HashMap::new()),
-            shutting_down: AtomicBool::new(false),
-        }
-    }
-
     pub fn new(locator: &MachineLocator) -> Result<Self> {
         let machines: HashMap<ModuleRoot, Arc<JitMachine>> = locator
             .module_roots()
             .iter()
             .cloned()
             .map(|root_meta| {
-                let root_path = replay_binary(root_meta.path);
+                let root_path = replay_binary(&root_meta.path);
                 let sub_machine = create_jit_machine(DEFAULT_JIT_CRANELIFT, &root_path)?;
                 Ok::<(ModuleRoot, Arc<JitMachine>), anyhow::Error>((
                     root_meta.module_root,
```

### crates/validator/src/engine/mod.rs
```diff
@@ -1,7 +1,7 @@
 // Copyright 2025-2026, Offchain Labs, Inc.
 // For license information, see https://github.com/OffchainLabs/nitro/blob/master/LICENSE.md
 
-use std::path::PathBuf;
+use std::path::{Path, PathBuf};
 
 use arbutil::Bytes32;
 
@@ -15,6 +15,6 @@ const REPLAY_WASM: &str = "replay.wasm";
 
 pub type ModuleRoot = Bytes32;
 
-pub fn replay_binary(binary_path: PathBuf) -> PathBuf {
+pub fn replay_binary(binary_path: &Path) -> PathBuf {
     binary_path.join(REPLAY_WASM)
 }
```

### crates/validator/src/server.rs
```diff
@@ -25,7 +25,7 @@ async fn run_server_internal(
 
     info!("Shutdown signal received. Running cleanup...");
 
-    state.jit_manager.complete_machines().await
+    state.shutdown().await
 }
 
 // Listens for Ctrl+C or SIGTERM
@@ -72,7 +72,7 @@ mod tests {
     };
 
     use crate::{
-        config::{ServerConfig, ServerState},
+        config::{ExecutionMode, ServerConfig, ServerState},
         engine::ModuleRoot,
         server::run_server_internal,
     };
@@ -138,11 +138,10 @@ mod tests {
         assert!(result.is_ok(), "Server should exit successfully");
 
         // 8. Verify jit_manager Cleanup
-        let machine_arc = {
-            let machines = test_config.state.jit_manager.machines.read().await;
-            machines.get(&module_root).cloned()
-        };
-        assert!(machine_arc.is_none());
+        if let ExecutionMode::Continuous { jit_manager } = &test_config.state.execution {
+            let machines = jit_manager.machines.read().await;
+            assert!(machines.get(&module_root).is_none());
+        }
 
         // 9. Verify same request from above fails expectadly
         let resp = client
```

### crates/validator/src/spawner_endpoints.rs
```diff
@@ -7,9 +7,10 @@
 //! package. Their serialization is configured to match the Go side (by using `PascalCase` for
 //! field names).
 
+use crate::config::ExecutionMode;
 use crate::engine::execution::{validate_continuous, validate_native};
 use crate::engine::ModuleRoot;
-use crate::{config::InputMode, ServerState};
+use crate::ServerState;
 use axum::extract::State;
 use axum::response::IntoResponse;
 use axum::Json;
@@ -105,9 +106,13 @@ pub async fn validate(
         module_root,
     };
 
-    let result = match state.mode {
-        InputMode::Native => validate_native(&state, request).await,
-        InputMode::Continuous => validate_continuous(&state, request).await,
+    let result = match &state.execution {
+        ExecutionMode::Native { module_cache } => {
+            validate_native(&state.locator, module_cache, request).await
+        }
+        ExecutionMode::Continuous { jit_manager } => {
+            validate_continuous(&state.locator, jit_manager, request).await
+        }
     };
 
     match result {
```
