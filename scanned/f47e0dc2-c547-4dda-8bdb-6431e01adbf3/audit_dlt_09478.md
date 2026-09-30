# [?] Merge pull request #5241 from mpapierski/core-68-fix-code-not-found-error-panic

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2025-05-29
Source: https://github.com/casper-network/casper-node/commit/23b58e60e4a9d3bc7462ed9a27e6d2f00630888e
Type: security-commit

## Details
Merge pull request #5241 from mpapierski/core-68-fix-code-not-found-error-panic

CORE-68: Fix code not found error panic

## Patch
### Cargo.lock
```diff
@@ -882,6 +882,7 @@ dependencies = [
 name = "casper-executor-wasm"
 version = "0.1.2"
 dependencies = [
+ "base16",
  "blake2 0.10.6",
  "borsh",
  "bytes",
@@ -893,7 +894,6 @@ dependencies = [
  "casper-storage",
  "casper-types",
  "digest 0.10.7",
- "either",
  "fs_extra",
  "itertools 0.14.0",
  "once_cell",
```

### binary_port/src/error_code.rs
```diff
@@ -370,6 +370,8 @@ pub enum ErrorCode {
     InvalidDelegationAmount = 116,
     #[error("Calling a stored contract by targeting it's `version` is not supported")]
     TargetingPackageVersionNotSupported = 117,
+    #[error("the transaction invocation target is unsupported under V2 runtime")]
+    UnsupportedInvocationTarget = 118,
 }
 
 impl TryFrom<u16> for ErrorCode {
@@ -574,6 +576,9 @@ impl From<InvalidTransactionV1> for ErrorCode {
             InvalidTransactionV1::TargetingPackageVersionNotSupported => {
                 ErrorCode::TargetingPackageVersionNotSupported
             }
+            InvalidTransactionV1::UnsupportedInvocationTarget { .. } => {
+                ErrorCode::UnsupportedInvocationTarget
+            }
             _other => ErrorCode::InvalidTransactionUnspecified,
         }
     }
@@ -594,12 +599,12 @@ mod tests {
             assert_ne!(
                 code,
                 ErrorCode::InvalidTransactionUnspecified,
-                "Seems like InvalidTransactionV1 {error} has no corresponding error code"
+                "Seems like InvalidTransactionV1 {error:?} has no corresponding error code"
             );
             assert_ne!(
                 code,
                 ErrorCode::InvalidDeployUnspecified,
-                "Seems like InvalidTransactionV1 {error} has no corresponding error code"
+                "Seems like InvalidTransactionV1 {error:?} has no corresponding error code"
             )
         }
     }
```

### executor/wasm/Cargo.toml
```diff
@@ -22,11 +22,10 @@ casper-execution-engine = { version = "8.1.0", path = "../../execution_engine",
     "test-support",
 ] }
 digest = "0.10.7"
-either = "1.10"
 parking_lot = "0.12.1"
 thiserror = "2.0"
 tracing = "0.1.40"
-
+base16 = "0.2.1"
 
 [dev-dependencies]
 tempfile = "3.10.1"
```

