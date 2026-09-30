# [?] fix(api): Fix panics in API server if storage values cache is disabled (#1370)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-03-06
Source: https://github.com/matter-labs/zksync-era/commit/723232b98b064bb536a34a722155dfc438f03243
Type: security-commit

## Details
fix(api): Fix panics in API server if storage values cache is disabled (#1370)

## What ❔

Don't panic in `PostgresStorageCaches::schedule_values_update()` if the
values cache was not configured.

## Why ❔

This leads to panics if the cache is disabled via config. Ignoring the
update looks like more reasonable behavior.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.
- [x] Spellcheck has been run via `zk spellcheck`.
- [x] Linkcheck has been run via `zk linkcheck`.

## Patch
### core/lib/state/src/postgres/mod.rs
```diff
@@ -307,18 +307,16 @@ impl PostgresStorageCaches {
         }
     }
 
-    /// Schedules an update of the VM storage values cache to the specified miniblock.
+    /// Schedules an update of the VM storage values cache to the specified miniblock. If the values cache is not configured,
+    /// this is a no-op.
     ///
     /// # Panics
     ///
-    /// - Panics if the cache wasn't previously configured using [`Self::configure_storage_values_cache()`].
     /// - Panics if the cache update task returned from `configure_storage_values_cache()` has panicked.
     pub fn schedule_values_update(&self, to_miniblock: MiniblockNumber) {
-        let values = self
-            .values
-            .as_ref()
-            .expect("`schedule_update()` called without configuring values cache");
-
+        let Some(values) = &self.values else {
+            return;
+        };
         if values.cache.valid_for() < to_miniblock {
             // Filter out no-op updates right away in order to not store lots of them in RAM.
             values
```

### core/lib/zksync_core/src/api_server/execution_sandbox/mod.rs
```diff
@@ -221,19 +221,12 @@ pub(crate) struct TxSharedArgs {
 
 impl TxSharedArgs {
     #[cfg(test)]
-    pub fn mock(base_system_contracts: MultiVMBaseSystemContracts, pool: ConnectionPool) -> Self {
-        let mut caches = PostgresStorageCaches::new(1, 1);
-        tokio::task::spawn_blocking(caches.configure_storage_values_cache(
-            1,
-            pool,
-            Handle::current(),
-        ));
-
+    pub fn mock(base_system_contracts: MultiVMBaseSystemContracts) -> Self {
         Self {
             operator_account: AccountTreeId::default(),
             fee_input: BatchFeeInput::l1_pegged(55, 555),
             base_system_contracts,
-            caches,
+            caches: PostgresStorageCaches::new(1, 1),
             validation_computational_gas_limit: u32::MAX,
             chain_id: L2ChainId::default(),
         }
```

### core/lib/zksync_core/src/api_server/execution_sandbox/tests.rs
```diff
@@ -181,7 +181,7 @@ async fn test_instantiating_vm(pool: ConnectionPool, block_args: BlockArgs) {
     tokio::task::spawn_blocking(move || {
         apply_vm_in_sandbox(
             vm_permit,
-            TxSharedArgs::mock(ApiContracts::load_from_disk().estimate_gas, pool.clone()),
+            TxSharedArgs::mock(ApiContracts::load_from_disk().estimate_gas),
             true,
             &TxExecutionArgs::for_gas_estimate(None, &transaction, 123),
             &pool,
```

### core/lib/zksync_core/src/api_server/tx_sender/tests.rs
```diff
@@ -18,14 +18,7 @@ pub(crate) async fn create_test_tx_sender(
     let state_keeper_config = StateKeeperConfig::for_tests();
     let tx_sender_config = TxSenderConfig::new(&state_keeper_config, &web3_config, l2_chain_id);
 
-    let mut storage_caches = PostgresStorageCaches::new(1, 1);
-    let cache_update_task = storage_caches.configure_storage_values_cache(
-        1,
-        pool.clone(),
-        tokio::runtime::Handle::current(),
-    );
-    tokio::task::spawn_blocking(cache_update_task);
-
+    let storage_caches = PostgresStorageCaches::new(1, 1);
     let batch_fee_model_input_provider = Arc::new(MockBatchFeeParamsProvider::default());
     let (mut tx_sender, vm_barrier) = crate::build_tx_sender(
         &tx_sender_config,
```
