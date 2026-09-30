# [?] fix(circle): reject opening point equal to a query point instead of panicking (#1849)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-06-14
Source: https://github.com/Plonky3/Plonky3/commit/94a184f5ebf1c1e0db34b295234685e0d52aa615
Type: security-commit

## Details
fix(circle): reject opening point equal to a query point instead of panicking (#1849)

* fix(circle): reject opening point equal to a query point instead of panicking

The DEEP-quotient verifier inverts the denominator |v_p(zeta)|^2, which equals
2*(1 - (x - zeta).x) and is zero exactly when an opening point zeta coincides
with a query point x. That case inverted zero and panicked with "Tried to
invert zero". Return a clean error instead, the same way two-adic FRI handles
it (OpeningPointMatchesQueryPoint, #1762).

The guard is verifier side only, matching the two-adic fix. For any zeta
distinct from x the computed value is unchanged, so valid proofs verify
identically.

* docs(circle): clarify DEEP-quotient collision comments

- Rewrite the vanishing-denominator docs and comments per repo doc conventions
  (one idea per line, no narration of the change).
- Use `EF::from_u8` directly instead of `EF::from(F::from_u8(..))` in the
  reduce-row test.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Thomas Coratger <thomas.coratger@gmail.com>
Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### circle/src/deep_quotient.rs
```diff
@@ -82,26 +82,32 @@ pub(crate) fn deep_quotient_vanishing_part<F: ComplexExtendable, EF: ExtensionFi
 ///
 /// # Returns
 ///
-/// The DEEP quotient value for this row.
+/// - `Some(value)`: the DEEP quotient value for this row.
+/// - `None`: the opening point coincides with this query point, so the denominator vanishes.
 pub(crate) fn deep_quotient_reduce_row<F: ComplexExtendable, EF: ExtensionField<F>>(
     alpha: EF,
     x: Point<F>,
     zeta: Point<EF>,
     ps_at_x: &[F],
     ps_at_zeta: &[EF],
-) -> EF {
+) -> Option<EF> {
     // Compute the vanishing part: handles the (x - zeta) denominator
     let (vp_num, vp_denom) =
         deep_quotient_vanishing_part(x, zeta, alpha.exp_u64(ps_at_x.len() as u64));
 
+    // On the circle, the denominator `|v_p(zeta)|^2` reduces to `2 * (1 - (x - zeta).x)`.
+    // This is zero exactly when `x == zeta`.
+    // Return `None` there so the caller rejects the opening instead of dividing by zero.
+    let vp_denom_inv = vp_denom.try_inverse()?;
+
     // Compute the constraint part: handles the f(x) - f(zeta) numerator
     let constraint_part = dot_product::<EF, _, _>(
         alpha.powers(),
         izip!(ps_at_x, ps_at_zeta).map(|(&p_at_x, &p_at_zeta)| -p_at_zeta + p_at_x),
     );
 
     // Combine vanishing part and constraint part
-    (vp_num / vp_denom) * constraint_part
+    Some(vp_num * vp_denom_inv * constraint_part)
 }
 
 /// The point-dependent part of the DEEP quotient on a fixed domain.
@@ -345,6 +351,7 @@ mod tests {
             .zip(domain.points())
             .map(|(ps_at_x, x)| {
                 deep_quotient_reduce_row(alpha, x, zeta, &ps_at_x.collect_vec(), &ps_at_zeta)
+                    .unwrap()
             })
             .collect_vec();
         assert_eq!(cfft_permute_slice(&mat_reduced), row_reduced);
@@ -472,4 +479,31 @@ mod tests {
             );
         }
     }
+
+    #[test]
+    fn reduce_row_rejects_opening_point_on_query_point() {
+        // Invariant: the DEEP-quotient denominator is `2 * (1 - (x - zeta).x)`.
+        // It vanishes exactly when the opening point `zeta` equals the query point `x`.
+        //
+        //     x == zeta  ->  denominator 0     ->  None
+        //     x != zeta  ->  denominator != 0  ->  Some(quotient)
+
+        // A query point on the circle domain, in the base field.
+        let x: Point<F> = Point::from_projective_line(F::from_u8(5));
+
+        // Challenge scalar and dummy column evaluations.
+        // Their values never affect whether the denominator vanishes.
+        let alpha = EF::from_u8(7);
+        let ps_at_x = [F::from_u8(1), F::from_u8(2)];
+        let ps_at_zeta = [EF::from_u8(3), EF::from_u8(4)];
+
+        // Lift the query point's coordinates into the extension field.
+        // The opening point is now the same point, so `x - zeta` is the group identity.
+        let zeta_on_x: Point<EF> = Point::new(EF::from(x.x), EF::from(x.y));
+        assert!(deep_quotient_reduce_row(alpha, x, zeta_on_x, &ps_at_x, &ps_at_zeta).is_none());
+
+        // A distinct opening point keeps the denominator nonzero and reduces normally.
+        let zeta_off: Point<EF> = Point::from_projective_line(EF::from_u8(9));
+        assert!(deep_quotient_reduce_row(alpha, x, zeta_off, &ps_at_x, &ps_at_zeta).is_some());
+    }
 }
```

### circle/src/pcs.rs
```diff
@@ -78,6 +78,11 @@ where
     FirstLayerMmcsError(FriMmcsError),
     #[error("input shape error: mismatched dimensions")]
     InputShapeError,
+    /// The opening point coincides with a queried domain point.
+    ///
+    /// The DEEP-quotient denominator vanishes there, so the row cannot be reduced.
+    #[error("opening point coincides with a query point")]
+    OpeningPointMatchesQueryPoint,
 }
 
 #[derive(Serialize, Deserialize, Clone)]
@@ -672,8 +677,11 @@ where
                             }
                             let zeta = Point::from_projective_line(*zeta_uni);
 
+                            // A vanishing denominator means this opening point lands on the
+                            // query point; reject the proof rather than dividing by zero.
                             *ro += *alpha_offset
-                                * deep_quotient_reduce_row(alpha, x, zeta, ps_at_x, ps_at_zeta);
+                                * deep_quotient_reduce_row(alpha, x, zeta, ps_at_x, ps_at_zeta)
+                                    .ok_or(InputError::OpeningPointMatchesQueryPoint)?;
 
                             *alpha_offset *= alpha_pow_width_2;
                         }
```
