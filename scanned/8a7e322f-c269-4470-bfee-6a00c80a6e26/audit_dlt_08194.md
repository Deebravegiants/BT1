# [?] fix(votor): prevent overflow when scaling `delta_timeout` (#12772)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-05-27
Source: https://github.com/anza-xyz/agave/commit/875146286a56d529075e8fc7fa7e600a1cc2dabd
Type: security-commit

## Details
fix(votor): prevent overflow when scaling `delta_timeout` (#12772)

## Patch
### votor/src/timer_manager/timers.rs
```diff
@@ -42,8 +42,12 @@ struct TimeoutConfig {
 impl TimeoutConfig {
     fn scaled(&self, slot: Slot, standstill_slot: Option<Slot>) -> TimeoutConfig {
         let multiplier = calculate_timeout_multiplier(slot, standstill_slot);
+        let delta_timeout = Duration::try_from_secs_f64(
+            (self.delta_timeout.as_secs_f64() * multiplier).clamp(0.0, MAX_TIMEOUT.as_secs_f64()),
+        )
+        .unwrap_or(MAX_TIMEOUT);
         TimeoutConfig {
-            delta_timeout: self.delta_timeout.mul_f64(multiplier).min(MAX_TIMEOUT),
+            delta_timeout,
             delta_first_slice: self.delta_first_slice,
             delta_block: self.delta_block,
         }
```
