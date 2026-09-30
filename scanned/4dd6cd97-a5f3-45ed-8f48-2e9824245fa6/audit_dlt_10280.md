# [?] fix: Fix for cost unit limit panic

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2022-09-13
Source: https://github.com/radixdlt/babylon-node/commit/f652668c336417dc954fe4781b469e0c15e70870
Type: security-commit

## Details
fix: Fix for cost unit limit panic

## Patch
### core-rust/Cargo.lock
```diff
@@ -960,7 +960,7 @@ dependencies = [
 [[package]]
 name = "radix-engine"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "colored",
  "hex",
@@ -977,7 +977,7 @@ dependencies = [
 [[package]]
 name = "radix-engine-stores"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "radix-engine",
  "rocksdb",
@@ -1075,7 +1075,7 @@ dependencies = [
 [[package]]
 name = "sbor"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "hex",
  "sbor-derive",
@@ -1085,7 +1085,7 @@ dependencies = [
 [[package]]
 name = "sbor-derive"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -1096,7 +1096,7 @@ dependencies = [
 [[package]]
 name = "scrypto"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "bech32",
  "forward_ref",
@@ -1115,7 +1115,7 @@ dependencies = [
 [[package]]
 name = "scrypto-abi"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "sbor",
  "serde",
@@ -1124,7 +1124,7 @@ dependencies = [
 [[package]]
 name = "scrypto-derive"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -1440,7 +1440,7 @@ dependencies = [
 [[package]]
 name = "transaction"
 version = "0.6.0"
-source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-efb1c2c0#efb1c2c01d0d62be9d335c1a6058eca65dd3123d"
+source = "git+https://github.com/radixdlt/radixdlt-scrypto?tag=alphanet-74234f74#74234f74731d334d295d1dff48c006da5c79c46a"
 dependencies = [
  "clap",
  "ed25519-dalek",
```

### core-rust/core-api-server/Cargo.toml
```diff
@@ -22,11 +22,11 @@ state-manager = { path = "../state-manager" }
 # 
 # Ensure this version is also identically updated in ../state-manager/Cargo.toml
 #
-sbor = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-scrypto = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-transaction = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-radix-engine = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-radix-engine-stores = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
+sbor = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+scrypto = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+transaction = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+radix-engine = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+radix-engine-stores = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
 
 jni = "0.19.0"
 
```

### core-rust/state-manager/Cargo.toml
```diff
@@ -22,11 +22,11 @@ jni = "0.19.0"
 # 
 # Ensure this version is also identically updated in ../core-api-server/Cargo.toml
 #
-sbor = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-scrypto = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-transaction = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-radix-engine = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
-radix-engine-stores = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-efb1c2c0" }
+sbor = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+scrypto = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+transaction = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+radix-engine = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
+radix-engine-stores = { git="https://github.com/radixdlt/radixdlt-scrypto", tag="alphanet-74234f74" }
 rocksdb = { version = "0.19.0" }
 hex = { version = "0.4.3", default-features = false }
 bech32 = { version = "0.9.0", default-features = false }
```

### core-rust/state-manager/src/state_manager.rs
```diff
@@ -74,8 +74,8 @@ use radix_engine::constants::{
 use radix_engine::ledger::{QueryableSubstateStore, ReadableSubstateStore, WriteableSubstateStore};
 use radix_engine::state_manager::StagedSubstateStoreManager;
 use radix_engine::transaction::{
-    ExecutionConfig, PreviewError, PreviewExecutor, PreviewResult, TransactionExecutor,
-    TransactionResult,
+    ExecutionConfig, FeeReserveConfig, PreviewError, PreviewExecutor, PreviewResult,
+    TransactionExecutor, TransactionResult,
 };
 use radix_engine::wasm::{DefaultWasmEngine, WasmInstrumenter};
 use scrypto::engine::types::RENodeId;
@@ -102,6 +102,7 @@ pub struct StateManager<M: Mempool, S> {
     wasm_instrumenter: WasmInstrumenter,
     validation_config: OwnedValidationConfig,
     execution_config: ExecutionConfig,
+    fee_reserve_config: FeeReserveConfig,
     intent_hash_manager: TestIntentHashManager,
 }
 
@@ -119,12 +120,14 @@ impl<M: Mempool, S> StateManager<M, S> {
                 min_tip_percentage: 0,
             },
             execution_config: ExecutionConfig {
-                cost_unit_price: DEFAULT_COST_UNIT_PRICE.parse().unwrap(),
                 max_call_depth: DEFAULT_MAX_CALL_DEPTH,
-                system_loan: DEFAULT_SYSTEM_LOAN,
                 is_system: false,
                 trace: false,
             },
+            fee_reserve_config: FeeReserveConfig {
+                cost_unit_price: DEFAULT_COST_UNIT_PRICE.parse().unwrap(),
+                system_loan: DEFAULT_SYSTEM_LOAN,
+            },
             intent_hash_manager: TestIntentHashManager::new(),
         }
     }
@@ -228,7 +231,11 @@ where
                 &mut self.wasm_engine,
                 &mut self.wasm_instrumenter,
             );
-            transaction_executor.execute_and_commit(&prepared, &self.execution_config);
+            transaction_executor.execute_and_commit(
+                &prepared,
+                &self.fee_reserve_config,
+                &self.execution_config,
+            );
         }
 
         for proposed in prepare_request.proposed {
@@ -250,8 +257,11 @@ where
                         &mut self.wasm_engine,
                         &mut self.wasm_instrumenter,
                     );
-                    let receipt = transaction_executor
-                        .execute_and_commit(&validated_transaction, &self.execution_config);
+                    let receipt = transaction_executor.execute_and_commit(
+                        &validated_transaction,
+                        &self.fee_reserve_config,
+                        &self.execution_config,
+                    );
                     match receipt.result {
                         TransactionResult::Commit(..) => non_rejected_txns.push(proposed),
                         TransactionResult::Reject(reject_result) => {
@@ -285,8 +295,11 @@ where
                 &mut self.wasm_instrumenter,
             );
 
-            let engine_receipt =
-                transaction_executor.execute_and_commit(&validated_txn, &self.execution_config);
+            let engine_receipt = transaction_executor.execute_and_commit(
+                &validated_txn,
+                &self.fee_reserve_config,
+                &self.execution_config,
+            );
 
             let ledger_receipt: LedgerTransactionReceipt =
                 engine_receipt.try_into().unwrap_or_else(|_| {
```
