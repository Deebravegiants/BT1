# [?] fix(ckb-bin): replay command crash if profile time under 1 second

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2022-02-25
Source: https://github.com/nervosnetwork/ckb/commit/79370b24fb2f0666ba0f6b9779c717472d6134c4
Type: security-commit

## Details
fix(ckb-bin): replay command crash if profile time under 1 second

subcommand replay crash due to divide profile_time(zero) if the time is less than 1 second

## Patch
### ckb-bin/src/subcommand/replay.rs
```diff
@@ -9,6 +9,8 @@ use ckb_store::ChainStore;
 use ckb_verification_traits::Switch;
 use std::sync::Arc;
 
+const MIN_PROFILING_TIME: u64 = 5;
+
 pub fn replay(args: ReplayArgs, async_handle: Handle) -> Result<(), ExitCode> {
     let shared_builder = SharedBuilder::new(
         &args.config.bin_name,
@@ -75,12 +77,25 @@ fn profile(shared: Shared, mut chain: ChainService, from: Option<u64>, to: Optio
     let now = std::time::Instant::now();
     let tx_count = process_range_block(&shared, &mut chain, from..=to);
     let duration = std::time::Instant::now().saturating_duration_since(now);
-    println!(
-        "end profiling, duration {:?} txs {} tps {}",
-        duration,
-        tx_count,
-        tx_count as u64 / duration.as_secs()
-    );
+    if duration.as_secs() >= MIN_PROFILING_TIME {
+        println!(
+            "\n----------------------------\nEnd profiling, duration:{:?}, txs:{}, tps:{}\n----------------------------",
+            duration,
+            tx_count,
+            tx_count as u64 / duration.as_secs()
+        );
+    } else {
+        println!(
+            concat!(
+                "----------------------------\n",
+                r#"Profiling with too short time({:?}) is inaccurate and referential; it's recommended to modify"#,
+                "\n",
+                r#"parameters(--from, --to) to increase block range, to make profiling time is greater than "#,
+                "{} seconds\n----------------------------",
+            ),
+            duration, MIN_PROFILING_TIME
+        );
+    }
 }
 
 fn process_range_block(
```
