# [?] fix(rpc): getblock verbosity 2 side-chain panic (GHSA-x6v8-c2xp-928m) (#10889)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-02
Source: https://github.com/ZcashFoundation/zebra/commit/b5e122f5f9c0aa490a3d5f2e8e4000d2a6023d73
Type: security-commit

## Details
fix(rpc): getblock verbosity 2 side-chain panic (GHSA-x6v8-c2xp-928m) (#10889)

* test(rpc): add regression test for getblock side-chain panic (GHSA-x6v8-c2xp-928m)

* fix(rpc): use i64 for transaction confirmations to avoid side-chain panic (GHSA-x6v8-c2xp-928m)

* fix(rpc): resolve clippy and rustfmt warnings

Remove unused `mut` on mempool mock and apply rustfmt formatting.

---------

Co-authored-by: Alfredo Garcia <oxarbitrage@gmail.com>

## Patch
### zebra-rpc/src/methods.rs
```diff
@@ -1328,27 +1328,24 @@ where
                 zebra_state::ReadResponse::BlockAndSize(block_and_size) => {
                     let (block, size) = block_and_size.ok_or_misc_error("Block not found")?;
                     let block_time = block.header.time;
-                    let transactions =
-                        block
-                            .transactions
-                            .iter()
-                            .map(|tx| {
-                                GetBlockTransaction::Object(Box::new(
-                                    TransactionObject::from_transaction(
-                                        tx.clone(),
-                                        Some(height),
-                                        Some(confirmations.try_into().expect(
-                                            "should be less than max block height, i32::MAX",
-                                        )),
-                                        &network,
-                                        Some(block_time),
-                                        Some(hash),
-                                        Some(true),
-                                        tx.hash(),
-                                    ),
-                                ))
-                            })
-                            .collect();
+                    let transactions = block
+                        .transactions
+                        .iter()
+                        .map(|tx| {
+                            GetBlockTransaction::Object(Box::new(
+                                TransactionObject::from_transaction(
+                                    tx.clone(),
+                                    Some(height),
+                                    Some(confirmations),
+                                    &network,
+                                    Some(block_time),
+                                    Some(hash),
+                                    Some(true),
+                                    tx.hash(),
+                                ),
+                            ))
+                        })
+                        .collect();
                     (transactions, Some(size))
                 }
                 _ => unreachable!("unmatched response to a transaction_ids_for_block request"),
@@ -1791,7 +1788,7 @@ where
                         AnyTx::Mined(mined) if in_best_chain => (
                             mined.tx.clone(),
                             Some(mined.height),
-                            Some(mined.confirmations),
+                            Some(mined.confirmations.into()),
                             Some(mined.block_time),
                         ),
                         _ => {
@@ -1834,7 +1831,7 @@ where
                                 TransactionObject::from_transaction(
                                     tx.tx.clone(),
                                     Some(tx.height),
-                                    Some(tx.confirmations),
+                                    Some(tx.confirmations.into()),
                                     &self.network,
                                     // TODO: Performance gain:
                                     // https://github.com/ZcashFoundation/zebra/pull/9458#discussion_r2059352752
```

### zebra-rpc/src/methods/tests/vectors.rs
```diff
@@ -831,6 +831,99 @@ async fn rpc_getblock_missing_error() {
     assert!(rpc_tx_queue_task_result.is_none());
 }
 
+/// Regression test for GHSA-x6v8-c2xp-928m — panics (aborts) before the fix.
+///
+/// When `Depth` returns `None` (side-chain block), `get_block_header` sets
+/// `confirmations = -1`:
+/// https://github.com/ZcashFoundation/zebra/blob/v5.2.0/zebra-rpc/src/methods.rs#L1508
+/// The old code narrowed that to `u32` via `.try_into().expect()`, which panicked.
+///
+/// The fix changes `TransactionObject.confirmations` from `u32` to `i64`, matching
+/// zcashd's signed `int`:
+/// https://github.com/zcash/zcash/blob/v6.3.0/src/rpc/rawtransaction.cpp#L311
+/// https://github.com/zcash/zcash/blob/v6.3.0/src/rpc/blockchain.cpp#L404
+#[tokio::test(flavor = "multi_thread")]
+async fn rpc_getblock_side_chain_verbosity2_does_not_panic() {
+    let _init_guard = zebra_test::init();
+
+    let block: Arc<Block> = zebra_test::vectors::BLOCK_MAINNET_GENESIS_BYTES
+        .zcash_deserialize_into()
+        .unwrap();
+    let block_hash = block.hash();
+    let block_header = block.header.clone();
+    let block_size = block.zcash_serialized_size();
+
+    let mempool: MockService<_, _, _, BoxError> = MockService::build().for_unit_tests();
+    let state: MockService<_, _, _, BoxError> = MockService::build().for_unit_tests();
+    let mut read_state: MockService<_, _, _, BoxError> = MockService::build()
+        .with_max_request_delay(std::time::Duration::from_secs(5))
+        .for_unit_tests();
+
+    let (_tx, rx) = tokio::sync::watch::channel(None);
+    let (rpc, _rpc_tx_queue) = RpcImpl::new(
+        Mainnet,
+        Default::default(),
+        Default::default(),
+        "0.0.1",
+        "RPC test",
+        Buffer::new(mempool.clone(), 1),
+        Buffer::new(state.clone(), 1),
+        Buffer::new(read_state.clone(), 1),
+        MockService::build().for_unit_tests(),
+        MockSyncStatus::default(),
+        NoChainTip,
+        MockAddressBookPeers::default(),
+        rx,
+        None,
+    );
+
+    let rpc_clone = rpc.clone();
+    let hash_str = block_hash.to_string();
+    let block_future = tokio::spawn(async move { rpc_clone.get_block(hash_str, Some(2u8)).await });
+
+    // get_block_header: BlockHeader, SaplingTree, Depth (None = side chain)
+    read_state
+        .expect_request(ReadRequest::BlockHeader(block_hash.into()))
+        .await
+        .respond(ReadResponse::BlockHeader {
+            header: block_header,
+            hash: block_hash,
+            height: zebra_chain::block::Height(0),
+            next_block_hash: None,
+        });
+    read_state
+        .expect_request_that(|req| matches!(req, ReadRequest::SaplingTree(_)))
+        .await
+        .respond(ReadResponse::SaplingTree(Some(Default::default())));
+    read_state
+        .expect_request(ReadRequest::Depth(block_hash))
+        .await
+        .respond(ReadResponse::Depth(None));
+
+    // get_block: BlockAndSize, OrchardTree, BlockInfo x2
+    read_state
+        .expect_request_that(|req| matches!(req, ReadRequest::BlockAndSize(_)))
+        .await
+        .respond(ReadResponse::BlockAndSize(Some((block, block_size))));
+    read_state
+        .expect_request_that(|req| matches!(req, ReadRequest::OrchardTree(_)))
+        .await
+        .respond(ReadResponse::OrchardTree(Some(Default::default())));
+    read_state
+        .expect_request_that(|req| matches!(req, ReadRequest::BlockInfo(_)))
+        .await
+        .respond(ReadResponse::BlockInfo(None));
+    read_state
+        .expect_request_that(|req| matches!(req, ReadRequest::BlockInfo(_)))
+        .await
+        .respond(ReadResponse::BlockInfo(Some(BlockInfo::default())));
+
+    block_future
+        .await
+        .expect("task should not panic")
+        .expect("getblock should succeed for side-chain blocks");
+}
+
 #[tokio::test(flavor = "multi_thread")]
 async fn rpc_getblockheader() {
     let _init_guard = zebra_test::init();
@@ -1146,7 +1239,7 @@ async fn rpc_getrawtransaction() {
                 panic!("unexpected response to Depth request");
             };
 
-            let expected_confirmations = 1 + depth.expect("depth should be Some");
+            let expected_confirmations: i64 = (1 + depth.expect("depth should be Some")).into();
 
             (confirmations, expected_confirmations)
         }
```

### zebra-rpc/src/methods/types/transaction.rs
```diff
@@ -290,7 +290,7 @@ pub struct TransactionObject {
     /// mempool.
     #[serde(skip_serializing_if = "Option::is_none")]
     #[getter(copy)]
-    pub(crate) confirmations: Option<u32>,
+    pub(crate) confirmations: Option<i64>,
 
     /// Transparent inputs of the transaction.
     #[serde(rename = "vin")]
@@ -794,7 +794,7 @@ impl TransactionObject {
     pub fn from_transaction(
         tx: Arc<Transaction>,
         height: Option<block::Height>,
-        confirmations: Option<u32>,
+        confirmations: Option<i64>,
         network: &Network,
         block_time: Option<DateTime<Utc>>,
         block_hash: Option<block::Hash>,
```
