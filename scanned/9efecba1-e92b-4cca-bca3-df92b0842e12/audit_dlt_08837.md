# [?] bugfix(runner): Profile coupon_call like function_call (fix from_trace panic). (#10081)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-06-11
Source: https://github.com/starkware-libs/cairo/commit/528ddcf7c73831bc3dc178df2077f8eecb3d458e
Type: security-commit

## Details
bugfix(runner): Profile coupon_call like function_call (fix from_trace panic). (#10081)

## Patch
### crates/cairo-lang-runner/src/profiling.rs
```diff
@@ -149,7 +149,8 @@ impl ProfilingInfo {
                 GenStatement::Invocation(invocation) => {
                     if matches!(
                         builder.registry().get_libfunc(&invocation.libfunc_id),
-                        Ok(CoreConcreteLibfunc::FunctionCall(_))
+                        Ok(CoreConcreteLibfunc::FunctionCall(_)
+                            | CoreConcreteLibfunc::CouponCall(_))
                     ) {
                         // Push to the stack.
                         if function_stack_depth < profiling_config.max_stack_trace_depth {
```

### crates/cairo-lang-runner/src/profiling_test_data/profiling
```diff
@@ -324,3 +324,68 @@ Weight by Sierra stack trace:
   test::main: 1
 Weight by Cairo stack trace:
   test::main: 1
+
+//! > ==========================================================================
+
+//! > Test profiling info with a coupon call (regression: profiler must frame coupon_call)
+
+//! > test_runner_name
+test_profiling
+
+//! > cairo_code
+use core::num::traits::WrappingAdd;
+
+extern fn coupon_buy<T>() -> T nopanic;
+
+fn add_with_coupon(a: u128, b: u128) -> u128 {
+    a.wrapping_add(b)
+}
+
+fn main() -> u128 {
+    let coupon: add_with_coupon::Coupon = coupon_buy();
+    add_with_coupon(3, 4, __coupon__: coupon)
+}
+
+//! > function_name
+main
+
+//! > expected_profiling_info
+Weight by sierra statement:
+  statement 0: 3 (u128_overflowing_add([0], [1], [2]) { fallthrough([3], [4]) 5([5], [6]) })
+  statement 1: 1 (branch_align() -> ())
+  statement 2: 1 (store_temp<RangeCheck>([3]) -> ([3]))
+  statement 3: 1 (store_temp<u128>([4]) -> ([4]))
+  statement 4: 1 (return([3], [4]))
+  statement 12: 1 (store_temp<RangeCheck>([0]) -> ([0]))
+  statement 13: 1 (store_temp<u128>([2]) -> ([2]))
+  statement 14: 1 (store_temp<u128>([3]) -> ([3]))
+  statement 15: 1 (coupon_call<user@test::add_with_coupon>([0], [2], [3], [1]) -> ([4], [5]))
+  statement 16: 1 (return([4], [5]))
+Weight by concrete libfunc:
+  libfunc store_temp<u128>: 3
+  libfunc u128_overflowing_add: 3
+  libfunc store_temp<RangeCheck>: 2
+  libfunc branch_align: 1
+  libfunc coupon_call<user@test::add_with_coupon>: 1
+  return: 2
+Weight by generic libfunc:
+  libfunc store_temp: 5
+  libfunc u128_overflowing_add: 3
+  libfunc branch_align: 1
+  libfunc coupon_call: 1
+  return: 2
+Weight by user function (inc. generated):
+  function test::add_with_coupon: 7
+  function test::main: 5
+Weight by original user function (exc. generated):
+  function test::add_with_coupon: 7
+  function test::main: 5
+Weight by Cairo function:
+  function core::integer::U128OverflowingAdd::overflowing_add: 7
+  function lib.cairo::main: 5
+Weight by Sierra stack trace:
+  test::main: 12
+  test::main -> test::add_with_coupon: 7
+Weight by Cairo stack trace:
+  test::main: 12
+  test::main -> test::add_with_coupon: 7
```
