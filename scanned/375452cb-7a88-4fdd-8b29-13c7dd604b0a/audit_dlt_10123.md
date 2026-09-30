# [?] fix: avoid replay profile zero-duration panic (#5217)

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2026-05-29
Source: https://github.com/nervosnetwork/ckb/commit/4141cea1fa6f5c21d4d4e8a1ed2b433dd087b0ad
Type: security-commit

## Details
fix: avoid replay profile zero-duration panic (#5217)

## Patch
### ckb-bin/src/subcommand/replay.rs
```diff
@@ -87,11 +87,14 @@ fn profile(shared: Shared, chain_controller: ChainController, from: Option<u64>,
             duration, MIN_PROFILING_TIME
         );
     }
+    let tps = if duration.as_secs() == 0 {
+        0
+    } else {
+        tx_count as u64 / duration.as_secs()
+    };
     println!(
         "\n----------------------------\nEnd profiling, duration:{:?}, txs:{}, tps:{}\n----------------------------",
-        duration,
-        tx_count,
-        tx_count as u64 / duration.as_secs()
+        duration, tx_count, tps
     );
 }
 
```
