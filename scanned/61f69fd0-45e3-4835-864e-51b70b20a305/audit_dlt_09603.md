# [?] Fix possible underflow in `try_acquire_cost`. (#1437)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-05-16
Source: https://github.com/Conflux-Chain/conflux-rust/commit/0c12ead420b2c292de2d887a853ee0bd770b98b5
Type: security-commit

## Details
Fix possible underflow in `try_acquire_cost`. (#1437)

* Fix possible underflow in `try_acquire_cost`.

* Fix tests.

## Patch
### util/throttling/src/token_bucket.rs
```diff
@@ -161,14 +161,26 @@ impl TokenBucket {
         }
 
         // tokens not enough and throttled
-        let cpu_recharge_secs = ((cpu_cost - self.cpu_tokens.cur_tokens) as f64
-            / self.cpu_tokens.recharge_rate as f64)
-            .ceil() as u64;
-        let message_recharge_secs =
+        let cpu_recharge_secs = if cpu_cost > self.cpu_tokens.cur_tokens {
+            ((cpu_cost - self.cpu_tokens.cur_tokens) as f64
+                / self.cpu_tokens.recharge_rate as f64)
+                .ceil() as u64
+        } else {
+            0
+        };
+        let message_recharge_secs = if message_size_cost
+            > self.message_size_tokens.cur_tokens
+        {
             ((message_size_cost - self.message_size_tokens.cur_tokens) as f64
                 / self.message_size_tokens.recharge_rate as f64)
-                .ceil() as u64;
+                .ceil() as u64
+        } else {
+            0
+        };
         let recharge_secs = max(cpu_recharge_secs, message_recharge_secs);
+        // `refresh` ensures the difference in `self.last_update` and `now` is
+        // less than 1 second, and `recharge_secs` is at least 1 second,
+        // so this will not underflow.
         Err(self.last_update + Duration::from_secs(recharge_secs) - now)
     }
 
```
