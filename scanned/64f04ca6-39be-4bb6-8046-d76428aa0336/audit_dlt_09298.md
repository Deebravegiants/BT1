# [?] fix: do not panic if cannot read counterexample (#12467)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-11-05
Source: https://github.com/foundry-rs/foundry/commit/ea9c764629fc1bfd532d99922d0702ef6d21519e
Type: security-commit

## Details
fix: do not panic if cannot read counterexample (#12467)

## Patch
### crates/evm/evm/src/executors/fuzz/mod.rs
```diff
@@ -142,7 +142,7 @@ impl FuzzedExecutor {
         'stop: while continue_campaign(test_data.runs) {
             // If counterexample recorded, replay it first, without incrementing runs.
             let input = if let Some(failure) = self.persisted_failure.take()
-                && func.selector() == failure.calldata[..4]
+                && failure.calldata.get(..4).is_some_and(|selector| func.selector() == selector)
             {
                 failure.calldata.clone()
             } else {
```