### executor/wasm/src/lib.rs
```diff
@@ -41,7 +41,6 @@ use casper_types::{
     MessageLimits, Package, PackageHash, PackageStatus, Phase, ProtocolVersion, StorageCosts,
     StoredValue, TransactionInvocationTarget, URef, WasmV2Config, U512,
 };
-use either::Either;
 use install::{InstallContractError, InstallContractRequest, InstallContractResult};
 use parking_lot::RwLock;
 use system::{MintArgs, MintTransferArgs};
@@ -201,14 +200,13 @@ impl ExecutorV2 {
         );
 
         let protocol_version = ProtocolVersion::V2_0_0;
-
         let protocol_version_major = protocol_version.value().major;
+
         let next_version = smart_contract.next_entity_version_for(protocol_version_major);
-        let entity_hash =
-            chain_utils::compute_next_contract_hash_version(smart_contract_addr, next_version);
+
         let entity_version_key = smart_contract.insert_entity_version(
             protocol_version_major,
-            EntityAddr::SmartContract(entity_hash),
+            EntityAddr::SmartContract(smart_contract_addr),
         );
         debug_assert_eq!(entity_version_key.entity_version(), next_version);
 
@@ -235,7 +233,8 @@ impl ExecutorV2 {
         );
 
         // 3. Store addressable entity
-        let addressable_entity_key = Key::AddressableEntity(EntityAddr::SmartContract(entity_hash));
+        let addressable_entity_key =
+            Key::AddressableEntity(EntityAddr::SmartContract(smart_contract_addr));
 
         // TODO: abort(str) as an alternative to trap
         let main_purse: URef = match system::mint_mint(
@@ -316,9 +315,9 @@ impl ExecutorV2 {
 
                         gas_usage
                     }
-                    Err(error) => {
-                        error!(%error, "unable to execute constructor");
-                        return Err(InstallContractError::Execute(error));
+                    Err(execute_error) => {
+                        error!(%execute_error, "unable to execute constructor");
+                        return Err(InstallContractError::Execute(execute_error));
                     }
                 }
             }
@@ -367,10 +366,10 @@ impl ExecutorV2 {
         // supported. let caller_entity_addr = EntityAddr::new_account(caller);
         let source_purse = get_purse_for_entity(&mut tracking_copy, caller_key);
 
-        let (wasm_bytes, export_or_selector): (_, Either<&str, u32>) = match &execution_kind {
+        let (wasm_bytes, export_name) = match &execution_kind {
             ExecutionKind::SessionBytes(wasm_bytes) => {
                 // self.execute_wasm(tracking_copy, address, gas_limit, wasm_bytes, input)
-                (wasm_bytes.clone(), Either::Left(DEFAULT_WASM_ENTRY_POINT))
+                (wasm_bytes.clone(), DEFAULT_WASM_ENTRY_POINT)
             }
             ExecutionKind::Stored {
                 address: smart_contract_addr,
@@ -383,19 +382,14 @@ impl ExecutorV2 {
                     .read_first(&[&legacy_key, &smart_contract_key])
                     .expect("should read contract");
 
-                // let entity_addr: EntityAddr;
-
-                // Resolve indirection - get the latest version from the smart contract package
-                // versions. let old_contract = contract.clone();
-                // let latest_version_key;
                 if let Some(StoredValue::SmartContract(smart_contract_package)) = &contract {
                     let contract_hash = smart_contract_package
                         .versions()
                         .latest()
                         .expect("should have last entry");
                     let entity_addr = EntityAddr::SmartContract(contract_hash.value());
                     let latest_version_key = Key::AddressableEntity(entity_addr);
-                    assert_ne!(&entity_addr.value(), smart_contract_addr);
+                    assert_eq!(&entity_addr.value(), smart_contract_addr);
                     let new_contract = tracking_copy
                         .read(&latest_version_key)
                         .expect("should read latest version");
@@ -491,7 +485,7 @@ impl ExecutorV2 {
                             }
                         }
 
-                        (Bytes::from(wasm_bytes), Either::Left(entry_point.as_str()))
+                        (Bytes::from(wasm_bytes), entry_point.as_str())
                     }
                     Some(StoredValue::Contract(_legacy_contract)) => {
                         let block_info = BlockInfo::new(
@@ -522,7 +516,12 @@ impl ExecutorV2 {
                         );
                     }
                     None => {
-                        panic!("No code found in {smart_contract_key:?}");
+                        error!(
+                            smart_contract_addr = base16::encode_lower(&smart_contract_addr),
+                            ?execution_kind,
+                            "No contract code found",
+                        );
+                        return Err(ExecuteError::CodeNotFound(*smart_contract_addr));
                     }
                 }
             }
@@ -566,11 +565,7 @@ impl ExecutorV2 {
         let mut instance = vm.instantiate(wasm_bytes, context, wasm_instance_config)?;
 
         self.push_execution_stack(execution_kind.clone());
-        let (vm_result, gas_usage) = match export_or_selector {
-            Either::Left(export_name) => instance.call_export(export_name),
-            Either::Right(_entry_point) => todo!("Restore selectors"), /* instance.call_export(&
-                                                                        * entry_point), */
-        };
+        let (vm_result, gas_usage) = instance.call_export(export_name);
 
         let top_execution_kind = self
             .pop_execution_stack()
@@ -644,16 +639,23 @@ impl ExecutorV2 {
                     messages: initial_tracking_copy.messages(),
                 })
             }
-            Err(VMError::Internal(host_error)) => {
-                error!(?host_error, "host error");
-                Ok(ExecuteResult {
-                    host_error: Some(CallError::InternalHost),
-                    output: None,
-                    gas_usage,
-                    effects: initial_tracking_copy.effects(),
-                    cache: initial_tracking_copy.cache(),
-                    messages: initial_tracking_copy.messages(),
-                })
+            Err(VMError::Execute(execute_error)) => {
+                let effects = initial_tracking_copy.effects();
+                let cache = initial_tracking_copy.cache();
+                let messages = initial_tracking_copy.messages();
+                error!(
+                    ?execute_error,
+                    ?gas_usage,
+                    ?effects,
+                    ?cache,
+                    ?messages,
+                    "host error"
+                );
+                Err(execute_error)
+            }
+            Err(VMError::Internal(internal_error)) => {
+                error!(?internal_error, "internal host error");
+                Err(ExecuteError::InternalHost(internal_error))
             }
         }
     }
```

