# [?] fix(supervisor/core): `l1_exhaust` and `reorg` race condition (op-rs/kona#2779)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-08-28
Source: https://github.com/ethereum-optimism/optimism/commit/676b987dc400c2acf21f79c5ce95c0a3f4fa9786
Type: security-commit

## Details
fix(supervisor/core): `l1_exhaust` and `reorg` race condition (op-rs/kona#2779)

Closes #2777

## Patch
### crates/supervisor/core/src/syncnode/node.rs
```diff
@@ -17,7 +17,7 @@ use kona_supervisor_storage::{DerivationStorageReader, HeadRefStorageReader, Log
 use kona_supervisor_types::{BlockSeal, OutputV0, Receipts};
 use std::sync::Arc;
 use tokio::sync::{Mutex, mpsc};
-use tracing::{error, trace, warn};
+use tracing::{debug, error, trace, warn};
 
 /// [`ManagedNode`] handles the subscription to managed node events.
 ///
@@ -49,7 +49,7 @@ where
         l1_provider: RootProvider<Ethereum>,
         chain_event_sender: mpsc::Sender<ChainEvent>,
     ) -> Self {
-        let resetter = Arc::new(Resetter::new(client.clone(), db_provider));
+        let resetter = Arc::new(Resetter::new(client.clone(), l1_provider.clone(), db_provider));
 
         Self { client, resetter, l1_provider, chain_event_sender, chain_id: Mutex::new(None) }
     }
@@ -116,10 +116,10 @@ where
             timestamp: block.header.timestamp,
         };
 
-        if block.header.parent_hash != derived_ref_pair.source.hash {
+        if new_source.parent_hash != derived_ref_pair.source.hash {
             // this could happen due to a reorg.
             // this case should be handled by the reorg manager
-            warn!(
+            debug!(
                 target: "supervisor::managed_node",
                 %chain_id,
                 %new_source,
@@ -617,7 +617,7 @@ mod tests {
         client.expect_provide_l1().times(1).returning(|_| Ok(())); // Should be called
 
         let client = Arc::new(client);
-        let db = Arc::new(MockDb::new());
+        let db = MockDb::new();
 
         let derived_ref_pair = DerivedRefPair {
             source: BlockInfo {
@@ -674,7 +674,7 @@ mod tests {
         asserter.push(MockResponse::Success(serde_json::from_str(next_block).unwrap()));
 
         let (tx, _rx) = mpsc::channel(10);
-        let node = ManagedNode::new(client.clone(), db, l1_provider, tx);
+        let node = ManagedNode::new(client.clone(), Arc::new(db), l1_provider, tx);
 
         let result = node.handle_exhaust_l1(&derived_ref_pair).await;
         assert!(result.is_ok());
```

### crates/supervisor/core/src/syncnode/resetter.rs
```diff
@@ -1,16 +1,19 @@
 use super::{ManagedNodeClient, ManagedNodeError};
-use alloy_eips::BlockNumHash;
+use alloy_eips::{BlockNumHash, BlockNumberOrTag};
+use alloy_network::Ethereum;
 use alloy_primitives::ChainId;
+use alloy_provider::{Provider, RootProvider};
 use kona_protocol::BlockInfo;
 use kona_supervisor_storage::{DerivationStorageReader, HeadRefStorageReader, StorageError};
 use kona_supervisor_types::SuperHead;
 use std::sync::Arc;
 use tokio::sync::Mutex;
-use tracing::{error, info};
+use tracing::{error, info, warn};
 
 #[derive(Debug)]
 pub(super) struct Resetter<DB, C> {
     client: Arc<C>,
+    l1_provider: RootProvider<Ethereum>,
     db_provider: Arc<DB>,
     reset_guard: Mutex<()>,
 }
@@ -21,8 +24,12 @@ where
     C: ManagedNodeClient + Send + Sync + 'static,
 {
     /// Creates a new [`Resetter`] with the specified client.
-    pub(super) fn new(client: Arc<C>, db_provider: Arc<DB>) -> Self {
-        Self { client, db_provider, reset_guard: Mutex::new(()) }
+    pub(super) fn new(
+        client: Arc<C>,
+        l1_provider: RootProvider<Ethereum>,
+        db_provider: Arc<DB>,
+    ) -> Self {
+        Self { client, l1_provider, db_provider, reset_guard: Mutex::new(()) }
     }
 
     /// Resets the node using the latest super head.
@@ -45,6 +52,15 @@ where
             }
         };
 
+        // check if the source of valid local_safe is canonical
+        // If the source block is not canonical, it mean there is a reorg on L1
+        // this makes sure that we always reset to a valid state
+        let source = self.db_provider.derived_to_source(local_safe.id())?;
+        if !self.is_canonical(chain_id, source.id()).await? {
+            warn!(target: "supervisor::syncnode_resetter", %chain_id, %source, "Source block for the valid local safe is not canonical");
+            return Err(ManagedNodeError::ResetFailed);
+        }
+
         let SuperHead { cross_unsafe, cross_safe, finalized, .. } =
             self.db_provider.get_super_head().inspect_err(
                 |err| error!(target: "supervisor::syncnode_resetter", %chain_id, %err, "Failed to get super head"),
@@ -155,6 +171,23 @@ where
                 })?;
         }
     }
+
+    async fn is_canonical(
+        &self,
+        chain_id: ChainId,
+        source: BlockNumHash,
+    ) -> Result<bool, ManagedNodeError> {
+        let canonical_block = self
+            .l1_provider
+            .get_block_by_number(BlockNumberOrTag::Number(source.number))
+            .await
+            .map_err(|err| {
+                warn!(target: "supervisor::syncnode_resetter", %chain_id, %err, "Failed to fetch source block from L1");
+                ManagedNodeError::GetBlockByNumberFailed(source.number)
+            })?;
+
+        canonical_block.map_or_else(|| Ok(false), |block| Ok(block.hash() == source.hash))
+    }
 }
 
 #[cfg(test)]
@@ -163,6 +196,8 @@ mod tests {
     use crate::syncnode::{AuthenticationError, ClientError};
     use alloy_eips::BlockNumHash;
     use alloy_primitives::{B256, ChainId};
+    use alloy_provider::mock::{Asserter, MockResponse, MockTransport};
+    use alloy_rpc_client::RpcClient;
     use async_trait::async_trait;
     use jsonrpsee::core::client::Subscription;
     use kona_interop::{DerivedRefPair, SafetyLevel};
@@ -242,13 +277,117 @@ mod tests {
         client.expect_chain_id().returning(move || Ok(1));
         client.expect_block_ref_by_number().returning(move |_| Ok(super_head.local_safe.unwrap()));
 
+        db.expect_derived_to_source()
+            .with(predicate::eq(super_head.local_safe.unwrap().id()))
+            .returning(move |_| Ok(super_head.l1_source.unwrap()));
+
+        let asserter = Asserter::new();
+        let transport = MockTransport::new(asserter.clone());
+        let l1_provider = RootProvider::<Ethereum>::new(RpcClient::new(transport, false));
+
+        let canonical_block = r#"{
+            "number": "100",
+            "hash": "0x3636363636363636363636363636363636363636363636363636363636363636",
+            "mixHash": "0x24900fb3da77674a861c428429dce0762707ecb6052325bbd9b3c64e74b5af9d",
+            "parentHash": "0x1f68ac259155e2f38211ddad0f0a15394d55417b185a93923e2abe71bb7a4d6d",
+            "nonce": "0x378da40ff335b070",
+            "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
+            "logsBloom": "0x00000000000000100000004080000000000500000000000000020000100000000800001000000004000001000000000000000800040010000020100000000400000010000000000000000040000000000000040000000000000000000000000000000400002400000000000000000000000000000004000004000000000000840000000800000080010004000000001000000800000000000000000000000000000000000800000000000040000000020000000000000000000800000400000000000000000000000600000400000000002000000000000000000000004000000000000000100000000000000000000000000000000000040000900010000000",
+            "transactionsRoot":"0x4d0c8e91e16bdff538c03211c5c73632ed054d00a7e210c0eb25146c20048126",
+            "stateRoot": "0x91309efa7e42c1f137f31fe9edbe88ae087e6620d0d59031324da3e2f4f93233",
+            "receiptsRoot": "0x68461ab700003503a305083630a8fb8d14927238f0bc8b6b3d246c0c64f21f4a",
+            "miner":"0xb42b6c4a95406c78ff892d270ad20b22642e102d",
+            "difficulty": "0x66e619a",
+            "totalDifficulty": "0x1e875d746ae",
+            "extraData": "0xd583010502846765746885676f312e37856c696e7578",
+            "size": "0x334",
+            "gasLimit": "0x47e7c4",
+            "gasUsed": "0x37993",
+            "timestamp": "0x5835c54d",
+            "uncles": [],
+            "transactions": [
+                "0xa0807e117a8dd124ab949f460f08c36c72b710188f01609595223b325e58e0fc",
+                "0xeae6d797af50cb62a596ec3939114d63967c374fa57de9bc0f4e2b576ed6639d"
+            ],
+            "baseFeePerGas": "0x7",
+            "withdrawalsRoot": "0x7a4ecf19774d15cf9c15adf0dd8e8a250c128b26c9e2ab2a08d6c9c8ffbd104f",
+            "withdrawals": [],
+            "blobGasUsed": "0x0",
+            "excessBlobGas": "0x0",
+            "parentBeaconBlockRoot": "0x95c4dbd5b19f6fe3cbc3183be85ff4e85ebe75c5b4fc911f1c91e5b7a554a685"
+        }"#;
+        asserter.push(MockResponse::Success(serde_json::from_str(canonical_block).unwrap()));
+
         client.expect_reset().returning(|_, _, _, _, _| Ok(()));
 
-        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
+        let resetter = Resetter::new(Arc::new(client), l1_provider, Arc::new(db));
 
         assert!(resetter.reset().await.is_ok());
     }
 
+    #[tokio::test]
+    async fn test_reset_canonical_hash_mismatch() {
+        let super_head = make_super_head();
+
+        let mut db = MockDb::new();
+        db.expect_latest_derivation_state().returning(move || {
+            Ok(DerivedRefPair {
+                derived: super_head.local_safe.unwrap(),
+                source: super_head.l1_source.unwrap(),
+            })
+        });
+        db.expect_get_super_head().returning(move || Ok(super_head));
+
+        let mut client = MockClient::new();
+        client.expect_chain_id().returning(move || Ok(1));
+        client.expect_block_ref_by_number().returning(move |_| Ok(super_head.local_safe.unwrap()));
+
+        db.expect_derived_to_source()
+            .with(predicate::eq(super_head.local_safe.unwrap().id()))
+            .returning(move |_| Ok(super_head.l1_source.unwrap()));
+
+        let asserter = Asserter::new();
+        let transport = MockTransport::new(asserter.clone());
+        let l1_provider = RootProvider::<Ethereum>::new(RpcClient::new(transport, false));
+
+        let canonical_block = r#"{
+            "number": "100",
+            "hash": "0x3737373737373737373737373737373737373737373737373737373737367637",
+            "mixHash": "0x24900fb3da77674a861c428429dce0762707ecb6052325bbd9b3c64e74b5af9d",
+            "parentHash": "0x1f68ac259155e2f38211ddad0f0a15394d55417b185a93923e2abe71bb7a4d6d",
+            "nonce": "0x378da40ff335b070",
+            "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
+            "logsBloom": "0x00000000000000100000004080000000000500000000000000020000100000000800001000000004000001000000000000000800040010000020100000000400000010000000000000000040000000000000040000000000000000000000000000000400002400000000000000000000000000000004000004000000000000840000000800000080010004000000001000000800000000000000000000000000000000000800000000000040000000020000000000000000000800000400000000000000000000000600000400000000002000000000000000000000004000000000000000100000000000000000000000000000000000040000900010000000",
+            "transactionsRoot":"0x4d0c8e91e16bdff538c03211c5c73632ed054d00a7e210c0eb25146c20048126",
+            "stateRoot": "0x91309efa7e42c1f137f31fe9edbe88ae087e6620d0d59031324da3e2f4f93233",
+            "receiptsRoot": "0x68461ab700003503a305083630a8fb8d14927238f0bc8b6b3d246c0c64f21f4a",
+            "miner":"0xb42b6c4a95406c78ff892d270ad20b22642e102d",
+            "difficulty": "0x66e619a",
+            "totalDifficulty": "0x1e875d746ae",
+            "extraData": "0xd583010502846765746885676f312e37856c696e7578",
+            "size": "0x334",
+            "gasLimit": "0x47e7c4",
+            "gasUsed": "0x37993",
+            "timestamp": "0x5835c54d",
+            "uncles": [],
+            "transactions": [
+                "0xa0807e117a8dd124ab949f460f08c36c72b710188f01609595223b325e58e0fc",
+                "0xeae6d797af50cb62a596ec3939114d63967c374fa57de9bc0f4e2b576ed6639d"
+            ],
+            "baseFeePerGas": "0x7",
+            "withdrawalsRoot": "0x7a4ecf19774d15cf9c15adf0dd8e8a250c128b26c9e2ab2a08d6c9c8ffbd104f",
+            "withdrawals": [],
+            "blobGasUsed": "0x0",
+            "excessBlobGas": "0x0",
+            "parentBeaconBlockRoot": "0x95c4dbd5b19f6fe3cbc3183be85ff4e85ebe75c5b4fc911f1c91e5b7a554a685"
+        }"#;
+        asserter.push(MockResponse::Success(serde_json::from_str(canonical_block).unwrap()));
+
+        let resetter = Resetter::new(Arc::new(client), l1_provider, Arc::new(db));
+
+        assert!(resetter.reset().await.is_err());
+    }
+
     #[tokio::test]
     async fn test_reset_db_error() {
         let mut db = MockDb::new();
@@ -257,7 +396,10 @@ mod tests {
         let mut client = MockClient::new();
         client.expect_chain_id().returning(move || Ok(1));
 
-        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
+        let asserter = Asserter::new();
+        let transport = MockTransport::new(asserter.clone());
+        let l1_provider = RootProvider::<Ethereum>::new(RpcClient::new(transport, false));
+        let resetter = Resetter::new(Arc::new(client), l1_provider, Arc::new(db));
 
         assert!(resetter.reset().await.is_err());
     }
@@ -279,7 +421,10 @@ mod tests {
             .expect_block_ref_by_number()
             .returning(|_| Err(ClientError::Authentication(AuthenticationError::InvalidHeader)));
 
-        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
+        let asserter = Asserter::new();
+        let transport = MockTransport::new(asserter.clone());
+        let l1_provider = RootProvider::<Ethereum>::new(RpcClient::new(transport, false));
+        let resetter = Resetter::new(Arc::new(client), l1_provider, Arc::new(db));
 
         assert!(resetter.reset().await.is_err());
     }
@@ -322,11 +467,52 @@ mod tests {
             .with(predicate::eq(last_valid_derived_block.number))
             .returning(move |_| Ok(last_valid_derived_block));
 
+        db.expect_derived_to_source()
+            .with(predicate::eq(last_valid_derived_block.id()))
+            .returning(move |_| Ok(prev_source_block));
+
+        let asserter = Asserter::new();
+        let transport = MockTransport::new(asserter.clone());
+        let l1_provider = RootProvider::<Ethereum>::new(RpcClient::new(transport, false));
+
+        let canonical_block = r#"{
+            "number": "100",
+            "hash": "0x0808080808080808080808080808080808080808080808080808080808080808",
+            "mixHash": "0x24900fb3da77674a861c428429dce0762707ecb6052325bbd9b3c64e74b5af9d",
+            "parentHash": "0x1f68ac259155e2f38211ddad0f0a15394d55417b185a93923e2abe71bb7a4d6d",
+            "nonce": "0x378da40ff335b070",
+            "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
+            "logsBloom": "0x00000000000000100000004080000000000500000000000000020000100000000800001000000004000001000000000000000800040010000020100000000400000010000000000000000040000000000000040000000000000000000000000000000400002400000000000000000000000000000004000004000000000000840000000800000080010004000000001000000800000000000000000000000000000000000800000000000040000000020000000000000000000800000400000000000000000000000600000400000000002000000000000000000000004000000000000000100000000000000000000000000000000000040000900010000000",
+            "transactionsRoot":"0x4d0c8e91e16bdff538c03211c5c73632ed054d00a7e210c0eb25146c20048126",
+            "stateRoot": "0x91309efa7e42c1f137f31fe9edbe88ae087e6620d0d59031324da3e2f4f93233",
+            "receiptsRoot": "0x68461ab700003503a305083630a8fb8d14927238f0bc8b6b3d246c0c64f21f4a",
+            "miner":"0xb42b6c4a95406c78ff892d270ad20b22642e102d",
+            "difficulty": "0x66e619a",
+            "totalDifficulty": "0x1e875d746ae",
+            "extraData": "0xd583010502846765746885676f312e37856c696e7578",
+            "size": "0x334",
+            "gasLimit": "0x47e7c4",
+            "gasUsed": "0x37993",
+            "timestamp": "0x5835c54d",
+            "uncles": [],
+            "transactions": [
+                "0xa0807e117a8dd124ab949f460f08c36c72b710188f01609595223b325e58e0fc",
+                "0xeae6d797af50cb62a596ec3939114d63967c374fa57de9bc0f4e2b576ed6639d"
+            ],
+            "baseFeePerGas": "0x7",
+            "withdrawalsRoot": "0x7a4ecf19774d15cf9c15adf0dd8e8a250c128b26c9e2ab2a08d6c9c8ffbd104f",
+            "withdrawals": [],
+            "blobGasUsed": "0x0",
+            "excessBlobGas": "0x0",
+            "parentBeaconBlockRoot": "0x95c4dbd5b19f6fe3cbc3183be85ff4e85ebe75c5b4fc911f1c91e5b7a554a685"
+        }"#;
+        asserter.push(MockResponse::Success(serde_json::from_str(canonical_block).unwrap()));
+
         db.expect_get_super_head().returning(move || Ok(super_head));
 
         client.expect_reset().times(1).returning(|_, _, _, _, _| Ok(()));
 
-        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
+        let resetter = Resetter::new(Arc::new(client), l1_provider, Arc::new(db));
 
         assert!(resetter.reset().await.is_ok());
     }
@@ -342,6 +528,48 @@ mod tests {
                 source: super_head.l1_source.unwrap(),
             })
         });
+
+        db.expect_derived_to_source()
+            .with(predicate::eq(super_head.local_safe.unwrap().id()))
+            .returning(move |_| Ok(super_head.l1_source.unwrap()));
+
+        let asserter = Asserter::new();
+        let transport = MockTransport::new(asserter.clone());
+        let l1_provider = RootProvider::<Ethereum>::new(RpcClient::new(transport, false));
+
+        let canonical_block = r#"{
+            "number": "100",
+            "hash": "0x3636363636363636363636363636363636363636363636363636363636363636",
+            "mixHash": "0x24900fb3da77674a861c428429dce0762707ecb6052325bbd9b3c64e74b5af9d",
+            "parentHash": "0x1f68ac259155e2f38211ddad0f0a15394d55417b185a93923e2abe71bb7a4d6d",
+            "nonce": "0x378da40ff335b070",
+            "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
+            "logsBloom": "0x00000000000000100000004080000000000500000000000000020000100000000800001000000004000001000000000000000800040010000020100000000400000010000000000000000040000000000000040000000000000000000000000000000400002400000000000000000000000000000004000004000000000000840000000800000080010004000000001000000800000000000000000000000000000000000800000000000040000000020000000000000000000800000400000000000000000000000600000400000000002000000000000000000000004000000000000000100000000000000000000000000000000000040000900010000000",
+            "transactionsRoot":"0x4d0c8e91e16bdff538c03211c5c73632ed054d00a7e210c0eb25146c20048126",
+            "stateRoot": "0x91309efa7e42c1f137f31fe9edbe88ae087e6620d0d59031324da3e2f4f93233",
+            "receiptsRoot": "0x68461ab700003503a305083630a8fb8d14927238f0bc8b6b3d246c0c64f21f4a",
+            "miner":"0xb42b6c4a95406c78ff892d270ad20b22642e102d",
+            "difficulty": "0x66e619a",
+            "totalDifficulty": "0x1e875d746ae",
+            "extraData": "0xd583010502846765746885676f312e37856c696e7578",
+            "size": "0x334",
+            "gasLimit": "0x47e7c4",
+            "gasUsed": "0x37993",
+            "timestamp": "0x5835c54d",
+            "uncles": [],
+            "transactions": [
+                "0xa0807e117a8dd124ab949f460f08c36c72b710188f01609595223b325e58e0fc",
+                "0xeae6d797af50cb62a596ec3939114d63967c374fa57de9bc0f4e2b576ed6639d"
+            ],
+            "baseFeePerGas": "0x7",
+            "withdrawalsRoot": "0x7a4ecf19774d15cf9c15adf0dd8e8a250c128b26c9e2ab2a08d6c9c8ffbd104f",
+            "withdrawals": [],
+            "blobGasUsed": "0x0",
+            "excessBlobGas": "0x0",
+            "parentBeaconBlockRoot": "0x95c4dbd5b19f6fe3cbc3183be85ff4e85ebe75c5b4fc911f1c91e5b7a554a685"
+        }"#;
+        asserter.push(MockResponse::Success(serde_json::from_str(canonical_block).unwrap()));
+
         db.expect_get_super_head().returning(move || Ok(super_head));
 
         let mut client = MockClient::new();
@@ -351,7 +579,7 @@ mod tests {
             Err(ClientError::Authentication(AuthenticationError::InvalidJwt))
         });
 
-        let resetter = Resetter::new(Arc::new(client), Arc::new(db));
+        let resetter = Resetter::new(Arc::new(client), l1_provider, Arc::new(db));
 
         assert!(resetter.reset().await.is_err());
     }
```
