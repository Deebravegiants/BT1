# [?] Fix test random panic

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-04-10
Source: https://github.com/starcoinorg/starcoin/commit/ad15c188ad60e80931faed99c325d7816dccc61b
Type: security-commit

## Details
Fix test random panic
panic with "json-rpc: signal: 4, SIGILL: illegal instruction"

## Patch
### miner/src/miner_client.rs
```diff
@@ -208,9 +208,29 @@ mod test {
         ::logger::init_for_test();
         let mut system = System::new("test");
         system.block_on(async {
+            let conf = Arc::new(NodeConfig::random_for_test());
+            let mut miner = Miner::<ArgonConsensusHeader>::new(BusActor::launch(), conf);
+            let stratum = {
+                let addr = "127.0.0.1:9000".parse().unwrap();
+                let dispatcher = Arc::new(StratumManager::new(miner.clone()));
+                Stratum::start(&addr, dispatcher, None).unwrap()
+            };
             let actor = MinerClientActor::<ArgonConsensus>::new("127.0.0.1:9000".parse().unwrap());
             actor.start();
-            let _ = async_std::future::timeout(Duration::from_secs(7), prepare()).await;
+            let mine_ctx = {
+                let header = BlockHeader::default();
+                let body = BlockBody::default();
+                let block = Block::new(header, body);
+                let mut block_template = BlockTemplate::from_block(block);
+                block_template.difficult = U256::max_value();
+                MineCtx::new(block_template)
+            };
+            Delay::new(Duration::from_millis(3000)).await;
+            miner.set_mint_job(mine_ctx);
+            for _ in 1..10 {
+                stratum.push_work_all(miner.get_mint_job()).unwrap();
+                Delay::new(Duration::from_millis(500)).await;
+            }
         });
     }
 }
```
