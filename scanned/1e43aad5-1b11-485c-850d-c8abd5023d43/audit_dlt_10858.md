# [?] [test]fix state_sync_test panic.

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-05-19
Source: https://github.com/starcoinorg/starcoin/commit/90e6dcb2131a14b0e105a5ffb422d8f9cf362b4c
Type: security-commit

## Details
[test]fix state_sync_test panic.

## Patch
### Cargo.lock
```diff
@@ -6188,6 +6188,7 @@ dependencies = [
  "starcoin-txpool-api",
  "starcoin-types",
  "starcoin-wallet-api",
+ "stest",
  "tokio 0.2.20",
 ]
 
```

### sync/Cargo.toml
```diff
@@ -45,4 +45,5 @@ miner = {path = "../miner", package="starcoin-miner" }
 hex = "0.4.2"
 starcoin-wallet-api = { path = "../wallet/api"}
 libp2p = "0.18.1"
+stest = { path = "../commons/stest"}
 
```

### sync/tests/state_sync_test.rs
```diff
@@ -24,7 +24,7 @@ use traits::ChainAsyncService;
 use txpool::{TxPool, TxPoolService};
 use types::system_events::SyncBegin;
 
-#[test]
+#[stest::test(timeout = 120)]
 fn test_state_sync() {
     ::logger::init_for_test();
     let rt = tokio::runtime::Runtime::new().unwrap();
@@ -116,10 +116,11 @@ fn test_state_sync() {
         );
         MinerClientActor::new(node_config_1.miner.clone()).start();
         Delay::new(Duration::from_secs(30)).await;
-        let block_1 = first_chain.clone().master_head_block().await.unwrap();
-        let number = block_1.header().number();
-        debug!("first chain :{:?}", number);
-        assert!(number > 11);
+        let mut block_1 = first_chain.clone().master_head_block().await.unwrap();
+        while block_1.header().number() <= 11 {
+            Delay::new(Duration::from_secs(5)).await;
+            block_1 = first_chain.clone().master_head_block().await.unwrap();
+        }
 
         ////////////////////////
         // second chain
```
