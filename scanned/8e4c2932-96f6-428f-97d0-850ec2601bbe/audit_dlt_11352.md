# [?] fix: catch panics from EC point creation (e.g. the point is at infinity) (#4790)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-04-15
Source: https://github.com/noir-lang/noir/commit/645dba192f16ef34018828186ffb297422a8dc73
Type: security-commit

## Details
fix: catch panics from EC point creation (e.g. the point is at infinity) (#4790)

# Description

## Problem\*

Presently noir programs panic when trying to add points not in the
curve.

For example:
```rust
#[test]
fn test_addition_with_zero() {
    let a = pedersen_commitment([1]);
    let b = pedersen_commitment([0]); // returns the point at infinity
    let result = a + b; // panics

    let expected = pedersen_commitment([1]);
    assert(result == expected);
}
```

## Summary\*

Ideally we would check if one of the operands to the ec addition is the
point at infinity and return the other operand if so. This at least
prevents it from panicking and returns a nicer error.


## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

---------

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>
Co-authored-by: Tom French <tom@tomfren.ch>

## Patch
### .gitignore
```diff
@@ -4,6 +4,7 @@ examples/**/target/
 examples/9
 node_modules
 pkg/
+.idea
 
 # Yarn
 .pnp.*
```

### acvm-repo/bn254_blackbox_solver/src/fixed_base_scalar_mul.rs
```diff
@@ -47,17 +47,29 @@ pub fn fixed_base_scalar_mul(
     }
 }
 
+fn create_point(x: FieldElement, y: FieldElement) -> Result<grumpkin::SWAffine, String> {
+    let point = grumpkin::SWAffine::new_unchecked(x.into_repr(), y.into_repr());
+    if !point.is_on_curve() {
+        return Err(format!("Point ({}, {}) is not on curve", x.to_hex(), y.to_hex()));
+    };
+    if !point.is_in_correct_subgroup_assuming_on_curve() {
+        return Err(format!("Point ({}, {}) is not in correct subgroup", x.to_hex(), y.to_hex()));
+    };
+    Ok(point)
+}
+
 pub fn embedded_curve_add(
     input1_x: FieldElement,
     input1_y: FieldElement,
     input2_x: FieldElement,
     input2_y: FieldElement,
 ) -> Result<(FieldElement, FieldElement), BlackBoxResolutionError> {
-    let mut point1 = grumpkin::SWAffine::new(input1_x.into_repr(), input1_y.into_repr());
-    let point2 = grumpkin::SWAffine::new(input2_x.into_repr(), input2_y.into_repr());
-    let res = point1 + point2;
-    point1 = res.into();
-    if let Some((res_x, res_y)) = point1.xy() {
+    let point1 = create_point(input1_x, input1_y)
+        .map_err(|e| BlackBoxResolutionError::Failed(BlackBoxFunc::EmbeddedCurveAdd, e))?;
+    let point2 = create_point(input2_x, input2_y)
+        .map_err(|e| BlackBoxResolutionError::Failed(BlackBoxFunc::EmbeddedCurveAdd, e))?;
+    let res = grumpkin::SWAffine::from(point1 + point2);
+    if let Some((res_x, res_y)) = res.xy() {
         Ok((FieldElement::from_repr(*res_x), FieldElement::from_repr(*res_y)))
     } else {
         Err(BlackBoxResolutionError::Failed(
@@ -72,6 +84,7 @@ mod grumpkin_fixed_base_scalar_mul {
     use ark_ff::BigInteger;
 
     use super::*;
+
     #[test]
     fn smoke_test() -> Result<(), BlackBoxResolutionError> {
         let input = FieldElement::one();
@@ -84,6 +97,7 @@ mod grumpkin_fixed_base_scalar_mul {
         assert_eq!(y, res.1.to_hex());
         Ok(())
     }
+
     #[test]
     fn low_high_smoke_test() -> Result<(), BlackBoxResolutionError> {
         let low = FieldElement::one();
@@ -103,9 +117,9 @@ mod grumpkin_fixed_base_scalar_mul {
         let max_limb = FieldElement::from(u128::MAX);
         let invalid_limb = max_limb + FieldElement::one();
 
-        let expected_error =  Err(BlackBoxResolutionError::Failed(
+        let expected_error = Err(BlackBoxResolutionError::Failed(
             BlackBoxFunc::FixedBaseScalarMul,
-            "Limb 0000000000000000000000000000000100000000000000000000000000000000 is not less than 2^128".into()
+            "Limb 0000000000000000000000000000000100000000000000000000000000000000 is not less than 2^128".into(),
         ));
 
         let res = fixed_base_scalar_mul(&invalid_limb, &FieldElement::zero());
@@ -128,7 +142,23 @@ mod grumpkin_fixed_base_scalar_mul {
             res,
             Err(BlackBoxResolutionError::Failed(
                 BlackBoxFunc::FixedBaseScalarMul,
-                "30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47 is not a valid grumpkin scalar".into()
+                "30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47 is not a valid grumpkin scalar".into(),
+            ))
+        );
+    }
+
+    #[test]
+    fn rejects_addition_of_points_not_in_curve() {
+        let x = FieldElement::from(1u128);
+        let y = FieldElement::from(2u128);
+
+        let res = embedded_curve_add(x, y, x, y);
+
+        assert_eq!(
+            res,
+            Err(BlackBoxResolutionError::Failed(
+                BlackBoxFunc::EmbeddedCurveAdd,
+                "Point (0000000000000000000000000000000000000000000000000000000000000001, 0000000000000000000000000000000000000000000000000000000000000002) is not on curve".into(),
             ))
         );
     }
```
