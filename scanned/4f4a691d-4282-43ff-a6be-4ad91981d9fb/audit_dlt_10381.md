# [?] Fix crash recovery tests

## Summary
Severity: Unknown
Chain: Sovereign SDK
Component: Sovereign-Labs/sovereign-sdk
Published: 2026-01-26
Source: https://github.com/Sovereign-Labs/sovereign-sdk/commit/7a2533463bf3d56e4f6529d58c2751bf30b480ff
Type: security-commit

## Details
Fix crash recovery tests

## Patch
### examples/demo-rollup/tests/restart/crash.rs
```diff
@@ -1,4 +1,4 @@
-use crate::test_helpers::build_transfer_token_tx;
+use crate::test_helpers::build_transfer_token_tx_with_generation;
 use crate::test_helpers::test_genesis_source;
 use futures::stream::BoxStream;
 use futures::StreamExt;
@@ -120,7 +120,7 @@ async fn test_crash_before_commiting_live() -> anyhow::Result<()> {
 
 // This test checks whether rollup can recover from different kinds of crashes, see `CrashLocation` enum.
 async fn test_start_stop_with_crash(crash_moment: CrashLocation) -> anyhow::Result<()> {
-    let temp_dir = Arc::new(tempfile::tempdir()?);
+    let temp_dir: Arc<TempDir> = Arc::new(tempfile::tempdir()?);
 
     let mut mock_da_config = MockDaConfig::instant_with_sender(MockAddress::new([0; 32]));
     mock_da_config.block_producing = BlockProducingConfig::Periodic {
@@ -259,7 +259,7 @@ async fn send_txs(
     let api_client = client.client.clone();
     let mut nb_of_txs = 0;
     loop {
-        let tx = build_transfer_token_tx::<MockNomtRollupSpec<Native>>(
+        let tx = build_transfer_token_tx_with_generation::<MockNomtRollupSpec<Native>>(
             &key_and_address.private_key,
             config_gas_token_id(),
             receiver,
```

### examples/demo-rollup/tests/test_helpers.rs
```diff
@@ -43,12 +43,12 @@ pub fn test_genesis_paths(operating_mode: OperatingMode) -> GenesisPaths {
 }
 
 /// Creates token transfer tx.
-pub fn build_transfer_token_tx<S>(
+pub fn build_transfer_token_tx_uniqueness_data<S>(
     key: &<<S as Spec>::CryptoSpec as CryptoSpec>::PrivateKey,
     token_id: TokenId,
     recipient: <S as Spec>::Address,
     amount: u128,
-    nonce: u64,
+    uniqueness_data: UniquenessData,
 ) -> Transaction<Runtime<S>, S>
 where
     S: Spec,
@@ -64,8 +64,48 @@ where
     test_signed_transaction(
         key,
         &msg,
-        UniquenessData::Nonce(nonce),
+        uniqueness_data,
         &CHAIN_HASH,
         default_test_tx_details(),
     )
 }
+
+pub fn build_transfer_token_tx_with_generation<S>(
+    key: &<<S as Spec>::CryptoSpec as CryptoSpec>::PrivateKey,
+    token_id: TokenId,
+    recipient: <S as Spec>::Address,
+    amount: u128,
+    generation: u64,
+) -> Transaction<Runtime<S>, S>
+where
+    S: Spec,
+    <S as Spec>::Address: FromVmAddress<EthereumAddress>,
+{
+    build_transfer_token_tx_uniqueness_data(
+        key,
+        token_id,
+        recipient,
+        amount,
+        UniquenessData::Generation(generation),
+    )
+}
+
+pub fn build_transfer_token_tx<S>(
+    key: &<<S as Spec>::CryptoSpec as CryptoSpec>::PrivateKey,
+    token_id: TokenId,
+    recipient: <S as Spec>::Address,
+    amount: u128,
+    nonce: u64,
+) -> Transaction<Runtime<S>, S>
+where
+    S: Spec,
+    <S as Spec>::Address: FromVmAddress<EthereumAddress>,
+{
+    build_transfer_token_tx_uniqueness_data(
+        key,
+        token_id,
+        recipient,
+        amount,
+        UniquenessData::Nonce(nonce),
+    )
+}
```
