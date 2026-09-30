# [?] Avoid panic in reactor tests

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-01-29
Source: https://github.com/casper-network/casper-node/commit/e4a8b1b960ccc136e162361990c5082ce53422ba
Type: security-commit

## Details
Avoid panic in reactor tests

## Patch
### node/src/reactor/main_reactor/tests/binary_port.rs
```diff
@@ -10,16 +10,17 @@ use casper_types::{
     bytesrepr::{FromBytes, ToBytes},
     testing::TestRng,
     AvailableBlockRange, BlockHash, BlockHashAndHeight, BlockHeader, BlockIdentifier,
-    BlockSynchronizerStatus, ChainspecRawBytes, Digest, Key, KeyTag, NextUpgrade, Peers,
-    ProtocolVersion, ReactorState, SecretKey, SignedBlock, StoredValue, Transaction,
-    TransactionHash, TransactionV1Builder, Transfer,
+    BlockSynchronizerStatus, ChainspecRawBytes, DeployBuilder, Digest, Key, KeyTag, NextUpgrade,
+    Peers, ProtocolVersion, ReactorState, SecretKey, SignedBlock, StoredValue, Transaction,
+    TransactionHash, TransactionV1Builder, Transfer, TransferTarget,
 };
 use juliet::{
     io::IoCoreBuilder,
     protocol::ProtocolBuilder,
     rpc::{JulietRpcClient, RpcBuilder},
     ChannelConfiguration, ChannelId,
 };
+use rand::Rng;
 use tokio::{net::TcpStream, time::timeout};
 use tracing::error;
 
@@ -224,7 +225,7 @@ async fn binary_port_component() {
         get_trie(*highest_block.block().state_root_hash()),
         try_accept_transaction(&secret_key),
         try_accept_transaction_invalid(&mut rng),
-        try_spec_exec_invalid(&mut rng, highest_block.block().clone_header()),
+        try_spec_exec_invalid(&mut rng, highest_block.block().clone_header(), &secret_key),
     ];
 
     let header = BinaryRequestHeader::new(ProtocolVersion::V1_0_0);
@@ -649,8 +650,20 @@ fn try_accept_transaction_invalid(rng: &mut TestRng) -> TestCase {
     }
 }
 
-fn try_spec_exec_invalid(rng: &mut TestRng, header: BlockHeader) -> TestCase {
-    let transaction = Transaction::V1(TransactionV1Builder::new_random(rng).build().unwrap());
+fn try_spec_exec_invalid(rng: &mut TestRng, header: BlockHeader, key: &SecretKey) -> TestCase {
+    let transaction = Transaction::Deploy(
+        DeployBuilder::new_transfer(
+            "casper-example",
+            100,
+            None,
+            TransferTarget::URef(rng.gen()),
+            None,
+        )
+        .with_secret_key(key)
+        .with_standard_payment(100)
+        .build()
+        .unwrap(),
+    );
     TestCase {
         name: "try_spec_exec_invalid",
         request: BinaryRequest::TrySpeculativeExec {
```
