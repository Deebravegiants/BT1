# [?] Avoid underflow when checking the length of `terms`

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2021-11-15
Source: https://github.com/0xPolygonZero/plonky2/commit/799ff26e71c03aec171fa0eb94abec8e11e3549e
Type: security-commit

## Details
Avoid underflow when checking the length of `terms`

## Patch
### src/util/reducing.rs
```diff
@@ -107,7 +107,7 @@ impl<const D: usize> ReducingFactorTarget<D> {
         let l = terms.len();
 
         // For small reductions, use an arithmetic gate.
-        if l - 1 <= ArithmeticExtensionGate::<D>::new_from_config(&builder.config).num_ops {
+        if l <= ArithmeticExtensionGate::<D>::new_from_config(&builder.config).num_ops + 1 {
             let terms_ext = terms
                 .iter()
                 .map(|&t| builder.convert_to_ext(t))
@@ -162,7 +162,7 @@ impl<const D: usize> ReducingFactorTarget<D> {
         let l = terms.len();
 
         // For small reductions, use an arithmetic gate.
-        if l - 1 <= ArithmeticExtensionGate::<D>::new_from_config(&builder.config).num_ops {
+        if l <= ArithmeticExtensionGate::<D>::new_from_config(&builder.config).num_ops + 1 {
             return self.reduce_arithmetic(terms, builder);
         }
 
```
