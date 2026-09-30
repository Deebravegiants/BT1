# [?] Prevent `U64Div` event from crashing (#1710)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-03-20
Source: https://github.com/0xMiden/miden-vm/commit/0234d3831bd9645bd76890cee0d3ea4a31647222
Type: security-commit

## Details
Prevent `U64Div` event from crashing (#1710)

* test: add failing test

* fix: fix `push_u64_div_result`

* changelog

* docstring nit

## Patch
### CHANGELOG.md
```diff
@@ -19,6 +19,7 @@
 - [BREAKING] Updated Winterfell dependency to v0.12 (#1658).
 - Update recursive verifier to use `HORNERBASE` (#1665).
 - Remove `FALCON_SIG_TO_STACK` event (#1703)
+- Prevent `U64Div` event from crashing processor (#1710)
 
 
 ## 0.12.0 (2025-01-22)
```

### processor/src/operations/sys_ops/sys_event_handlers.rs
```diff
@@ -316,17 +316,41 @@ pub fn push_u64_div_result(
     advice_provider: &mut impl AdviceProvider,
     process: ProcessState,
 ) -> Result<(), ExecutionError> {
-    let divisor_hi = process.get_stack_item(0).as_int();
-    let divisor_lo = process.get_stack_item(1).as_int();
-    let divisor = (divisor_hi << 32) + divisor_lo;
+    let divisor = {
+        let divisor_hi = process.get_stack_item(0).as_int();
+        let divisor_lo = process.get_stack_item(1).as_int();
 
-    if divisor == 0 {
-        return Err(ExecutionError::DivideByZero(process.clk()));
-    }
+        // Ensure the divisor is a pair of u32 values
+        if divisor_hi > u32::MAX.into() {
+            return Err(ExecutionError::NotU32Value(Felt::new(divisor_hi), ZERO));
+        }
+        if divisor_lo > u32::MAX.into() {
+            return Err(ExecutionError::NotU32Value(Felt::new(divisor_lo), ZERO));
+        }
 
-    let dividend_hi = process.get_stack_item(2).as_int();
-    let dividend_lo = process.get_stack_item(3).as_int();
-    let dividend = (dividend_hi << 32) + dividend_lo;
+        let divisor = (divisor_hi << 32) + divisor_lo;
+
+        if divisor == 0 {
+            return Err(ExecutionError::DivideByZero(process.clk()));
+        }
+
+        divisor
+    };
+
+    let dividend = {
+        let dividend_hi = process.get_stack_item(2).as_int();
+        let dividend_lo = process.get_stack_item(3).as_int();
+
+        // Ensure the dividend is a pair of u32 values
+        if dividend_hi > u32::MAX.into() {
+            return Err(ExecutionError::NotU32Value(Felt::new(dividend_hi), ZERO));
+        }
+        if dividend_lo > u32::MAX.into() {
+            return Err(ExecutionError::NotU32Value(Felt::new(dividend_lo), ZERO));
+        }
+
+        (dividend_hi << 32) + dividend_lo
+    };
 
     let quotient = dividend / divisor;
     let remainder = dividend - quotient * divisor;
```

### stdlib/tests/math/u64_mod.rs
```diff
@@ -4,6 +4,7 @@ use processor::ExecutionError;
 use test_utils::{
     Felt, U32_BOUND, ZERO, expect_exec_error_matches, proptest::prelude::*, rand::rand_value,
 };
+use vm_core::assert_matches;
 
 // ADDITION
 // ------------------------------------------------------------------------------------------------
@@ -428,6 +429,41 @@ fn unchecked_div() {
     test.expect_stack(&[d1, d0]);
 }
 
+/// The `U64Div` event handler is susceptible to crashing the processor if we don't ensure that the
+/// divisor and dividend limbs are proper u32 values.
+#[test]
+fn ensure_div_doesnt_crash() {
+    let source = "
+        use.std::math::u64
+        begin
+            exec.u64::div
+        end";
+
+    // 1. divisor limbs not u32
+
+    let (dividend_hi, dividend_lo) = (0, 1);
+    let (divisor_hi, divisor_lo) = (u32::MAX as u64, u32::MAX as u64 + 1);
+
+    let test = build_test!(source, &[dividend_lo, dividend_hi, divisor_lo, divisor_hi]);
+    let err = test.execute();
+    match err {
+        Ok(_) => panic!("expected an error"),
+        Err(err) => assert_matches!(err, ExecutionError::NotU32Value(_, _)),
+    }
+
+    // 2. dividend limbs not u32
+
+    let (dividend_hi, dividend_lo) = (u32::MAX as u64, u32::MAX as u64 + 1);
+    let (divisor_hi, divisor_lo) = (0, 1);
+
+    let test = build_test!(source, &[dividend_lo, dividend_hi, divisor_lo, divisor_hi]);
+    let err = test.execute();
+    match err {
+        Ok(_) => panic!("expected an error"),
+        Err(err) => assert_matches!(err, ExecutionError::NotU32Value(_, _)),
+    }
+}
+
 // MODULO OPERATION
 // ------------------------------------------------------------------------------------------------
 
```
