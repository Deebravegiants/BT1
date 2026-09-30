# [?] Avoid integer overflow when argument is too large (#307)

## Summary
Severity: Unknown
Chain: ZK
Component: arkworks-rs/algebra
Published: 2021-08-14
Source: https://github.com/arkworks-rs/algebra/commit/90f9adc9748fcf88bba4dfa951d478ac09d489e0
Type: security-commit

## Details
Avoid integer overflow when argument is too large (#307)

## Patch
### poly/src/domain/radix2/mod.rs
```diff
@@ -53,7 +53,7 @@ impl<F: FftField> EvaluationDomain<F> for Radix2EvaluationDomain<F> {
         let size = if num_coeffs.is_power_of_two() {
             num_coeffs as u64
         } else {
-            num_coeffs.next_power_of_two() as u64
+            num_coeffs.checked_next_power_of_two()? as u64
         };
         let log_size_of_group = size.trailing_zeros();
 
@@ -82,7 +82,7 @@ impl<F: FftField> EvaluationDomain<F> for Radix2EvaluationDomain<F> {
     }
 
     fn compute_size_of_domain(num_coeffs: usize) -> Option<usize> {
-        let size = num_coeffs.next_power_of_two();
+        let size = num_coeffs.checked_next_power_of_two()?;
         if size.trailing_zeros() > F::FftParams::TWO_ADICITY {
             None
         } else {
```