### executor/wasm/tests/integration.rs
```diff
@@ -16,7 +16,8 @@ use casper_executor_wasm::{
 };
 use casper_executor_wasm_common::error::CallError;
 use casper_executor_wasm_interface::executor::{
-    ExecuteRequest, ExecuteRequestBuilder, ExecuteWithProviderResult, ExecutionKind,
+    ExecuteError, ExecuteRequest, ExecuteRequestBuilder, ExecuteWithProviderError,
+    ExecuteWithProviderResult, ExecutionKind,
 };
 use casper_storage::{
     data_access_layer::{
@@ -987,3 +988,31 @@ fn write_n_bytes_at_limit(
 //         _ => false,
 //     }));
 // }
+
+#[test]
+fn non_existing_smart_contract_does_not_panic() {
+    let address_generator = make_address_generator();
+    let executor = make_executor();
+    let (mut global_state, state_root_hash, _tempdir) = make_global_state_with_genesis();
+
+    let non_existing_address = [255; 32];
+    let execute_request = base_execute_builder()
+        .with_target(ExecutionKind::Stored {
+            address: non_existing_address,
+            entry_point: "non_existing".to_string(),
+        })
+        .with_input(Bytes::new())
+        .with_gas_limit(DEFAULT_GAS_LIMIT)
+        .with_transferred_value(0)
+        .with_shared_address_generator(Arc::clone(&address_generator))
+        .build()
+        .expect("should build");
+
+    let result = executor
+        .execute_with_provider(state_root_hash, &mut global_state, execute_request)
+        .expect_err("Failure");
+
+    assert!(matches!(
+        result,
+        ExecuteWithProviderError::Execute(execute_error) if matches!(execute_error, ExecuteError::CodeNotFound(address) if address == non_existing_address)));
+}
```

### executor/wasm_common/src/chain_utils.rs
```diff
@@ -30,19 +30,6 @@ pub fn compute_wasm_bytecode_hash<T: AsRef<[u8]>>(wasm_bytes: T) -> [u8; 32] {
     hash.into()
 }
 
-#[must_use]
-pub fn compute_next_contract_hash_version(
-    smart_contract_addr: [u8; 32],
-    next_version: u32,
-) -> [u8; 32] {
-    let mut hasher = Blake2b::<U32>::new();
-
-    hasher.update(smart_contract_addr);
-    hasher.update(next_version.to_le_bytes());
-
-    hasher.finalize().into()
-}
-
 #[cfg(test)]
 mod tests {
     const SEED: [u8; 32] = [1u8; 32];
@@ -58,16 +45,4 @@ mod tests {
             super::compute_predictable_address("mainnet", initiator, bytecode_hash, Some(SEED));
         assert_ne!(predictable_address_1, predictable_address_2);
     }
-
-    #[test]
-    fn test_compute_nth_version_hash() {
-        let smart_contract_addr = [1u8; 32];
-        let mut next_version = 1;
-
-        let hash_1 = super::compute_next_contract_hash_version(smart_contract_addr, next_version);
-        next_version += 1;
-
-        let hash_2 = super::compute_next_contract_hash_version(smart_contract_addr, next_version);
-        assert_ne!(hash_1, hash_2);
-    }
 }
```

