# [?] fix: Acir gen doesn't panic on unsupported BB function (#3866)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-12-19
Source: https://github.com/noir-lang/noir/commit/34fd978d206789a9e9f5167bfd690a34386834d0
Type: security-commit

## Details
fix: Acir gen doesn't panic on unsupported BB function (#3866)

# Description

## Problem\*

Resolves #3865

## Summary\*



## Additional Context



## Documentation\*

Check one:
- [ ] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[Exceptional Case]** Documentation to be submitted in a separate
PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_evaluator/src/ssa/acir_gen/acir_ir/acir_variable.rs
```diff
@@ -1605,28 +1605,40 @@ fn execute_brillig(
             _signature: &[u8],
             _message: &[u8],
         ) -> Result<bool, BlackBoxResolutionError> {
-            unimplemented!("SchnorrVerify is not supported")
+            Err(BlackBoxResolutionError::Failed(
+                BlackBoxFunc::SchnorrVerify,
+                "SchnorrVerify is not supported".to_string(),
+            ))
         }
         fn pedersen_commitment(
             &self,
             _inputs: &[FieldElement],
             _domain_separator: u32,
         ) -> Result<(FieldElement, FieldElement), BlackBoxResolutionError> {
-            unimplemented!("PedersenCommitment is not supported")
+            Err(BlackBoxResolutionError::Failed(
+                BlackBoxFunc::PedersenCommitment,
+                "PedersenCommitment is not supported".to_string(),
+            ))
         }
         fn pedersen_hash(
             &self,
             _inputs: &[FieldElement],
             _domain_separator: u32,
         ) -> Result<FieldElement, BlackBoxResolutionError> {
-            unimplemented!("PedersenHash is not supported")
+            Err(BlackBoxResolutionError::Failed(
+                BlackBoxFunc::PedersenHash,
+                "PedersenHash is not supported".to_string(),
+            ))
         }
         fn fixed_base_scalar_mul(
             &self,
             _low: &FieldElement,
             _high: &FieldElement,
         ) -> Result<(FieldElement, FieldElement), BlackBoxResolutionError> {
-            unimplemented!("FixedBaseScalarMul is not supported")
+            Err(BlackBoxResolutionError::Failed(
+                BlackBoxFunc::FixedBaseScalarMul,
+                "FixedBaseScalarMul is not supported".to_string(),
+            ))
         }
     }
 
```
