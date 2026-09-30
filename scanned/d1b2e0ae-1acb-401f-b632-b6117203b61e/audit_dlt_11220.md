# [?] fix(ssa): report runtime-only intrinsics in the wrong runtime instead of panicking in codegen (#13660)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-09-17
Source: https://github.com/noir-lang/noir/commit/b3dc84035651dd4fbabf145640886c251d375884
Type: security-commit

## Details
fix(ssa): report runtime-only intrinsics in the wrong runtime instead of panicking in codegen (#13660)

## Patch
### compiler/noirc_evaluator/src/errors.rs
```diff
@@ -120,6 +120,10 @@ pub enum RuntimeError {
         "The return value has {num_witnesses} elements which exceeds the limit of {max_witnesses}"
     )]
     ReturnLimitExceeded { num_witnesses: usize, max_witnesses: usize, call_stack: CallStack },
+    #[error("Cannot call `std::verify_proof_with_type` in unconstrained context")]
+    RecursiveAggregationInUnconstrained { call_stack: CallStack },
+    #[error("`{name}` can only be called in unconstrained context")]
+    UnconstrainedOnlyIntrinsicInConstrained { name: String, call_stack: CallStack },
 }
 
 #[derive(Debug, PartialEq, Eq, Clone, Error)]
@@ -171,7 +175,11 @@ impl RuntimeError {
             | RuntimeError::SsaValidationError { call_stack, .. }
             | RuntimeError::ArraySetAliasViolation { call_stack, .. }
             | RuntimeError::CallArgAliasViolation { call_stack, .. }
-            | RuntimeError::ReturnLimitExceeded { call_stack, .. } => call_stack,
+            | RuntimeError::ReturnLimitExceeded { call_stack, .. }
+            | RuntimeError::RecursiveAggregationInUnconstrained { call_stack }
+            | RuntimeError::UnconstrainedOnlyIntrinsicInConstrained { call_stack, .. } => {
+                call_stack
+            }
         }
     }
 }
```

### compiler/noirc_evaluator/src/ssa/checks/check_runtime_only_intrinsics.rs
```diff
@@ -0,0 +1,145 @@
+//! Rejects calls to intrinsics that the calling function's runtime cannot lower.
+//!
+//! `recursive_aggregation` exists only as circuit constraints, so Brillig has no lowering for it,
+//! and `field_less_than` exists only for unconstrained execution, so ACIR has none. Both back ends
+//! treat the other runtime's intrinsic as unreachable.
+//!
+//! Whether a function is constrained is decided at monomorphization, and code is commonly guarded
+//! with `is_unconstrained()` so that each runtime only reaches the calls it can lower. The check
+//! therefore runs on the SSA that is about to be lowered, after the passes that fold
+//! `is_unconstrained()` and remove the branches it disables, and reports the call that survives
+//! with its call stack.
+use acvm::acir::BlackBoxFunc;
+
+use crate::{
+    errors::RuntimeError,
+    ssa::{
+        ir::{
+            instruction::{Instruction, Intrinsic},
+            value::Value,
+        },
+        ssa_gen::Ssa,
+    },
+};
+
+impl Ssa {
+    /// Returns an error for the first call to an intrinsic that the calling function's runtime
+    /// cannot lower.
+    pub(crate) fn check_runtime_only_intrinsics(&self) -> Result<(), RuntimeError> {
+        for function in self.functions.values() {
+            let is_brillig = function.runtime().is_brillig();
+            for block_id in function.reachable_blocks() {
+                for instruction_id in function.dfg[block_id].instructions() {
+                    let Instruction::Call { func, .. } = &function.dfg[*instruction_id] else {
+                        continue;
+                    };
+                    let Value::Intrinsic(intrinsic) = &function.dfg[*func] else {
+                        continue;
+                    };
+                    let call_stack = || function.dfg.get_instruction_call_stack(*instruction_id);
+                    match intrinsic {
+                        Intrinsic::BlackBox(BlackBoxFunc::RecursiveAggregation) if is_brillig => {
+                            return Err(RuntimeError::RecursiveAggregationInUnconstrained {
+                                call_stack: call_stack(),
+                            });
+                        }
+                        Intrinsic::FieldLessThan if !is_brillig => {
+                            return Err(RuntimeError::UnconstrainedOnlyIntrinsicInConstrained {
+                                name: intrinsic.to_string(),
+                                call_stack: call_stack(),
+                            });
+                        }
+                        _ => {}
+                    }
+                }
+            }
+        }
+        Ok(())
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use crate::{errors::RuntimeError, ssa::ssa_gen::Ssa};
+
+    fn check(src: &str) -> Result<(), RuntimeError> {
+        Ssa::from_str(src).unwrap().check_runtime_only_intrinsics()
+    }
+
+    #[test]
+    fn rejects_recursive_aggregation_in_brillig() {
+        let src = r#"
+            brillig(inline) predicate_pure fn main f0 {
+              b0(v0: u32):
+                v1 = make_array [Field 0] : [Field; 1]
+                v2 = make_array [Field 0] : [Field; 1]
+                v3 = make_array [Field 0] : [Field; 1]
+                call recursive_aggregation(v1, v2, v3, Field 0, u32 0)
+                return
+            }
+        "#;
+        assert!(matches!(
+            check(src),
+            Err(RuntimeError::RecursiveAggregationInUnconstrained { .. })
+        ));
+    }
+
+    #[test]
+    fn accepts_recursive_aggregation_in_acir() {
+        let src = r#"
+            acir(inline) predicate_pure fn main f0 {
+              b0(v0: u32):
+                v1 = make_array [Field 0] : [Field; 1]
+                v2 = make_array [Field 0] : [Field; 1]
+                v3 = make_array [Field 0] : [Field; 1]
+                call recursive_aggregation(v1, v2, v3, Field 0, u32 0)
+                return
+            }
+        "#;
+        assert!(check(src).is_ok());
+    }
+
+    #[test]
+    fn rejects_field_less_than_in_acir() {
+        let src = r#"
+            acir(inline) fn main f0 {
+              b0(v0: Field, v1: Field):
+                v2 = call field_less_than(v0, v1) -> u1
+                return v2
+            }
+        "#;
+        assert!(matches!(
+            check(src),
+            Err(RuntimeError::UnconstrainedOnlyIntrinsicInConstrained { name, .. }) if name == "field_less_than"
+        ));
+    }
+
+    #[test]
+    fn accepts_field_less_than_in_brillig() {
+        let src = r#"
+            brillig(inline) fn main f0 {
+              b0(v0: Field, v1: Field):
+                v2 = call field_less_than(v0, v1) -> u1
+                return v2
+            }
+        "#;
+        assert!(check(src).is_ok());
+    }
+
+    #[test]
+    fn ignores_calls_in_unreachable_blocks() {
+        // Once `is_unconstrained()` is folded, the branch it disables is unreachable; a call left
+        // there is never lowered and is not reported.
+        let src = r#"
+            brillig(inline) fn main f0 {
+              b0():
+                return
+              b1():
+                v1 = make_array [Field 0] : [Field; 1]
+                call recursive_aggregation(v1, v1, v1, Field 0, u32 0)
+                return
+            }
+        "#;
+        assert!(check(src).is_ok());
+    }
+}
```

### compiler/noirc_evaluator/src/ssa/checks/mod.rs
```diff
@@ -1,11 +1,13 @@
-//! This module defines security SSA passes detecting constraint problems leading to possible
-//! soundness vulnerabilities.
+//! This module defines checks on the final SSA.
 //!
-//! The compiler informs the developer of these as bugs.
+//! The security checks detect constraint problems leading to possible soundness
+//! vulnerabilities, and the compiler informs the developer of these as bugs. The runtime check
+//! rejects calls to intrinsics that the calling function's runtime cannot lower.
 use crate::ssa::ir::{function::Function, value::ValueId};
 
 mod check_for_missing_brillig_constraints;
 mod check_for_underconstrained_values;
+mod check_runtime_only_intrinsics;
 
 pub use check_for_missing_brillig_constraints::{
     DEFAULT_MAX_ANCESTOR_DISTANCE, DEFAULT_MAX_ARRAY_OUTPUT_LENGTH,
```

### compiler/noirc_evaluator/src/ssa/mod.rs
```diff
@@ -489,6 +489,10 @@ pub fn optimize_ssa_builder_into_acir(
         "Brillig Array Get and Set Optimizations",
     )])?;
 
+    // Neither back end can lower the other runtime's intrinsics. Reject any that survived the
+    // passes, which have by now removed the branches `is_unconstrained()` disables.
+    builder.ssa().check_runtime_only_intrinsics()?;
+
     let brillig = time("SSA to Brillig", options.print_codegen_timings, || {
         builder.ssa().to_brillig(&options.brillig_options)
     });
```

### test_programs/compile_failure/recursive_aggregation_in_unconstrained_callee/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "recursive_aggregation_in_unconstrained_callee"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/compile_failure/recursive_aggregation_in_unconstrained_callee/src/main.nr
```diff
@@ -0,0 +1,14 @@
+// `inner` is written as a constrained function, but it is only reached from the unconstrained
+// `hint`, so it is compiled as unconstrained and its proof verification cannot be lowered.
+fn inner(vk: [Field; 1], proof: [Field; 1], pi: [Field; 1], kh: Field) {
+    std::verify_proof_with_type(vk, proof, pi, kh, 0);
+}
+
+unconstrained fn hint(vk: [Field; 1], proof: [Field; 1], pi: [Field; 1], kh: Field) {
+    inner(vk, proof, pi, kh);
+}
+
+fn main(vk: [Field; 1], proof: [Field; 1], pi: [Field; 1], kh: Field) {
+    // Safety: `hint` returns nothing; the program only exercises the compile-time rejection.
+    unsafe { hint(vk, proof, pi, kh) };
+}
```

### tooling/nargo_cli/tests/snapshots/compile_failure/recursive_aggregation_in_unconstrained_callee/execute__tests__stderr.snap
```diff
@@ -0,0 +1,19 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Cannot call `std::verify_proof_with_type` in unconstrained context
+   ┌─ std/lib.nr:93:5
+   │
+93 │     verify_proof_internal(verification_key, proof, public_inputs, key_hash, proof_type);
+   │     -----------------------------------------------------------------------------------
+   │
+   = Call stack:
+     1: hint
+             at src/main.nr:8:5
+     2: inner
+             at src/main.nr:4:5
+     3: verify_proof_with_type
+             at std/lib.nr:93:5
+
+Aborting due to 1 previous error
```
