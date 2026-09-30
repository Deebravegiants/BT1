# [?] fix(msm): avoid i64::MIN overflow in I64Scalars MSM (#917)

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2025-08-27
Source: https://github.com/a16z/jolt/commit/2343e4b39c7fed5ec398dd4776bdac360aa76373
Type: security-commit

## Details
fix(msm): avoid i64::MIN overflow in I64Scalars MSM (#917)

* fix(msm): avoid i64::MIN overflow in I64Scalars MSM

* delete comments

## Patch
### jolt-core/src/msm/mod.rs
```diff
@@ -67,6 +67,13 @@ where
 
             // TODO: Check if this is the fastest way forward.
             MultilinearPolynomial::I64Scalars(poly) => {
+                if bases.len() != poly.coeffs.len() {
+                    return Err(ProofVerifyError::KeyLengthError(
+                        bases.len(),
+                        poly.coeffs.len(),
+                    ));
+                }
+
                 let scalars = &poly.coeffs;
                 let (pos_scalars, pos_bases, neg_scalars, neg_bases): (
                     Vec<u64>,
@@ -83,7 +90,7 @@ where
                                 pos_s.push(scalar as u64);
                                 pos_b.push(*base);
                             } else if scalar < 0 {
-                                neg_s.push((-scalar) as u64);
+                                neg_s.push(scalar.unsigned_abs());
                                 neg_b.push(*base);
                             }
                             (pos_s, pos_b, neg_s, neg_b)
@@ -99,15 +106,9 @@ where
                             (ps1, pb1, ns1, nb1)
                         },
                     );
-                (bases.len() == poly.coeffs.len())
-                    .then(|| {
-                        msm_u64::<Self>(&pos_bases, &pos_scalars, false)
-                            - msm_u64::<Self>(&neg_bases, &neg_scalars, false)
-                    })
-                    .ok_or(ProofVerifyError::KeyLengthError(
-                        bases.len(),
-                        poly.coeffs.len(),
-                    ))
+
+                Ok(msm_u64::<Self>(&pos_bases, &pos_scalars, false)
+                    - msm_u64::<Self>(&neg_bases, &neg_scalars, false))
             }
             _ => unimplemented!("This variant of MultilinearPolynomial is not yet handled"),
         }
```
