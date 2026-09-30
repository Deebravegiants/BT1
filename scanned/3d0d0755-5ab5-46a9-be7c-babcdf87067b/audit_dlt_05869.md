# [?] fix(api): Fix panic applying nonce override (#3748)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2025-03-24
Source: https://github.com/matter-labs/zksync-era/commit/944059b0cb2911debc3253a3066c4ce855b5196b
Type: security-commit

## Details
fix(api): Fix panic applying nonce override (#3748)

## What ❔

- Refactors state override application in the API server.
- Adds metrics related to state overrides.

## Why ❔

Currently, `eth_call` / `eth_estimateGas` will panic if a nonce override
is supplied. This is because in this case, storage is read using
blocking `ReadStorage` trait in the non-blocking context.

## Is this a breaking change?

- [ ] Yes
- [x] No

## Operational changes

No operational changes.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

## Patch
### core/lib/state/src/postgres/mod.rs
```diff
@@ -493,7 +493,7 @@ impl<'a> PostgresStorage<'a> {
         mut connection: Connection<'a, Core>,
         block_number: L2BlockNumber,
         consider_new_l1_batch: bool,
-    ) -> anyhow::Result<PostgresStorage<'a>> {
+    ) -> anyhow::Result<Self> {
         let resolved = connection
             .storage_web3_dal()
             .resolve_l1_batch_number_of_l2_block(block_number)
@@ -536,6 +536,11 @@ impl<'a> PostgresStorage<'a> {
     fn values_cache(&self) -> Option<&ValuesCache> {
         Some(&self.caches.as_ref()?.values.as_ref()?.cache)
     }
+
+    /// Returns the wrapped connection.
+    pub fn into_inner(self) -> Connection<'a, Core> {
+        self.connection
+    }
 }
 
 impl ReadStorage for PostgresStorage<'_> {
```

### core/lib/types/src/api/state_override.rs
```diff
@@ -1,4 +1,4 @@
-use std::collections::HashMap;
+use std::collections::{hash_map, HashMap};
 
 use serde::{de, Deserialize, Deserializer, Serialize, Serializer};
 use zksync_basic_types::{bytecode::BytecodeHash, web3::Bytes, H256, U256};
@@ -34,6 +34,15 @@ impl StateOverride {
     }
 }
 
+impl IntoIterator for StateOverride {
+    type Item = (Address, OverrideAccount);
+    type IntoIter = hash_map::IntoIter<Address, OverrideAccount>;
+
+    fn into_iter(self) -> Self::IntoIter {
+        self.0.into_iter()
+    }
+}
+
 /// Serialized bytecode representation.
 #[derive(Debug, Clone, PartialEq)]
 pub struct Bytecode(Bytes);
```

### core/lib/vm_interface/src/storage/overrides.rs
```diff
@@ -9,45 +9,53 @@ use zksync_types::{AccountTreeId, StorageKey, StorageValue, H256};
 
 use super::ReadStorage;
 
+/// Storage overrides.
+#[derive(Debug, Default)]
+pub struct StorageOverrides {
+    pub overridden_slots: HashMap<StorageKey, H256>,
+    pub overridden_factory_deps: HashMap<H256, Vec<u8>>,
+    pub empty_accounts: HashSet<AccountTreeId>,
+}
+
 /// A storage view that allows to override some of the storage values.
 #[derive(Debug)]
 pub struct StorageWithOverrides<S> {
     storage_handle: S,
-    overridden_slots: HashMap<StorageKey, H256>,
-    overridden_factory_deps: HashMap<H256, Vec<u8>>,
-    empty_accounts: HashSet<AccountTreeId>,
+    overrides: StorageOverrides,
 }
 
 impl<S: ReadStorage> StorageWithOverrides<S> {
     /// Creates a new storage view based on the underlying storage.
     pub fn new(storage: S) -> Self {
         Self {
             storage_handle: storage,
-            overridden_slots: HashMap::new(),
-            overridden_factory_deps: HashMap::new(),
-            empty_accounts: HashSet::new(),
+            overrides: StorageOverrides::default(),
         }
     }
 
     pub fn set_value(&mut self, key: StorageKey, value: StorageValue) {
-        self.overridden_slots.insert(key, value);
+        self.overrides.overridden_slots.insert(key, value);
     }
 
     pub fn store_factory_dep(&mut self, hash: H256, code: Vec<u8>) {
-        self.overridden_factory_deps.insert(hash, code);
+        self.overrides.overridden_factory_deps.insert(hash, code);
     }
 
     pub fn insert_erased_account(&mut self, account: AccountTreeId) {
-        self.empty_accounts.insert(account);
+        self.overrides.empty_accounts.insert(account);
+    }
+
+    pub fn into_parts(self) -> (S, StorageOverrides) {
+        (self.storage_handle, self.overrides)
     }
 }
 
 impl<S: ReadStorage + fmt::Debug> ReadStorage for StorageWithOverrides<S> {
     fn read_value(&mut self, key: &StorageKey) -> StorageValue {
-        if let Some(value) = self.overridden_slots.get(key) {
+        if let Some(value) = self.overrides.overridden_slots.get(key) {
             return *value;
         }
-        if self.empty_accounts.contains(key.account()) {
+        if self.overrides.empty_accounts.contains(key.account()) {
             return H256::zero();
         }
         self.storage_handle.read_value(key)
@@ -58,7 +66,8 @@ impl<S: ReadStorage + fmt::Debug> ReadStorage for StorageWithOverrides<S> {
     }
 
     fn load_factory_dep(&mut self, hash: H256) -> Option<Vec<u8>> {
-        self.overridden_factory_deps
+        self.overrides
+            .overridden_factory_deps
             .get(&hash)
             .cloned()
             .or_else(|| self.storage_handle.load_factory_dep(hash))
```

### core/node/api_server/src/execution_sandbox/execute.rs
```diff
@@ -204,8 +204,15 @@ impl SandboxExecutor {
             .prepare_env_and_storage(connection, block_args, &action)
             .await?;
 
-        let state_override = state_override.unwrap_or_default();
-        let storage = apply_state_override(storage, &state_override);
+        let storage = if let Some(state_override) = state_override {
+            tokio::task::spawn_blocking(|| apply_state_override(storage, state_override))
+                .await
+                .context("applying state override failed")?
+        } else {
+            // Do not spawn a new thread in the most frequent case.
+            StorageWithOverrides::new(storage)
+        };
+
         let (execution_args, tracing_params) = action.into_parts();
         self.engine
             .execute_in_sandbox(storage, env, execution_args, tracing_params)
```

### core/node/api_server/src/execution_sandbox/mod.rs
```diff
@@ -25,6 +25,8 @@ mod error;
 mod execute;
 mod storage;
 #[cfg(test)]
+pub(crate) mod testonly;
+#[cfg(test)]
 mod tests;
 mod validate;
 mod vm_metrics;
```

### core/node/api_server/src/execution_sandbox/storage.rs
```diff
@@ -11,43 +11,43 @@ use zksync_types::{
 /// This method is blocking.
 pub(super) fn apply_state_override<S: ReadStorage>(
     storage: S,
-    state_override: &StateOverride,
+    state_override: StateOverride,
 ) -> StorageWithOverrides<S> {
     let mut storage = StorageWithOverrides::new(storage);
-    for (account, overrides) in state_override.iter() {
+    for (account, overrides) in state_override {
         if let Some(balance) = overrides.balance {
-            let balance_key = storage_key_for_eth_balance(account);
+            let balance_key = storage_key_for_eth_balance(&account);
             storage.set_value(balance_key, u256_to_h256(balance));
         }
 
         if let Some(nonce) = overrides.nonce {
-            let nonce_key = get_nonce_key(account);
+            let nonce_key = get_nonce_key(&account);
             let full_nonce = storage.read_value(&nonce_key);
             let (_, deployment_nonce) = decompose_full_nonce(h256_to_u256(full_nonce));
             let new_full_nonce = u256_to_h256(nonces_to_full_nonce(nonce, deployment_nonce));
             storage.set_value(nonce_key, new_full_nonce);
         }
 
-        if let Some(code) = &overrides.code {
-            let code_key = get_code_key(account);
+        if let Some(code) = overrides.code {
+            let code_key = get_code_key(&account);
             let code_hash = code.hash();
             storage.set_value(code_key, code_hash);
             let known_code_key = get_known_code_key(&code_hash);
             storage.set_value(known_code_key, H256::from_low_u64_be(1));
-            storage.store_factory_dep(code_hash, code.clone().into_bytes());
+            storage.store_factory_dep(code_hash, code.into_bytes());
         }
 
-        match &overrides.state {
+        match overrides.state {
             Some(OverrideState::State(state)) => {
-                let account = AccountTreeId::new(*account);
-                for (&key, &value) in state {
+                let account = AccountTreeId::new(account);
+                for (key, value) in state {
                     storage.set_value(StorageKey::new(account, key), value);
                 }
                 storage.insert_erased_account(account);
             }
             Some(OverrideState::StateDiff(state_diff)) => {
-                let account = AccountTreeId::new(*account);
-                for (&key, &value) in state_diff {
+                let account = AccountTreeId::new(account);
+                for (key, value) in state_diff {
                     storage.set_value(StorageKey::new(account, key), value);
                 }
             }
@@ -123,7 +123,7 @@ mod tests {
         storage.set_value(retained_key, H256::repeat_byte(0xfe));
         let erased_key = StorageKey::new(AccountTreeId::new(Address::repeat_byte(5)), H256::zero());
         storage.set_value(erased_key, H256::repeat_byte(1));
-        let mut storage = apply_state_override(storage, &overrides);
+        let mut storage = apply_state_override(storage, overrides);
 
         let balance = storage.read_value(&storage_key_for_eth_balance(&Address::repeat_byte(1)));
         assert_eq!(balance, H256::from_low_u64_be(1));
```

### core/node/api_server/src/execution_sandbox/testonly.rs
```diff
@@ -0,0 +1,64 @@
+use tokio::runtime::Handle;
+use zksync_dal::{Connection, Core, CoreDal};
+use zksync_state::PostgresStorage;
+use zksync_types::{
+    api::state_override::StateOverride, AccountTreeId, L2BlockNumber, StorageKey, StorageLog, H256,
+};
+
+use super::storage::apply_state_override;
+
+/// Applies overrides to the Postgres storage by inserting the necessary storage logs / factory deps into the genesis block.
+pub(crate) async fn apply_state_overrides(
+    mut connection: Connection<'static, Core>,
+    state_override: StateOverride,
+) {
+    let latest_block = connection
+        .blocks_dal()
+        .get_sealed_l2_block_number()
+        .await
+        .unwrap()
+        .expect("no blocks in Postgres");
+    let state = PostgresStorage::new_async(Handle::current(), connection, latest_block, false)
+        .await
+        .unwrap();
+    let state_with_overrides =
+        tokio::task::spawn_blocking(|| apply_state_override(state, state_override))
+            .await
+            .unwrap();
+    let (state, overrides) = state_with_overrides.into_parts();
+
+    let mut connection = state.into_inner();
+    let mut storage_logs = vec![];
+    // Old logs must be erased before inserting `overridden_slots`.
+    let all_existing_logs = connection
+        .storage_logs_dal()
+        .dump_all_storage_logs_for_tests()
+        .await;
+    for log in all_existing_logs {
+        if let (Some(addr), Some(key)) = (log.address, log.key) {
+            let account = AccountTreeId::new(addr);
+            if overrides.empty_accounts.contains(&account) {
+                let key = StorageKey::new(account, key);
+                storage_logs.push(StorageLog::new_write_log(key, H256::zero()));
+            }
+        }
+    }
+
+    storage_logs.extend(
+        overrides
+            .overridden_slots
+            .into_iter()
+            .map(|(key, value)| StorageLog::new_write_log(key, value)),
+    );
+
+    connection
+        .storage_logs_dal()
+        .append_storage_logs(L2BlockNumber(0), &storage_logs)
+        .await
+        .unwrap();
+    connection
+        .factory_deps_dal()
+        .insert_factory_deps(L2BlockNumber(0), &overrides.overridden_factory_deps)
+        .await
+        .unwrap();
+}
```

### core/node/api_server/src/execution_sandbox/vm_metrics.rs
```diff
@@ -1,9 +1,13 @@
 use std::time::Duration;
 
 use vise::{
-    Buckets, EncodeLabelSet, EncodeLabelValue, Family, Gauge, Histogram, LatencyObserver, Metrics,
+    Buckets, Counter, EncodeLabelSet, EncodeLabelValue, Family, Gauge, Histogram, LatencyObserver,
+    Metrics,
+};
+use zksync_types::{
+    api::state_override::{OverrideState, StateOverride},
+    H256,
 };
-use zksync_types::H256;
 
 use crate::utils::ReportFilter;
 
@@ -75,6 +79,27 @@ impl Drop for SubmitTxLatencyObserver<'_> {
     }
 }
 
+#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, EncodeLabelValue)]
+#[metrics(rename_all = "snake_case")]
+enum OverrideKind {
+    Code,
+    Nonce,
+    Balance,
+    StorageSlot,
+}
+
+impl OverrideKind {
+    fn for_method(self, method: &'static str) -> StateOverrideLabels {
+        StateOverrideLabels { method, kind: self }
+    }
+}
+
+#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, EncodeLabelSet)]
+struct StateOverrideLabels {
+    method: &'static str,
+    kind: OverrideKind,
+}
+
 #[derive(Debug, Metrics)]
 #[metrics(prefix = "api_web3")]
 pub(crate) struct SandboxMetrics {
@@ -96,6 +121,8 @@ pub(crate) struct SandboxMetrics {
     /// is (as expected) greater than the final gas estimate.
     #[metrics(buckets = Buckets::linear(-0.05..=0.15, 0.01))]
     pub estimate_gas_optimistic_gas_limit_relative_diff: Histogram<f64>,
+    /// Statistics on state overrides.
+    state_overrides: Family<StateOverrideLabels, Counter>,
 }
 
 impl SandboxMetrics {
@@ -110,6 +137,27 @@ impl SandboxMetrics {
             stage,
         }
     }
+
+    pub fn observe_override_metrics(&self, method: &'static str, state_overrides: &StateOverride) {
+        for (_, account_override) in state_overrides.iter() {
+            if account_override.code.is_some() {
+                self.state_overrides[&OverrideKind::Code.for_method(method)].inc();
+            }
+            if account_override.nonce.is_some() {
+                self.state_overrides[&OverrideKind::Nonce.for_method(method)].inc();
+            }
+            if account_override.balance.is_some() {
+                self.state_overrides[&OverrideKind::Balance.for_method(method)].inc();
+            }
+            if let Some(state) = &account_override.state {
+                let slot_count = match state {
+                    OverrideState::State(slots) | OverrideState::StateDiff(slots) => slots.len(),
+                };
+                self.state_overrides[&OverrideKind::StorageSlot.for_method(method)]
+                    .inc_by(slot_count as u64);
+            }
+        }
+    }
 }
 
 #[vise::register]
```

### core/node/api_server/src/testonly.rs
```diff
@@ -4,7 +4,7 @@ use std::{collections::HashMap, iter};
 
 use assert_matches::assert_matches;
 use zk_evm_1_5_0::zkevm_opcode_defs::decoding::{EncodingModeProduction, VmEncodingMode};
-use zksync_contracts::{eth_contract, load_contract, read_bytecode};
+use zksync_contracts::{load_contract, read_bytecode};
 use zksync_dal::{
     transactions_dal::L2TxSubmissionResult, Connection, ConnectionPool, Core, CoreDal,
 };
@@ -19,8 +19,9 @@ use zksync_node_genesis::{insert_genesis_batch, GenesisParams};
 use zksync_node_test_utils::{create_l2_block, default_l1_batch_env, default_system_env};
 use zksync_state::PostgresStorage;
 use zksync_system_constants::{
-    CONTRACT_DEPLOYER_ADDRESS, L2_BASE_TOKEN_ADDRESS, REQUIRED_L1_TO_L2_GAS_PER_PUBDATA_BYTE,
-    SYSTEM_CONTEXT_ADDRESS, SYSTEM_CONTEXT_CURRENT_L2_BLOCK_INFO_POSITION,
+    CONTRACT_DEPLOYER_ADDRESS, L2_BASE_TOKEN_ADDRESS, NONCE_HOLDER_ADDRESS,
+    REQUIRED_L1_TO_L2_GAS_PER_PUBDATA_BYTE, SYSTEM_CONTEXT_ADDRESS,
+    SYSTEM_CONTEXT_CURRENT_L2_BLOCK_INFO_POSITION,
 };
 use zksync_test_contracts::{Account, LoadnextContractExecutionParams, TestContract};
 use zksync_types::{
@@ -30,10 +31,9 @@ use zksync_types::{
     bytecode::BytecodeHash,
     commitment::PubdataParams,
     ethabi,
-    ethabi::Token,
+    ethabi::{ParamType, Token},
     fee::Fee,
     fee_model::FeeParams,
-    get_code_key, get_known_code_key,
     l1::L1Tx,
     l2::L2Tx,
     transaction_request::{CallRequest, Eip712Meta},
@@ -45,6 +45,8 @@ use zksync_types::{
 };
 use zksync_vm_executor::{batch::MainBatchExecutorFactory, interface::BatchExecutorFactory};
 
+use crate::execution_sandbox::testonly::apply_state_overrides;
+
 const MULTICALL3_CONTRACT_PATH: &str =
     "contracts/l2-contracts/zkout/Multicall3.sol/Multicall3.json";
 
@@ -121,6 +123,11 @@ impl StateBuilder {
         self
     }
 
+    pub fn with_nonce(mut self, address: Address, nonce: U256) -> Self {
+        self.inner.entry(address).or_default().nonce = Some(nonce);
+        self
+    }
+
     pub fn with_expensive_contract(self) -> Self {
         self.with_contract(
             Self::EXPENSIVE_CONTRACT_ADDRESS,
@@ -169,50 +176,8 @@ impl StateBuilder {
     }
 
     /// Applies these state overrides to Postgres storage, which is assumed to be empty (other than genesis data).
-    pub async fn apply(self, connection: &mut Connection<'_, Core>) {
-        let mut storage_logs = vec![];
-        let mut factory_deps = HashMap::new();
-        for (address, account) in self.inner {
-            if let Some(balance) = account.balance {
-                let balance_key = storage_key_for_eth_balance(&address);
-                storage_logs.push(StorageLog::new_write_log(
-                    balance_key,
-                    u256_to_h256(balance),
-                ));
-            }
-            if let Some(code) = account.code {
-                let code_hash = code.hash();
-                storage_logs.extend([
-                    StorageLog::new_write_log(get_code_key(&address), code_hash),
-                    StorageLog::new_write_log(
-                        get_known_code_key(&code_hash),
-                        H256::from_low_u64_be(1),
-                    ),
-                ]);
-                factory_deps.insert(code_hash, code.into_bytes());
-            }
-            if let Some(state) = account.state {
-                let state_slots = match state {
-                    OverrideState::State(slots) | OverrideState::StateDiff(slots) => slots,
-                };
-                let state_logs = state_slots.into_iter().map(|(key, value)| {
-                    let key = StorageKey::new(AccountTreeId::new(address), key);
-                    StorageLog::new_write_log(key, value)
-                });
-                storage_logs.extend(state_logs);
-            }
-        }
-
-        connection
-            .storage_logs_dal()
-            .append_storage_logs(L2BlockNumber(0), &storage_logs)
-            .await
-            .unwrap();
-        connection
-            .factory_deps_dal()
-            .insert_factory_deps(L2BlockNumber(0), &factory_deps)
-            .await
-            .unwrap();
+    pub async fn apply(self, connection: Connection<'static, Core>) {
+        apply_state_overrides(connection, StateOverride::new(self.inner)).await;
     }
 }
 
@@ -318,6 +283,8 @@ pub(crate) trait TestAccount {
 
     fn query_base_token_balance(&self) -> CallRequest;
 
+    fn query_min_nonce(&self, address: Address) -> CallRequest;
+
     fn create_transfer_with_fee(&mut self, to: Address, value: U256, fee: Fee) -> L2Tx;
 
     fn create_load_test_tx(&mut self, params: LoadnextContractExecutionParams) -> L2Tx;
@@ -355,7 +322,7 @@ impl TestAccount for Account {
     }
 
     fn query_base_token_balance(&self) -> CallRequest {
-        let data = eth_contract()
+        let data = zksync_contracts::eth_contract()
             .function("balanceOf")
             .expect("No `balanceOf` function in contract")
             .encode_input(&[Token::Uint(address_to_u256(&self.address()))])
@@ -368,6 +335,18 @@ impl TestAccount for Account {
         }
     }
 
+    fn query_min_nonce(&self, address: Address) -> CallRequest {
+        let signature = ethabi::short_signature("getMinNonce", &[ParamType::Address]);
+        let mut data = signature.to_vec();
+        data.extend_from_slice(&ethabi::encode(&[Token::Address(address)]));
+        CallRequest {
+            from: Some(self.address()),
+            to: Some(NONCE_HOLDER_ADDRESS),
+            data: Some(data.into()),
+            ..CallRequest::default()
+        }
+    }
+
     fn create_load_test_tx(&mut self, params: LoadnextContractExecutionParams) -> L2Tx {
         let execute = Execute {
             contract_address: Some(StateBuilder::LOAD_TEST_ADDRESS),
```

### core/node/api_server/src/tx_sender/tests/call.rs
```diff
@@ -266,3 +266,32 @@ async fn limiting_storage_access_during_call(vm_mode: FastVmMode) {
         .unwrap_err();
     assert_matches!(err, SubmitTxError::ExecutionReverted(msg, _) if msg.contains("limit reached"));
 }
+
+#[tokio::test]
+async fn overriding_account_nonce() {
+    let alice = Account::random();
+    let pool = ConnectionPool::<Core>::constrained_test_pool(1).await;
+    let tx_sender = create_real_tx_sender(pool).await;
+
+    // Check the base case (no overrides).
+    let output = test_call(
+        &tx_sender,
+        StateOverride::default(),
+        alice.query_min_nonce(alice.address),
+    )
+    .await
+    .unwrap();
+    assert_eq!(decode_u256_output(&output), 0.into());
+
+    let state_override = StateBuilder::default()
+        .with_nonce(alice.address, 23.into())
+        .build();
+    let output = test_call(
+        &tx_sender,
+        state_override,
+        alice.query_min_nonce(alice.address),
+    )
+    .await
+    .unwrap();
+    assert_eq!(decode_u256_output(&output), 23.into());
+}
```

### core/node/api_server/src/tx_sender/tests/send_tx.rs
```diff
@@ -33,9 +33,8 @@ async fn submitting_tx_requires_one_connection() {
     // Manually set sufficient balance for the tx initiator.
     StateBuilder::default()
         .with_balance(tx.initiator_account(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     let mut tx_executor = MockOneshotExecutor::default();
     tx_executor.set_tx_responses(move |received_tx, _| {
@@ -137,9 +136,8 @@ async fn fee_validation_errors() {
 
     StateBuilder::default()
         .with_balance(tx.initiator_account(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     // Sanity check: validation should succeed with reasonable fee params.
     tx_sender
@@ -193,12 +191,11 @@ async fn sending_transfer() {
     let mut alice = Account::random();
 
     // Manually set sufficient balance for the tx initiator.
-    let mut storage = tx_sender.acquire_replica_connection().await.unwrap();
+    let storage = tx_sender.acquire_replica_connection().await.unwrap();
     StateBuilder::default()
         .with_balance(alice.address(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     let transfer = alice.create_transfer(1_000_000_000.into());
     let vm_result = tx_sender.submit_tx(transfer, block_args).await.unwrap();
@@ -230,12 +227,11 @@ async fn sending_transfer_with_incorrect_signature() {
     let mut alice = Account::random();
     let transfer_value = 1_000_000_000.into();
 
-    let mut storage = tx_sender.acquire_replica_connection().await.unwrap();
+    let storage = tx_sender.acquire_replica_connection().await.unwrap();
     StateBuilder::default()
         .with_balance(alice.address(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     let mut transfer = alice.create_transfer(transfer_value);
     transfer.execute.value = transfer_value / 2; // This should invalidate tx signature
@@ -251,13 +247,12 @@ async fn sending_load_test_transaction(tx_params: LoadnextContractExecutionParam
     let block_args = pending_block_args(&tx_sender).await;
     let mut alice = Account::random();
 
-    let mut storage = tx_sender.acquire_replica_connection().await.unwrap();
+    let storage = tx_sender.acquire_replica_connection().await.unwrap();
     StateBuilder::default()
         .with_load_test_contract()
         .with_balance(alice.address(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     let tx = alice.create_load_test_tx(tx_params);
     let vm_result = tx_sender.submit_tx(tx, block_args).await.unwrap();
@@ -271,13 +266,12 @@ async fn sending_reverting_transaction() {
     let block_args = pending_block_args(&tx_sender).await;
     let mut alice = Account::random();
 
-    let mut storage = tx_sender.acquire_replica_connection().await.unwrap();
+    let storage = tx_sender.acquire_replica_connection().await.unwrap();
     StateBuilder::default()
         .with_counter_contract(0)
         .with_balance(alice.address(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     let tx = alice.create_counter_tx(1.into(), true);
     let vm_result = tx_sender.submit_tx(tx, block_args).await.unwrap();
@@ -294,13 +288,12 @@ async fn sending_transaction_out_of_gas() {
     let block_args = pending_block_args(&tx_sender).await;
     let mut alice = Account::random();
 
-    let mut storage = tx_sender.acquire_replica_connection().await.unwrap();
+    let storage = tx_sender.acquire_replica_connection().await.unwrap();
     StateBuilder::default()
         .with_infinite_loop_contract()
         .with_balance(alice.address(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     let tx = alice.create_infinite_loop_tx();
     let vm_result = tx_sender.submit_tx(tx, block_args).await.unwrap();
@@ -328,9 +321,8 @@ async fn submit_tx_with_validation_traces(actual_range: Range<u64>, expected_ran
     // Manually set sufficient balance for the tx initiator.
     StateBuilder::default()
         .with_balance(tx.initiator_account(), u64::MAX.into())
-        .apply(&mut storage)
+        .apply(storage)
         .await;
-    drop(storage);
 
     let mut tx_executor = MockOneshotExecutor::default();
     tx_executor.set_tx_responses(move |received_tx, _| {
```

### core/node/api_server/src/utils.rs
```diff
@@ -466,7 +466,7 @@ mod tests {
             .unwrap();
         StateBuilder::default()
             .with_balance(alice.address(), u64::MAX.into())
-            .apply(&mut storage)
+            .apply(storage)
             .await;
 
         let deploy_execute = Execute {
@@ -508,6 +508,7 @@ mod tests {
         persist_block_with_transactions(&pool, txs).await;
 
         // Check the account type helper.
+        let mut storage = pool.connection().await.unwrap();
         let account_types = get_account_types(
             &mut storage,
             [alice.address, account_addr].into_iter(),
```
