# [?] Fix a transaction pool overflow

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2024-01-08
Source: https://github.com/Conflux-Chain/conflux-rust/commit/9aa5ced3a47e7939421bef8e4ae2edf8c095b6c2
Type: security-commit

## Details
Fix a transaction pool overflow

## Patch
### client/src/configuration.rs
```diff
@@ -12,7 +12,9 @@ use cfx_addr::{cfx_addr_decode, Network};
 use cfx_internal_common::{
     ChainIdParams, ChainIdParamsInner, ChainIdParamsOneChainInner,
 };
-use cfx_parameters::block::DEFAULT_TARGET_BLOCK_GAS_LIMIT;
+use cfx_parameters::{
+    block::DEFAULT_TARGET_BLOCK_GAS_LIMIT, tx_pool::TXPOOL_DEFAULT_NONCE_BITS,
+};
 use cfx_storage::{
     defaults::DEFAULT_DEBUG_SNAPSHOT_CHECKER_THREADS, storage_dir,
     ConsensusParam, ProvideExtraSnapshotSyncConfig, StorageConfiguration,
@@ -266,6 +268,7 @@ build_config! {
         (tx_pool_size, (usize), 50_000)
         (tx_pool_min_native_tx_gas_price, (Option<u64>), None)
         (tx_pool_min_eth_tx_gas_price, (Option<u64>), None)
+        (tx_pool_nonce_bits, (usize), TXPOOL_DEFAULT_NONCE_BITS)
         (max_packing_batch_gas_limit, (u64), 3_000_000)
         (max_packing_batch_size, (usize), 50)
         (packing_pool_degree, (u8), 4)
@@ -694,6 +697,7 @@ impl Configuration {
             self.raw_conf.referee_bound,
             self.raw_conf.max_block_size_in_bytes,
             self.raw_conf.transaction_epoch_bound,
+            self.raw_conf.tx_pool_nonce_bits,
             machine,
             pos_verifier,
         )
```

### core/parameters/src/lib.rs
```diff
@@ -191,6 +191,10 @@ pub mod pow {
     pub const INITIAL_DIFFICULTY: u64 = 20_000_000_000;
 }
 
+pub mod tx_pool {
+    pub const TXPOOL_DEFAULT_NONCE_BITS: usize = 128;
+}
+
 pub mod block {
     use crate::consensus::GENESIS_GAS_LIMIT;
 
```

### core/src/sync/utils.rs
```diff
@@ -10,6 +10,7 @@ use cfx_internal_common::ChainIdParamsInner;
 use cfx_parameters::{
     block::{MAX_BLOCK_SIZE_IN_BYTES, REFEREE_DEFAULT_BOUND},
     consensus::{GENESIS_GAS_LIMIT, TRANSACTION_DEFAULT_EPOCH_BOUND},
+    tx_pool::TXPOOL_DEFAULT_NONCE_BITS,
     WORKER_COMPUTATION_PARALLELISM,
 };
 use cfx_storage::{StorageConfiguration, StorageManager};
@@ -206,6 +207,7 @@ pub fn initialize_synchronization_graph_with_data_manager(
         REFEREE_DEFAULT_BOUND,
         MAX_BLOCK_SIZE_IN_BYTES,
         TRANSACTION_DEFAULT_EPOCH_BOUND,
+        TXPOOL_DEFAULT_NONCE_BITS,
         machine.clone(),
         pos_verifier.clone(),
     );
```

### core/src/transaction_pool/transaction_pool_inner.rs
```diff
@@ -268,7 +268,7 @@ impl DeferredPool {
         let removed_tx = self
             .packing_pool
             .in_space_mut(addr.space)
-            .split_off_prefix(tx.sender(), &(tx.nonce() - 1));
+            .split_off_prefix(tx.sender(), &(tx.nonce() + 1));
         if let Some(removed_tx) = removed_tx.first() {
             if removed_tx.nonce() < tx.nonce() {
                 warn!("Internal Issue: Packing pool has inconsistent tranaction with nonce pool.");
```

### core/src/verification.rs
```diff
@@ -38,6 +38,7 @@ pub struct VerificationConfig {
     pub referee_bound: usize,
     pub max_block_size_in_bytes: usize,
     pub transaction_epoch_bound: u64,
+    pub max_nonce: Option<U256>,
     machine: Arc<Machine>,
     pos_verifier: Arc<PosVerifier>,
 }
@@ -220,10 +221,15 @@ pub fn is_valid_receipt_inclusion_proof(
 impl VerificationConfig {
     pub fn new(
         test_mode: bool, referee_bound: usize, max_block_size_in_bytes: usize,
-        transaction_epoch_bound: u64, machine: Arc<Machine>,
-        pos_verifier: Arc<PosVerifier>,
+        transaction_epoch_bound: u64, tx_pool_nonce_bits: usize,
+        machine: Arc<Machine>, pos_verifier: Arc<PosVerifier>,
     ) -> Self
     {
+        let max_nonce = if tx_pool_nonce_bits < 256 {
+            Some((U256::one() << tx_pool_nonce_bits) - 1)
+        } else {
+            None
+        };
         if test_mode {
             VerificationConfig {
                 verify_timestamp: false,
@@ -232,6 +238,7 @@ impl VerificationConfig {
                 transaction_epoch_bound,
                 machine,
                 pos_verifier,
+                max_nonce,
             }
         } else {
             VerificationConfig {
@@ -241,6 +248,7 @@ impl VerificationConfig {
                 transaction_epoch_bound,
                 machine,
                 pos_verifier,
+                max_nonce,
             }
         }
     }
@@ -629,6 +637,14 @@ impl VerificationConfig {
             }
         }
 
+        if let (VerifyTxMode::Local(..), Some(max_nonce)) =
+            (mode, self.max_nonce)
+        {
+            if tx.nonce() > &max_nonce {
+                bail!(TransactionError::TooLargeNonce)
+            }
+        }
+
         // ******************************************
         // Each constraint depends on a mode or a CIP should be
         // implemented in a seperated function.
```

### primitives/src/transaction.rs
```diff
@@ -106,6 +106,8 @@ pub enum TransactionError {
     InvalidEthereumLike,
     /// Receiver with invalid type bit.
     InvalidReceiver,
+    /// Transaction nonce exceeds local limit.
+    TooLargeNonce,
 }
 
 impl From<keylib::Error> for TransactionError {
@@ -169,6 +171,7 @@ impl fmt::Display for TransactionError {
             ZeroGasPrice => "Zero gas price is not allowed".into(),
             InvalidEthereumLike => "Ethereum like transaction should have u64::MAX storage limit".into(),
             InvalidReceiver => "Sending transaction to invalid address. The first four bits of address must be 0x0, 0x1, or 0x8.".into(),
+            TooLargeNonce => "Transaction nonce is too large.".into(),
         };
 
         f.write_fmt(format_args!("Transaction error ({})", msg))
```
