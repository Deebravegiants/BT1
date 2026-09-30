# [?] streamer: fix stake quota overflow in stream throttling (#14799)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-08-24
Source: https://github.com/anza-xyz/agave/commit/87ec9667119896409dadb9f00cb4b7113ca4c973
Type: security-commit

## Details
streamer: fix stake quota overflow in stream throttling (#14799)

streamer: prevent stake quota overflow

## Patch
### streamer/src/nonblocking/stream_throttle.rs
```diff
@@ -175,9 +175,10 @@ impl StakedStreamLoadEMA {
                 if self.staked_throttling_enabled.load(Ordering::Relaxed) {
                     // 1 is added to `max_unstaked_load_in_throttling_window` to guarantee that staked
                     // clients get at least 1 more number of streams than unstaked connections.
-                    self.max_staked_load_in_throttling_window
-                        .saturating_mul(stake)
-                        .checked_div(total_stake)
+                    u128::from(self.max_staked_load_in_throttling_window)
+                        .saturating_mul(u128::from(stake))
+                        .checked_div(u128::from(total_stake))
+                        .and_then(|capacity| u64::try_from(capacity).ok())
                         .unwrap_or(self.max_unstaked_load_in_throttling_window + 1)
                         .max(self.max_unstaked_load_in_throttling_window + 1)
                 } else {
```
