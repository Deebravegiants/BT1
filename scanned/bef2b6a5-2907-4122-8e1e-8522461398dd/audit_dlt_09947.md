# [?] Fix sub overflow panic on txrelay flow time check (#385)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2024-01-11
Source: https://github.com/kaspanet/rusty-kaspa/commit/49f671025a8c9603603ffff6d34b1f1ce39d206c
Type: security-commit

## Details
Fix sub overflow panic on txrelay flow time check (#385)

## Patch
### protocol/flows/src/v5/txrelay/flow.rs
```diff
@@ -91,7 +91,7 @@ impl RelayTransactionsFlow {
         loop {
             // TODO: Extract should_throttle logic to a separate function
             let now = unix_now();
-            if now - last_checked_time > 10000 {
+            if now > last_checked_time + 10000 {
                 let next_snapshot = self.ctx.mining_manager().clone().snapshot();
                 let snapshot_delta = &next_snapshot - &curr_snapshot;
 
```
