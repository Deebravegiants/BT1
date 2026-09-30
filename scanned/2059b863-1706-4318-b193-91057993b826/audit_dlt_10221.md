# [?] crypto(fixpoint): add overflow failure test

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-05-13
Source: https://github.com/penumbra-zone/penumbra/commit/716901df0ab4a33b106f8c884e401d8a137795a5
Type: security-commit

## Details
crypto(fixpoint): add overflow failure test

## Patch
### crypto/src/fixpoint/tests.rs
```diff
@@ -20,3 +20,13 @@ proptest! {
     }
 
 }
+
+#[test]
+#[should_panic]
+fn multiply_large_failure() {
+    let a = 1788000000000000000000u128;
+    let b = 1000000000000000000000u128;
+    let a_fp: U128x128 = a.into();
+    let b_fp: U128x128 = b.into();
+    let c_fp = (a_fp * b_fp).expect("overflow loudly!");
+}
```
