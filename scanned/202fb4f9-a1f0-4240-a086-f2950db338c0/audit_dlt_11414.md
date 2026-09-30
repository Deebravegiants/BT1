# [?] fix: Reed-Solomon panic on duplicate input points (#312)

## Summary
Severity: Unknown
Chain: ZK
Component: EspressoSystems/jellyfish
Published: 2023-06-09
Source: https://github.com/EspressoSystems/jellyfish/commit/fbf3b0d409bbd9f870269f7f3beb9f41ec39dc2c
Type: security-commit

## Details
fix: Reed-Solomon panic on duplicate input points (#312)

* failing test

* check for duplicate input points

## Patch
### primitives/src/reed_solomon_code/mod.rs
```diff
@@ -111,14 +111,21 @@ where
     let w = (0..data_size)
         .map(|i| {
             let mut ret = F::one();
-            (0..data_size).for_each(|j| {
+            for j in 0..data_size {
                 if i != j {
-                    ret /= x[i] - x[j];
+                    let denom = x[i] - x[j];
+                    if denom.is_zero() {
+                        return Err(PrimitivesError::ParameterError(format!(
+                            "duplicate input point {} at indices {}, {}",
+                            x[i], i, j
+                        )));
+                    }
+                    ret /= denom;
                 }
-            });
-            ret
+            }
+            Ok(ret)
         })
-        .collect::<Vec<_>>();
+        .collect::<Result<Vec<_>, _>>()?;
     // Calculate f(x) = \sum_i l_i(x)
     let mut f = vec![F::zero(); data_size];
     // for i in 0..shares.len() {
@@ -252,4 +259,32 @@ mod test {
         test_rs_code_fft_helper::<Fr377>();
         test_rs_code_fft_helper::<Fr381>();
     }
+
+    fn duplicate_inputs_helper<F: Field>() {
+        // Encoded as a polynomial 4x^2 + x + 3
+        let payload = [3u64, 1, 4].map(|x| F::from(x));
+        // Evaluation of the above polynomial on (1, 2, 3, 4, 5) is (8, 21, 42, 71, 108)
+        let expected = [8u64, 21, 42, 71, 108].map(|x| F::from(x));
+        let code: Vec<F> = reed_solomon_erasure_encode(payload.iter(), 2)
+            .unwrap()
+            .collect();
+        assert_eq!(code, expected);
+
+        let mut points = [1u64, 2, 3].map(|x| F::from(x));
+        let recovered_payload: Vec<F> =
+            reed_solomon_erasure_decode(points.iter().zip(&code[..3]), payload.len()).unwrap();
+        assert_eq!(recovered_payload, payload);
+
+        points[1] = points[0]; // duplicate input point
+        assert!(reed_solomon_erasure_decode::<F, _, _, _>(
+            points.iter().zip(&code[..3]),
+            payload.len()
+        )
+        .is_err());
+    }
+
+    #[test]
+    fn duplicate_inputs() {
+        duplicate_inputs_helper::<Fr381>();
+    }
 }
```