### executor/wasm_common/src/error.rs
```diff
@@ -127,9 +127,6 @@ pub enum CallError {
     /// Called contract is not callable.
     #[error("not callable")]
     NotCallable,
-    /// Encountered a host function error.
-    #[error("internal host")]
-    InternalHost,
 }
 
 impl CallError {
@@ -141,7 +138,6 @@ impl CallError {
             Self::CalleeTrapped(_) => CALLEE_TRAPPED,
             Self::CalleeGasDepleted => CALLEE_GAS_DEPLETED,
             Self::NotCallable => CALLEE_NOT_CALLABLE,
-            Self::InternalHost => CALLEE_HOST_ERROR,
         }
     }
 }
```

### executor/wasm_common/src/keyspace.rs
```diff
@@ -24,7 +24,7 @@ pub enum Keyspace<'a> {
     ///
     /// There's no additional payload for this variant as the host implies the contract's address.
     State,
-    /// Stores contract's context date. Bytes can be any value as long as it uniquely identifies a
+    /// Stores contract's context data. Bytes can be any value as long as it uniquely identifies a
     /// value.
     Context(&'a [u8]),
     /// Stores contract's named keys.
```

### executor/wasm_host/src/host.rs
```diff
@@ -18,7 +18,7 @@ use casper_executor_wasm_common::{
     keyspace::{Keyspace, KeyspaceTag},
 };
 use casper_executor_wasm_interface::{
-    executor::{ExecuteError, ExecuteRequestBuilder, ExecuteResult, ExecutionKind, Executor},
+    executor::{ExecuteRequestBuilder, ExecuteResult, ExecutionKind, Executor},
     u32_from_host_result, Caller, InternalHostError, VMError, VMResult,
 };
 use casper_storage::{
@@ -465,8 +465,8 @@ fn keyspace_to_global_state_key<S: GlobalStateReader, E: Executor>(
 
     match keyspace {
         Keyspace::State => Some(Key::State(entity_addr)),
-        Keyspace::Context(payload) => {
-            let digest = Digest::hash(payload);
+        Keyspace::Context(bytes) => {
+            let digest = Digest::hash(bytes);
             Some(casper_types::Key::NamedKey(
                 NamedKeyAddr::new_named_key_entry(entity_addr, digest.value()),
             ))
@@ -651,9 +651,7 @@ pub fn casper_create<S: GlobalStateReader + 'static, E: Executor + 'static>(
     let mut smart_contract_package = Package::default();
 
     let protocol_version = ProtocolVersion::V2_0_0;
-
-    let first_version =
-        smart_contract_package.next_entity_version_for(protocol_version.value().major);
+    let protocol_version_major = protocol_version.value().major;
 
     let callee_addr = context_to_entity_addr(caller.context()).value();
 
@@ -664,12 +662,9 @@ pub fn casper_create<S: GlobalStateReader + 'static, E: Executor + 'static>(
         seed,
     );
 
-    let contract_hash =
-        chain_utils::compute_next_contract_hash_version(smart_contract_addr, first_version);
-
     smart_contract_package.insert_entity_version(
-        protocol_version.value().major,
-        EntityAddr::SmartContract(contract_hash),
+        protocol_version_major,
+        EntityAddr::SmartContract(smart_contract_addr),
     );
 
     if caller
@@ -697,7 +692,7 @@ pub fn casper_create<S: GlobalStateReader + 'static, E: Executor + 'static>(
 
     // 3. Store addressable entity
 
-    let entity_addr = EntityAddr::SmartContract(contract_hash);
+    let entity_addr = EntityAddr::SmartContract(smart_contract_addr);
     let addressable_entity_key = Key::AddressableEntity(entity_addr);
 
     // TODO: abort(str) as an alternative to trap
@@ -748,7 +743,7 @@ pub fn casper_create<S: GlobalStateReader + 'static, E: Executor + 'static>(
                 .with_gas_limit(gas_limit)
                 .with_target(ExecutionKind::Stored {
                     address: smart_contract_addr,
-                    entry_point: entry_point_name,
+                    entry_point: entry_point_name.clone(),
                 })
                 .with_input(input_data.unwrap_or_default())
                 .with_transferred_value(transferred_value)
@@ -793,10 +788,11 @@ pub fn casper_create<S: GlobalStateReader + 'static, E: Executor + 'static>(
 
                     output
                 }
-                Err(ExecuteError::WasmPreparation(_preparation_error)) => {
+                Err(execute_error) => {
                     // This is a bug in the EE, as it should have been caught during the preparation
                     // phase when the contract was stored in the global state.
-                    todo!()
+                    error!(?execute_error, "Failed to execute constructor entry point");
+                    return Err(VMError::Execute(execute_error));
                 }
             }
         }
@@ -890,7 +886,7 @@ pub fn casper_call<S: GlobalStateReader + 'static, E: Executor + 'static>(
         .with_gas_limit(gas_limit)
         .with_target(ExecutionKind::Stored {
             address: smart_contract_addr,
-            entry_point,
+            entry_point: entry_point.clone(),
         })
         .with_transferred_value(transferred_value)
         .with_input(input_data)
@@ -945,10 +941,14 @@ pub fn casper_call<S: GlobalStateReader + 'static, E: Executor + 'static>(
 
             (gas_usage, host_result)
         }
-        Err(ExecuteError::WasmPreparation(preparation_error)) => {
-            // This is a bug in the EE, as it should have been caught during the preparation phase
-            // when the contract was stored in the global state.
-            unreachable!("Preparation error: {:?}", preparation_error)
+        Err(execute_error) => {
+            error!(
+                ?execute_error,
+                ?smart_contract_addr,
+                ?entry_point,
+                "Failed to execute entry point"
+            );
+            return Err(VMError::Execute(execute_error));
         }
     };
 
@@ -1445,13 +1445,17 @@ pub fn casper_upgrade<S: GlobalStateReader + 'static, E: Executor>(
                     );
                 }
             }
-            Err(ExecuteError::WasmPreparation(preparation_error)) => {
-                // Unable to call contract because the wasm is broken.
+            Err(execute_error) => {
+                // Unable to call contract because of execution error or internal host error.
+                // This usually means an internal error that should not happen and has to be handled
+                // by the contract runtime.
                 error!(
-                    ?preparation_error,
-                    "Wasm preparation error while performing upgrade"
+                    ?execute_error,
+                    ?entry_point_name,
+                    smart_contract_addr = base16::encode_lower(&smart_contract_addr),
+                    "Failed to execute upgrade entry point"
                 );
-                return Ok(CALLEE_NOT_CALLABLE);
+                return Err(VMError::Execute(execute_error));
             }
         }
     }
```

