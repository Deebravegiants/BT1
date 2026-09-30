# [?] Fix overflow in `SerializingChallenger64` (#486)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2024-09-30
Source: https://github.com/Plonky3/Plonky3/commit/6aa5e089c88c7d153b97f4f11c987d3b031d4deb
Type: security-commit

## Details
Fix overflow in `SerializingChallenger64` (#486)

* Fix overflow in `SerializingChallenger64`

* Use wider int arithmetic instead, a bit simpler

## Patch
### challenger/src/serializing_challenger.rs
```diff
@@ -96,7 +96,8 @@ where
     fn sample(&mut self) -> EF {
         let modulus = F::ORDER_U64 as u32;
         let log_size = log2_ceil_u64(F::ORDER_U64);
-        let pow_of_two_bound = (1 << log_size) - 1;
+        // We use u64 to avoid overflow in the case that log_size = 32.
+        let pow_of_two_bound = ((1u64 << log_size) - 1) as u32;
         // Perform rejection sampling over the uniform range (0..log2_ceil(p))
         let sample_base = |inner: &mut Inner| loop {
             let value = u32::from_le_bytes(inner.sample_array::<4>());
@@ -193,8 +194,10 @@ where
 {
     fn sample(&mut self) -> EF {
         let modulus = F::ORDER_U64;
-        let log_size = log2_ceil_u64(F::ORDER_U64);
-        let pow_of_two_bound = (1 << log_size) - 1;
+        let log_size = log2_ceil_u64(F::ORDER_U64) as u32;
+        // We use u128 to avoid overflow in the case that log_size = 64.
+        let pow_of_two_bound = ((1u128 << log_size) - 1) as u64;
+
         // Perform rejection sampling over the uniform range (0..log2_ceil(p))
         let sample_base = |inner: &mut Inner| loop {
             let value = u64::from_le_bytes(inner.sample_array::<8>());
```
