# [?] Prevent shift ops from panicking (#1073)

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2023-06-06
Source: https://github.com/0xPolygonZero/plonky2/commit/2cf31f5f2d5322f104d4c4748f09ef5e0ba96cd6
Type: security-commit

## Details
Prevent shift ops from panicking (#1073)

## Patch
### evm/src/witness/operation.rs
```diff
@@ -468,7 +468,12 @@ pub(crate) fn generate_shl<F: Field>(
 ) -> Result<(), ProgramError> {
     let [(input0, log_in0), (input1, log_in1)] =
         stack_pop_with_log_and_fill::<2, _>(state, &mut row)?;
-    let result = input1 << input0;
+
+    let result = if input0 > U256::from(255u64) {
+        U256::zero()
+    } else {
+        input1 << input0
+    };
     append_shift(state, row, input0, log_in0, log_in1, result)
 }
 
@@ -478,7 +483,12 @@ pub(crate) fn generate_shr<F: Field>(
 ) -> Result<(), ProgramError> {
     let [(input0, log_in0), (input1, log_in1)] =
         stack_pop_with_log_and_fill::<2, _>(state, &mut row)?;
-    let result = input1 >> input0;
+
+    let result = if input0 > U256::from(255u64) {
+        U256::zero()
+    } else {
+        input1 >> input0
+    };
     append_shift(state, row, input0, log_in0, log_in1, result)
 }
 
```
