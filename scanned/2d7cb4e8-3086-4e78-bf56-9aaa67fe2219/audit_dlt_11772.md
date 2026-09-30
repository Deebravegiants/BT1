# [?] Merge pull request #2158 from AleoHQ/fix/finalize-cost-overflow

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-11-10
Source: https://github.com/AleoNet/snarkVM-test/commit/6417f781aa791b5ca4c2d549b382c803eb470a39
Type: security-commit

## Details
Merge pull request #2158 from AleoHQ/fix/finalize-cost-overflow

[TOB] Guard overflow in finalize cost calculation

## Patch
### synthesizer/src/vm/helpers/cost.rs
```diff
@@ -199,5 +199,9 @@ pub fn cost_in_microcredits<N: Network>(finalize: &Finalize<N>) -> Result<u64> {
         Command::BranchEq(_) | Command::BranchNeq(_) => Ok(5_000),
         Command::Position(_) => Ok(1_000),
     };
-    finalize.commands().iter().map(|command| cost(command)).sum()
+    finalize
+        .commands()
+        .iter()
+        .map(cost)
+        .try_fold(0u64, |acc, res| res.and_then(|x| acc.checked_add(x).ok_or(anyhow!("Finalize cost overflowed"))))
 }
```
