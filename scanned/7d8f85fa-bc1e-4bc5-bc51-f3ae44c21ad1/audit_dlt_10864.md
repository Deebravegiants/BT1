# [?] [fix] dev network On demand produce block panic. https://github.com/starcoinorg/starcoin/issues/196

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-04-15
Source: https://github.com/starcoinorg/starcoin/commit/796197fbaedccdd303e41150bd34a78ef27ae1e0
Type: security-commit

## Details
[fix] dev network On demand produce block panic. https://github.com/starcoinorg/starcoin/issues/196

## Patch
### consensus/src/dummy.rs
```diff
@@ -8,7 +8,7 @@ use rand::prelude::*;
 use std::convert::TryFrom;
 use std::sync::Arc;
 use std::thread;
-use std::time::{Duration, SystemTime, UNIX_EPOCH};
+use std::time::Duration;
 use traits::ChainReader;
 use traits::{Consensus, ConsensusHeader};
 use types::block::BlockHeader;
@@ -41,17 +41,19 @@ impl Consensus for DummyConsensus {
     type ConsensusHeader = DummyHeader;
 
     fn calculate_next_difficulty(config: Arc<NodeConfig>, _reader: &dyn ChainReader) -> U256 {
-        config.miner.dev_period.into()
+        let mut rng = rand::thread_rng();
+        // if produce block on demand, use a default wait time.
+        let high: u64 = if config.miner.dev_period == 0 {
+            1000
+        } else {
+            config.miner.dev_period * 1000
+        };
+        let time: u64 = rng.gen_range(1, high);
+        time.into()
     }
 
     fn solve_consensus_header(_header_hash: &[u8], difficulty: U256) -> Self::ConsensusHeader {
-        let start = SystemTime::now();
-        let since_the_epoch = start
-            .duration_since(UNIX_EPOCH)
-            .expect("Time went backwards");
-        let mut rng: StdRng = SeedableRng::seed_from_u64(since_the_epoch.as_secs());
-        let df: u64 = difficulty.into();
-        let time: u64 = rng.gen_range(0, df);
+        let time: u64 = difficulty.as_u64();
         debug!("DummyConsensus rand sleep time : {}", time);
         thread::sleep(Duration::from_millis(time));
         DummyHeader {}
```
