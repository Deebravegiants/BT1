# [?] fix: EXC: Fix metric overflow in tests (#4359)

## Summary
Severity: Unknown
Chain: Internet Computer
Component: dfinity/ic
Published: 2025-03-13
Source: https://github.com/dfinity/ic/commit/c494f861b6f4cfbcc6a811832fcb5a806a03b5e1
Type: security-commit

## Details
fix: EXC: Fix metric overflow in tests (#4359)

The tests are compiled with debug asserts and overflow checks enabled by
default. There are no issues on the mainnet.

See
https://doc.rust-lang.org/rustc/codegen-options/index.html#overflow-checks

## Patch
### rs/execution_environment/src/scheduler/round_schedule.rs
```diff
@@ -414,7 +414,7 @@ impl RoundSchedule {
 
         // Collect the priority of the canisters for this round.
         let mut accumulated_priority_invariant = AccumulatedPriority::default();
-        let mut accumulated_priority_deviation = 0;
+        let mut accumulated_priority_deviation = 0.0;
         for (&canister_id, canister) in canister_states.iter_mut() {
             if is_reset_round {
                 // By default, each canister accumulated priority is set to its compute allocation.
@@ -440,7 +440,7 @@ impl RoundSchedule {
             total_compute_allocation_percent += compute_allocation.as_percent() as i64;
             accumulated_priority_invariant += accumulated_priority;
             accumulated_priority_deviation +=
-                accumulated_priority.get() * accumulated_priority.get();
+                accumulated_priority.get() as f64 * accumulated_priority.get() as f64;
             if !canister.has_input() {
                 canister
                     .system_state
@@ -465,7 +465,7 @@ impl RoundSchedule {
             .set(accumulated_priority_invariant.get());
         metrics
             .scheduler_accumulated_priority_deviation
-            .set((accumulated_priority_deviation as f64 / number_of_canisters as f64).sqrt());
+            .set((accumulated_priority_deviation / number_of_canisters as f64).sqrt());
 
         // Free capacity per canister in multiplied percent.
         // Note, to avoid division by zero when there are no canisters
```
