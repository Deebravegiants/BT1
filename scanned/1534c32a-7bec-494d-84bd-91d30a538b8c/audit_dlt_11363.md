# [?] fix: corrected the formatting of error message parameters in index out of bounds error (#3630)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-11-29
Source: https://github.com/noir-lang/noir/commit/3bba3862dc8703410681300be894bfd1ebca7336
Type: security-commit

## Details
fix: corrected the formatting of error message parameters in index out of bounds error (#3630)

chore: corrected the formatting of error message parameters in index out of bounds error

## Patch
### compiler/noirc_evaluator/src/errors.rs
```diff
@@ -26,7 +26,7 @@ pub enum RuntimeError {
     },
     #[error(transparent)]
     InternalError(#[from] InternalError),
-    #[error("Index out of bounds, array has size {index:?}, but index was {array_size:?}")]
+    #[error("Index out of bounds, array has size {array_size}, but index was {index}")]
     IndexOutOfBounds { index: usize, array_size: usize, call_stack: CallStack },
     #[error("Range constraint of {num_bits} bits is too large for the Field size")]
     InvalidRangeConstraint { num_bits: u32, call_stack: CallStack },
```
