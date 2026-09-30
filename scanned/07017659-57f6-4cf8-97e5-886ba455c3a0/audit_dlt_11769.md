# [?] fix: avoid a panic in combine_for_open

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-12-14
Source: https://github.com/AleoNet/snarkVM-test/commit/5f94a0ae8959df49b7df22016c6b2f648c2cbdcb
Type: security-commit

## Details
fix: avoid a panic in combine_for_open

Signed-off-by: ljedrz <ljedrz@gmail.com>

## Patch
### algorithms/src/polycommit/sonic_pc/mod.rs
```diff
@@ -276,14 +276,17 @@ impl<E: PairingEngine, S: AlgebraicSponge<E::Fq, 2>> SonicKZG10<E, S> {
         Commitment<E>: 'a,
     {
         ensure!(labeled_polynomials.len() == rands.len());
-        Ok(Self::combine_polynomials(labeled_polynomials.into_iter().zip_eq(rands).map(|(p, r)| {
+        let mut to_combine = Vec::with_capacity(labeled_polynomials.len());
+
+        for (p, r) in labeled_polynomials.zip_eq(rands) {
             let enforced_degree_bounds: Option<&[usize]> = ck.enforced_degree_bounds.as_deref();
 
-            kzg10::KZG10::<E>::check_degrees_and_bounds(universal_prover.max_degree, enforced_degree_bounds, p)
-                .unwrap();
+            kzg10::KZG10::<E>::check_degrees_and_bounds(universal_prover.max_degree, enforced_degree_bounds, p)?;
             let challenge = fs_rng.squeeze_short_nonnative_field_element::<E::Fr>();
-            (challenge, p.polynomial().to_dense(), r)
-        })))
+            to_combine.push((challenge, p.polynomial().to_dense(), r));
+        }
+
+        Ok(Self::combine_polynomials(to_combine))
     }
 
     /// On input a list of labeled polynomials and a query set, `open` outputs a proof of evaluation
```
