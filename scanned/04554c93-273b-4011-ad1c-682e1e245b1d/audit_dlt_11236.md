# [?] fix: avoid panic on zero-limb field byte decomposition (#12738)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-05-26
Source: https://github.com/noir-lang/noir/commit/c1f34cdad6c7cd98bd3f04ba4a6ff790c402543a
Type: security-commit

## Details
fix: avoid panic on zero-limb field byte decomposition (#12738)

## Patch
### acvm-repo/brillig_vm/src/black_box.rs
```diff
@@ -310,11 +310,6 @@ fn to_be_radix<F: AcirField>(
         "Radix out of the valid range [2,256]. Value: {radix}"
     );
 
-    assert!(
-        num_limbs >= 1 || input.is_zero(),
-        "Input value {input} is not zero but number of limbs is zero."
-    );
-
     assert!(
         !output_bits || radix == 2u32,
         "Radix {radix} is not equal to 2 and bit mode is activated."
@@ -402,4 +397,17 @@ mod to_be_radix_tests {
             .collect();
         assert_eq!(limbs, expected_limbs);
     }
+
+    #[test]
+    fn rejects_non_zero_field_with_zero_limbs() {
+        let value = FieldElement::from(1u128);
+
+        let error = to_be_radix(value, 256, 0, false).unwrap_err();
+        assert_eq!(
+            error,
+            acvm_blackbox_solver::BlackBoxResolutionError::AssertFailed(
+                "Field failed to decompose into specified 0 limbs".to_string()
+            )
+        );
+    }
 }
```

### noir_stdlib/src/field/mod.nr
```diff
@@ -527,6 +527,16 @@ mod tests {
         let _: [u8; 16] = 0x100000000000000000000000000000000.to_le_bytes();
     }
 
+    #[test(should_fail_with = "Field failed to decompose into specified 0 limbs")]
+    unconstrained fn non_zero_field_to_le_bytes_zero_limbs() {
+        let _: [u8; 0] = 5.to_le_bytes();
+    }
+
+    #[test(should_fail_with = "Field failed to decompose into specified 0 limbs")]
+    unconstrained fn non_zero_field_to_be_bytes_zero_limbs() {
+        let _: [u8; 0] = 5.to_be_bytes();
+    }
+
     #[test]
     unconstrained fn test_field_less_than() {
         assert(field_less_than(0, 1));
```
