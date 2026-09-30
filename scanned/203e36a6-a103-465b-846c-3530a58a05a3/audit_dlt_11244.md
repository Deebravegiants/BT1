# [?] fix: prevent potential overflow for i128 (#12115)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-03
Source: https://github.com/noir-lang/noir/commit/5f93d49ca17c9da73ec03fb0efcac25bdd3f46cd
Type: security-commit

## Details
fix: prevent potential overflow for i128 (#12115)

## Patch
### compiler/noirc_evaluator/src/ssa/opt/expand_signed_math.rs
```diff
@@ -148,7 +148,9 @@ impl Context<'_, '_, '_> {
         // negative value by -1. For example dividing -128 i8 by -1 would give 128, but that
         // does not fit i8. So the first thing we do is check for this case.
         let min_negative_value = self.numeric_constant(1_u128 << (bit_size - 1), unsigned_typ);
-        let minus_one = self.numeric_constant((1_u128 << bit_size) - 1, unsigned_typ);
+        let max_for_bit_size =
+            if bit_size == 128 { u128::MAX - 1 } else { (1_u128 << bit_size) - 1 };
+        let minus_one = self.numeric_constant(max_for_bit_size, unsigned_typ);
         let lhs_is_min_negative_value =
             self.insert_binary(lhs_unsigned, BinaryOp::Eq, min_negative_value);
         let rhs_is_minus_one = self.insert_binary(rhs_unsigned, BinaryOp::Eq, minus_one);
```
