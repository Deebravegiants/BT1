# [?] fix: ADVZ payload prover panic on some payload byte lengths (#422)

## Summary
Severity: Unknown
Chain: ZK
Component: EspressoSystems/jellyfish
Published: 2023-11-22
Source: https://github.com/EspressoSystems/jellyfish/commit/265eaaa059e0a501824e5aadf7ac5f32d9e4a6b8
Type: security-commit

## Details
fix: ADVZ payload prover panic on some payload byte lengths (#422)

* add failing test

* fix bug

* refactor

## Patch
### primitives/src/vid/advz/payload_prover.rs
```diff
@@ -86,7 +86,7 @@ where
         let range_poly = self.range_elem_to_poly(&range_elem);
         let start_namespace_byte = self.index_poly_to_byte(range_poly.start);
         let offset_elem = range_elem.start - self.index_byte_to_elem(start_namespace_byte);
-        let range_elem_byte = self.range_elem_to_byte(&range_elem);
+        let range_elem_byte = self.range_elem_to_byte_clamped(&range_elem, payload.len());
 
         check_range_poly(&range_poly)?;
 
@@ -198,20 +198,20 @@ where
         let range_poly = self.range_elem_to_poly(&range_elem);
         let start_namespace_byte = self.index_poly_to_byte(range_poly.start);
         let offset_elem = range_elem.start - self.index_byte_to_elem(start_namespace_byte);
-        let range_elem_byte = self.range_elem_to_byte(&range_elem);
+        let range_elem_byte = self.range_elem_to_byte_clamped(&range_elem, payload.len());
 
         check_range_poly(&range_poly)?;
 
         // compute the prefix and suffix elems
         let mut elems_iter =
             bytes_to_field::<_, KzgEval<E>>(payload[start_namespace_byte..].iter())
                 .take(self.payload_chunk_size);
-        let prefix: Vec<_> = elems_iter.by_ref().take(offset_elem).collect();
-        let suffix: Vec<_> = elems_iter.skip(range_elem.len()).collect();
+        let prefix_elems: Vec<_> = elems_iter.by_ref().take(offset_elem).collect();
+        let suffix_elems: Vec<_> = elems_iter.skip(range_elem.len()).collect();
 
         Ok(LargeRangeProof {
-            prefix_elems: prefix,
-            suffix_elems: suffix,
+            prefix_elems,
+            suffix_elems,
             prefix_bytes: payload[range_elem_byte.start..range.start].to_vec(),
             suffix_bytes: payload[range.end..range_elem_byte.end].to_vec(),
             chunk_range: range,
@@ -278,6 +278,13 @@ where
     fn range_elem_to_byte(&self, range: &Range<usize>) -> Range<usize> {
         range_refine(range, elem_byte_capacity::<KzgEval<E>>())
     }
+    fn range_elem_to_byte_clamped(&self, range: &Range<usize>, len: usize) -> Range<usize> {
+        let result = self.range_elem_to_byte(range);
+        Range {
+            end: ark_std::cmp::min(result.end, len),
+            ..result
+        }
+    }
     fn range_elem_to_poly(&self, range: &Range<usize>) -> Range<usize> {
         range_coarsen(range, self.payload_chunk_size)
     }
@@ -392,7 +399,7 @@ mod tests {
         payload_prover::PayloadProver,
     };
     use ark_bls12_381::Bls12_381;
-    use ark_std::{ops::Range, println, rand::Rng};
+    use ark_std::{ops::Range, print, println, rand::Rng};
     use sha2::Sha256;
 
     fn correctness_generic<E, H>()
@@ -402,18 +409,21 @@ mod tests {
     {
         // play with these items
         let (payload_chunk_size, num_storage_nodes) = (4, 6);
-        let num_polys = 4;
+        let num_polys = 3;
 
         // more items as a function of the above
         let payload_elems_len = num_polys * payload_chunk_size;
-        let payload_bytes_len = payload_elems_len * elem_byte_capacity::<E::ScalarField>();
+        let payload_bytes_base_len = payload_elems_len * elem_byte_capacity::<E::ScalarField>();
         let poly_bytes_len = payload_chunk_size * elem_byte_capacity::<E::ScalarField>();
         let mut rng = jf_utils::test_rng();
-        let payload = init_random_payload(payload_bytes_len, &mut rng);
         let srs = init_srs(payload_elems_len, &mut rng);
-
         let advz = Advz::<E, H>::new(payload_chunk_size, num_storage_nodes, srs).unwrap();
-        let d = advz.disperse(&payload).unwrap();
+
+        // TEST: different payload byte lengths
+        let payload_byte_len_noise_cases = vec![0, poly_bytes_len / 2, poly_bytes_len - 1];
+        let payload_len_cases = payload_byte_len_noise_cases
+            .into_iter()
+            .map(|l| payload_bytes_base_len - l);
 
         // TEST: prove data ranges for this paylaod
         // it takes too long to test all combos of (polynomial, start, len)
@@ -464,35 +474,56 @@ mod tests {
         };
         let all_cases = [(edge_cases, "edge"), (random_cases, "rand")];
 
-        for poly in 0..num_polys {
-            let poly_offset = poly * poly_bytes_len;
-
-            for cases in all_cases.iter() {
-                for range in cases.0.iter() {
-                    let range = Range {
-                        start: range.start + poly_offset,
-                        end: range.end + poly_offset,
-                    };
-                    println!("poly {} {} case: {:?}", poly, cases.1, range);
-
-                    let stmt = Statement {
-                        payload_subslice: &payload[range.clone()],
-                        range: range.clone(),
-                        commit: &d.commit,
-                        common: &d.common,
-                    };
-
-                    let small_range_proof: SmallRangeProof<_> =
-                        advz.payload_proof(&payload, range.clone()).unwrap();
-                    advz.payload_verify(stmt.clone(), &small_range_proof)
-                        .unwrap()
-                        .unwrap();
-
-                    let large_range_proof: LargeRangeProof<_> =
-                        advz.payload_proof(&payload, range.clone()).unwrap();
-                    advz.payload_verify(stmt, &large_range_proof)
-                        .unwrap()
-                        .unwrap();
+        for payload_len_case in payload_len_cases {
+            let payload = init_random_payload(payload_len_case, &mut rng);
+            let d = advz.disperse(&payload).unwrap();
+            println!("payload byte len case: {}", payload.len());
+
+            for poly in 0..num_polys {
+                let poly_offset = poly * poly_bytes_len;
+
+                for cases in all_cases.iter() {
+                    for range in cases.0.iter() {
+                        let range = Range {
+                            start: range.start + poly_offset,
+                            end: range.end + poly_offset,
+                        };
+                        print!("poly {} {} case: {:?}", poly, cases.1, range);
+
+                        // ensure range fits inside payload
+                        let range = if range.start >= payload.len() {
+                            println!(" outside payload len {}, skipping", payload.len());
+                            continue;
+                        } else if range.end > payload.len() {
+                            println!(" clamped to payload len {}", payload.len());
+                            Range {
+                                end: payload.len(),
+                                ..range
+                            }
+                        } else {
+                            println!();
+                            range
+                        };
+
+                        let stmt = Statement {
+                            payload_subslice: &payload[range.clone()],
+                            range: range.clone(),
+                            commit: &d.commit,
+                            common: &d.common,
+                        };
+
+                        let small_range_proof: SmallRangeProof<_> =
+                            advz.payload_proof(&payload, range.clone()).unwrap();
+                        advz.payload_verify(stmt.clone(), &small_range_proof)
+                            .unwrap()
+                            .unwrap();
+
+                        let large_range_proof: LargeRangeProof<_> =
+                            advz.payload_proof(&payload, range.clone()).unwrap();
+                        advz.payload_verify(stmt, &large_range_proof)
+                            .unwrap()
+                            .unwrap();
+                    }
                 }
             }
         }
```
