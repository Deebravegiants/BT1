# [?] fix: check for signed division overflow (#9857)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-16
Source: https://github.com/noir-lang/noir/commit/72c5842a449b93a1cd2959d2fa0bccd4a62e2c5b
Type: security-commit

## Details
fix: check for signed division overflow (#9857)

## Patch
### compiler/noirc_evaluator/src/acir/acir_context/mod.rs
```diff
@@ -1169,6 +1169,18 @@ impl<F: AcirField, B: BlackBoxFunctionSolver<F>> AcirContext<F, B> {
         let r_is_not_0 = self.not_var(r_is_0, AcirType::unsigned(1))?;
         let remainder = self.mul_var(remainder, r_is_not_0)?;
 
+        // The quotient must be a valid signed integer.
+        // For instance -128/-1 = 128, but 128 is not a valid i8
+        // Because it is the only possible overflow that can happen due to signed representation,
+        // we simply check for this case: quotient is negative, or distinct from 2^{bit_size-1}
+        // Indeed, negative quotient cannot 'overflow' because the division will not increase its absolute value
+        let assert_message =
+            self.generate_assertion_message_payload("Attempt to divide with overflow".to_string());
+        let unsigned = self.not_var(q_sign, AcirType::unsigned(1))?;
+        // We just use `unsigned` for the predicate of assert_neq_var because if the `predicate` is false, the quotient
+        // we get from the unsigned division under the predicate will not be 2^{bit_size-1} anyways.
+        self.assert_neq_var(quotient, max_power_of_two, unsigned, Some(assert_message))?;
+
         Ok((quotient, remainder))
     }
 
```

### compiler/noirc_evaluator/src/acir/tests/mod.rs
```diff
@@ -1082,6 +1082,33 @@ fn test_operators(
     }
 }
 
+#[test]
+// Regression for https://github.com/noir-lang/noir/issues/9847
+fn signed_div_overflow() {
+    // Test that check -128 / -1 overflow for i8
+    let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0(v1: i8, v2: i8):
+            v3 = div v1, v2
+            return
+        }
+        "#;
+
+    let ssa = Ssa::from_str(src).unwrap();
+    let inputs = vec![FieldElement::from(128_u128), FieldElement::from(255_u128)];
+    let inputs = inputs
+        .into_iter()
+        .enumerate()
+        .map(|(i, f)| (Witness(i as u32), f))
+        .collect::<BTreeMap<_, _>>();
+    let initial_witness = WitnessMap::from(inputs);
+    let output = None;
+
+    // acir execution should fail to divide -128 / -1
+    let acir_execution_result = execute_ssa(ssa, initial_witness.clone(), output.as_ref());
+    assert!(matches!(acir_execution_result, (ACVMStatus::Failure(_), _)));
+}
+
 proptest! {
 #[test]
 fn test_binary_on_field(lhs in 0u128.., rhs in 0u128..) {
```