### executor/wasm_interface/src/executor.rs
```diff
@@ -14,7 +14,7 @@ use casper_types::{
 use parking_lot::RwLock;
 use thiserror::Error;
 
-use crate::{CallError, GasUsage, WasmPreparationError};
+use crate::{CallError, GasUsage, InternalHostError, WasmPreparationError};
 
 /// Request to execute a Wasm contract.
 pub struct ExecuteRequest {
@@ -349,6 +349,11 @@ pub enum ExecuteError {
     /// No wasm was executed at this point.
     #[error("Wasm error error: {0}")]
     WasmPreparation(#[from] WasmPreparationError),
+    /// Error while executing Wasm: traps, memory access errors, etc.
+    #[error("Internal host error: {0}")]
+    InternalHost(#[from] InternalHostError),
+    #[error("Code not found")]
+    CodeNotFound(HashAddr),
 }
 
 #[derive(Debug, Error)]
```

### executor/wasm_interface/src/lib.rs
```diff
@@ -1,6 +1,7 @@
 pub mod executor;
 
 use bytes::Bytes;
+use executor::ExecuteError;
 use thiserror::Error;
 
 use casper_executor_wasm_common::{
@@ -109,14 +110,16 @@ pub enum VMError {
     Export(ExportError),
     #[error("Out of gas")]
     OutOfGas,
-    #[error("Internal host error")]
-    Internal(InternalHostError),
     /// Error while executing Wasm: traps, memory access errors, etc.
     ///
     /// NOTE: for supporting multiple different backends we may want to abstract this a bit and
     /// extract memory access errors, trap codes, and unify error reporting.
     #[error("Trap: {0}")]
     Trap(TrapCode),
+    #[error("Internal host error")]
+    Internal(#[from] InternalHostError),
+    #[error("Execute error: {0}")]
+    Execute(#[from] ExecuteError),
 }
 
 impl VMError {
@@ -132,12 +135,6 @@ impl VMError {
 /// Result of a VM operation.
 pub type VMResult<T> = Result<T, VMError>;
 
-impl From<InternalHostError> for VMError {
-    fn from(value: InternalHostError) -> Self {
-        Self::Internal(value)
-    }
-}
-
 /// Configuration for the Wasm engine.
 #[derive(Clone, Debug)]
 pub struct Config {
```

