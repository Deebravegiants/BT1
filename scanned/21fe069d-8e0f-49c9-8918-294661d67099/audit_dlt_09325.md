# [?] fix: capacity overflow on invariant shrinking (#6819)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-01-16
Source: https://github.com/foundry-rs/foundry/commit/04ccec7ace1687cd8067e2aee8bc3f338107a87a
Type: security-commit

## Details
fix: capacity overflow on invariant shrinking (#6819)

## Patch
### crates/evm/evm/src/executors/invariant/error.rs
```diff
@@ -288,16 +288,17 @@ impl InvariantFuzzError {
         let shrunk_call_indices = Arc::new(RwLock::new((0..calls.len()).collect()));
         let shrink_limit = self.shrink_run_limit - runs;
 
+        let upper_bound = calls.len().saturating_sub(1);
         // We construct either a full powerset (this guarantees we maximally shrunk for the given
         // calls) or a random subset
         let (set_of_indices, is_powerset): (Vec<_>, bool) = if calls.len() <= 64 &&
             2_usize.pow(calls.len() as u32) <= shrink_limit
         {
             // We add the last tx always because thats ultimately what broke the invariant
-            let powerset = (0..calls.len() - 1)
+            let powerset = (0..upper_bound)
                 .powerset()
                 .map(|mut subset| {
-                    subset.push(calls.len() - 1);
+                    subset.push(upper_bound);
                     subset
                 })
                 .collect();
@@ -309,16 +310,16 @@ impl InvariantFuzzError {
                 (0..shrink_limit / 3)
                     .map(|_| {
                         // Select between 1 and calls.len() - 2 number of indices
-                        let amt: usize = rng.gen_range(1..calls.len() - 1);
+                        let amt: usize = rng.gen_range(1..upper_bound);
                         // Construct a random sequence of indices, up to calls.len() - 1 (sample is
                         // exclusive range and we dont include the last tx
                         // because its always included), and amt number of indices
-                        let mut seq = seq::index::sample(&mut rng, calls.len() - 1, amt).into_vec();
+                        let mut seq = seq::index::sample(&mut rng, upper_bound, amt).into_vec();
                         // Sort the indices because seq::index::sample is unordered
                         seq.sort();
                         // We add the last tx always because thats what ultimately broke the
                         // invariant
-                        seq.push(calls.len() - 1);
+                        seq.push(upper_bound);
                         seq
                     })
                     .collect(),
```
