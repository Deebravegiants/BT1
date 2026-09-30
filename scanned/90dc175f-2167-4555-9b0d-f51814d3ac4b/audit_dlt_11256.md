# [?] fix: error when overflow check fails at compile time (#11256)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-26
Source: https://github.com/noir-lang/noir/commit/bb123097bfa6a73605c1962ad782ca4bb7fd9856
Type: security-commit

## Details
fix: error when overflow check fails at compile time (#11256)

## Patch
### compiler/noirc_evaluator/src/acir/acir_context/mod.rs
```diff
@@ -1081,12 +1081,16 @@ impl<F: AcirField> AcirContext<F> {
         message: Option<String>,
         predicate: AcirVar,
     ) -> Result<AcirVar, RuntimeError> {
-        // If `variable` is constant then we don't need to add a constraint.
-        // We _do_ add a constraint if `variable` would fail the range check however so that we throw an error.
+        let mut return_zero = false;
         if let Some(constant) = self.var_to_expression(variable)?.to_const() {
+            // If `variable` is constant and fits in the bit_size range
+            // then we don't need to add a constraint.
             if constant.num_bits() <= bit_size {
                 return Ok(variable);
             }
+            // The range check is ensured to fail, unless the predicate is false.
+            // In both cases, the return value does not matter and we can return 0.
+            return_zero = true;
         }
         // Under a predicate, a range check must not fail, so we
         // range check `predicate * variable` instead.
@@ -1100,7 +1104,12 @@ impl<F: AcirField> AcirContext<F> {
                 .assertion_payloads
                 .insert(self.acir_ir.last_acir_opcode_location(), payload);
         }
-        Ok(predicate_range)
+        if return_zero {
+            let zero = self.add_constant(F::zero());
+            Ok(zero)
+        } else {
+            Ok(predicate_range)
+        }
     }
 
     /// Returns an `AcirVar` which will be constrained to be lhs mod 2^{rhs}
```

### compiler/noirc_evaluator/src/acir/tests/instructions.rs
```diff
@@ -1,7 +1,6 @@
 use acvm::assert_circuit_snapshot;
 
 use crate::acir::tests::ssa_to_acir_program;
-
 mod binary;
 
 #[test]
@@ -361,3 +360,18 @@ fn truncate_underflow() {
     ";
     let _ = ssa_to_acir_program(src);
 }
+
+/// The underflow of v0 should not trigger a compile time error,
+/// nor a xor black box input error.
+#[test]
+fn regression_11249() {
+    let src = "
+    acir(inline) fn main f0 {
+      b0():
+        v0 = sub u64 162, u64 7089289267698293936
+        v1 = xor v0, u64 12326866836579951866
+        return v1
+    }
+    ";
+    let _ = ssa_to_acir_program(src);
+}
```

### compiler/noirc_evaluator/src/acir/tests/mod.rs
```diff
@@ -16,6 +16,7 @@ use std::collections::BTreeMap;
 use crate::{
     acir::{acir_context::BrilligStdLib, ssa::codegen_acir},
     brillig::{Brillig, BrilligOptions, brillig_ir::artifact::GeneratedBrillig},
+    errors::RuntimeError,
     ssa::{
         ArtifactsAndWarnings, combine_artifacts, interpreter::value::Value, ir::types::NumericType,
         ssa_gen::Ssa,
@@ -36,6 +37,11 @@ fn ssa_to_acir_program(src: &str) -> Program<FieldElement> {
 }
 
 fn ssa_to_acir_program_with_debug_info(src: &str) -> (Program<FieldElement>, Vec<DebugInfo>) {
+    try_ssa_to_acir(src).expect("Should compile manually written SSA into ACIR")
+}
+
+/// Attempts to convert SSA to ACIR, returning the error if compilation fails.
+fn try_ssa_to_acir(src: &str) -> Result<(Program<FieldElement>, Vec<DebugInfo>), RuntimeError> {
     let ssa = Ssa::from_str(src).unwrap();
     let arg_size_and_visibilities = ssa
         .functions
@@ -57,10 +63,8 @@ fn ssa_to_acir_program_with_debug_info(src: &str) -> (Program<FieldElement>, Vec
 
     let brillig = ssa.to_brillig(&BrilligOptions::default());
 
-    let (acir_functions, brillig_functions, _) = ssa
-        .generate_entry_point_index()
-        .into_acir(&brillig, &BrilligOptions::default())
-        .expect("Should compile manually written SSA into ACIR");
+    let (acir_functions, brillig_functions, _) =
+        ssa.generate_entry_point_index().into_acir(&brillig, &BrilligOptions::default())?;
 
     let artifacts =
         ArtifactsAndWarnings((acir_functions, brillig_functions, BTreeMap::default()), vec![]);
@@ -73,7 +77,7 @@ fn ssa_to_acir_program_with_debug_info(src: &str) -> (Program<FieldElement>, Vec
     );
     let program = program_artifact.program;
     let debug = program_artifact.debug;
-    (program, debug)
+    Ok((program, debug))
 }
 
 #[test]
```
