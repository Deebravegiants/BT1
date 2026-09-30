# [?] fix: avoid possible overflow during truncation (#10841)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-12-08
Source: https://github.com/noir-lang/noir/commit/9a5ea6f3cae79e2a0b83082b93462d28fce61151
Type: security-commit

## Details
fix: avoid possible overflow during truncation (#10841)

## Patch
### compiler/noirc_evaluator/src/acir/mod.rs
```diff
@@ -848,6 +848,13 @@ impl<'a> Context<'a> {
                     // for FieldElements. Furthermore, adding a power of two
                     // would be incorrect for a FieldElement (cf. #8519).
                     if max_bit_size < FieldElement::max_num_bits() {
+                        // When max_bit_size is max_num_bits() - 1, adding
+                        // 2**max_bit_size to an element of max_bit_size bits
+                        // gives an element of max_num_bits() bits which may overflow
+                        assert!(
+                            max_bit_size != FieldElement::max_num_bits() - 1,
+                            "potential underflow in subtraction when max_bit_size is {max_bit_size}"
+                        );
                         let integer_modulus = power_of_two::<FieldElement>(max_bit_size);
                         let integer_modulus = self.acir_context.add_constant(integer_modulus);
                         var = self.acir_context.add_var(var, integer_modulus)?;
```

### compiler/noirc_evaluator/src/acir/tests/instructions.rs
```diff
@@ -347,3 +347,17 @@ fn make_array() {
     ASSERT w4 = 10
     ");
 }
+
+#[test]
+#[should_panic(expected = "potential underflow in subtraction when max_bit_size is 253")]
+fn truncate_underflow() {
+    let src = "
+    acir(inline) fn main f0 {
+      b0(v0: Field, v1: Field):
+        v2 = sub v0, v1
+        v3 = truncate v2 to 6 bits, max_bit_size: 253
+        return v3
+    }
+    ";
+    let _ = ssa_to_acir_program(src);
+}
```
