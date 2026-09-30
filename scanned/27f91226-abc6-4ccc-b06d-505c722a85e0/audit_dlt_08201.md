# [?] fix(random): return Overflow error when sum of weights exceed u64::MAX (#9652)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-12-19
Source: https://github.com/anza-xyz/agave/commit/bcaeadd992fbb8daab77801af96c962f24791fd0
Type: security-commit

## Details
fix(random): return Overflow error when sum of weights exceed u64::MAX (#9652)

## Patch
### random/src/weighted.rs
```diff
@@ -27,7 +27,7 @@ impl WeightedU64Index {
         // chosen weight.
         let mut total_weight = 0u64;
         for weight in weights.iter_mut() {
-            total_weight = total_weight.saturating_add(*weight);
+            total_weight = total_weight.checked_add(*weight).ok_or(Error::Overflow)?;
             *weight = total_weight;
         }
         if weights.pop().is_none() {
@@ -105,5 +105,9 @@ mod tests {
             WeightedU64Index::new(vec![0, 0, 0, 0, 0]),
             Err(Error::InsufficientNonZero)
         );
+        assert_matches!(
+            WeightedU64Index::new(vec![u64::MAX / 3, u64::MAX / 2, 0, u64::MAX / 3]),
+            Err(Error::Overflow)
+        );
     }
 }
```