### executor/wasmer_backend/src/middleware/gas_metering.rs
```diff
@@ -189,7 +189,17 @@ fn cycles(operator: &Operator) -> u64 {
         Operator::I64Store32 { .. } => 1,
         Operator::MemorySize { .. } => 31,
         Operator::MemoryGrow { .. } => 67,
-        Operator::MemoryCopy { .. } => 31,
+
+
+        Operator::MemoryInit { .. }
+        | Operator::DataDrop { .. }
+        | Operator::MemoryCopy { ..}
+        | Operator::MemoryFill { .. }
+        | Operator::TableInit { .. }
+        | Operator::ElemDrop { .. }
+        | Operator::TableCopy { .. } => 31, // memory.copy has cycle count of 31, rest needs benchmark validation (bulk memory extension)
+
+
         Operator::Select => 14,
         Operator::If { .. } => 1,
         Operator::Call { .. } => 17,
@@ -207,7 +217,7 @@ fn cycles(operator: &Operator) -> u64 {
         | Operator::Catch { .. }
         | Operator::Rethrow { .. }
         | Operator::Delegate { .. }
-        | Operator::CatchAll => todo!("{operator:?}"),
+        | Operator::CatchAll => todo!("try/catch operators are not metered yet; gatekeeper config should not enable this extension"),
         Operator::End
         | Operator::Return
         | Operator::ReturnCall { .. }
@@ -248,12 +258,6 @@ fn cycles(operator: &Operator) -> u64 {
         | Operator::RefI31
         | Operator::I31GetS
         | Operator::I31GetU
-        | Operator::MemoryInit { .. }
-        | Operator::DataDrop { .. }
-        | Operator::MemoryFill { .. }
-        | Operator::TableInit { .. }
-        | Operator::ElemDrop { .. }
-        | Operator::TableCopy { .. }
         | Operator::TableFill { .. }
         | Operator::TableSet { .. }
         | Operator::TableGrow { .. }
@@ -621,7 +625,7 @@ fn cycles(operator: &Operator) -> u64 {
         | Operator::ArrayAtomicRmwXor { .. }
         | Operator::ArrayAtomicRmwXchg { .. }
         | Operator::ArrayAtomicRmwCmpxchg { .. }
-        | Operator::RefI31Shared => todo!(),
+        | Operator::RefI31Shared => todo!("{operator:?}"),
     }
 }
 
```
