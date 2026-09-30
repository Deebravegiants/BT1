# [?] fix(sierra): avoid overflow when simulating array_slice (#10373)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-09-14
Source: https://github.com/starkware-libs/cairo/commit/7aa0b17ad3f097b69574d949f3620fc4c03ca538
Type: security-commit

## Details
fix(sierra): avoid overflow when simulating array_slice (#10373)

Signed-off-by: wangjingshuiku <wangjingshuiku@163.com>

## Patch
### crates/cairo-lang-sierra/src/simulation/core.rs
```diff
@@ -169,7 +169,9 @@ pub fn simulate<
                 CoreValue::Uint32(start),
                 CoreValue::Uint32(length),
             ] = inputs);
-            match arr.get(start as usize..(start + length) as usize) {
+            let start = start as usize;
+            let end = start.checked_add(length as usize);
+            match end.and_then(|end| arr.get(start..end)) {
                 Some(elements) => {
                     (vec![CoreValue::RangeCheck, CoreValue::Array(elements.to_vec())], 0)
                 }
```

### crates/cairo-lang-sierra/src/simulation/test.rs
```diff
@@ -154,6 +154,13 @@ fn simulate(
              vec![RangeCheck, Felt252(((BigInt::from(3) << 128_u32) + BigInt::from(7)).into())]
              => Ok((vec![RangeCheck, Uint128(3), Uint128(7)], 1));
             "u128s_from_felt252(3 * 2**128 + 7)")]
+#[test_case("array_slice", vec![type_arg("u128")],
+             vec![RangeCheck, Array(vec![]), Uint32(u32::MAX), Uint32(1)]
+             => Ok((vec![RangeCheck], 1)); "array_slice([], u32::MAX, 1)")]
+#[test_case("array_slice", vec![type_arg("u128")],
+             vec![RangeCheck, Array(vec![Uint128(1), Uint128(2), Uint128(3)]), Uint32(1), Uint32(2)]
+             => Ok((vec![RangeCheck, Array(vec![Uint128(2), Uint128(3)])], 0));
+            "array_slice([1, 2, 3], 1, 2)")]
 fn simulate_branch(
     id: &str,
     generic_args: Vec<GenericArg>,
```
