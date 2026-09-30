# [?] switch to SimpleFloorPlanner to avoid call stack overflow

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2022-07-06
Source: https://github.com/zkonduit/ezkl/commit/a34fdd8a454b014b5f6d57efdfd08067d7ba3c42
Type: security-commit

## Details
switch to SimpleFloorPlanner to avoid call stack overflow

## Patch
### src/mvmul2.rs
```diff
@@ -6,7 +6,8 @@ use halo2_proofs::{
         floor_planner::V1,
         AssignedCell, // a value Value<V> together with its global location as a Cell with region_index, row_offset, and column
         Layouter,     // layout strategy and accepter struct, a bit like a Writer
-        Value,        // basically an Option<V>, where Some(v) is called known and None is unknown
+        SimpleFloorPlanner,
+        Value, // basically an Option<V>, where Some(v) is called known and None is unknown
     },
     plonk::{
         create_proof,
@@ -76,7 +77,8 @@ impl<F: FieldExt, const NROWS: usize, const NCOLS: usize> Circuit<F>
     for MvmulCircuit<F, NROWS, NCOLS>
 {
     type Config = MvmulConfig<F, NROWS, NCOLS>;
-    type FloorPlanner = V1;
+    type FloorPlanner = SimpleFloorPlanner;
+    //    type FloorPlanner = V1;
 
     fn without_witnesses(&self) -> Self {
         // put Unknown in all the Value<Assigned>
@@ -299,8 +301,8 @@ mod tests {
 
     #[test]
     fn test_mvmul_bigger() {
-        const NROWS: usize = 30;
-        const NCOLS: usize = 40;
+        const NROWS: usize = 128;
+        const NCOLS: usize = 128; //32x52 overflows stack in verifying key creation
         let k = 4; //2^k rows
                    //        let avals: [u64; 32] = rand.rand();
         let m_a: nalgebra::SMatrix<u64, NROWS, NCOLS> =
@@ -311,6 +313,7 @@ mod tests {
         println!("a: {}", m_a);
         println!("v: {}", m_v);
         println!("u: {}", m_u);
+        println!("{}", NROWS * NCOLS + NROWS + NCOLS);
 
         let mut a: Vec<Vec<Value<Assigned<Fp>>>> = Vec::new();
         for i in 0..NROWS {
@@ -350,7 +353,7 @@ mod tests {
         create_proof(&params, &pk, &[circuit], &[&[]], &mut rng, &mut transcript)
             .expect("proof generation should not fail");
         let proof = transcript.finalize();
-        println!("{:?}", proof);
+        //println!("{:?}", proof);
         let strategy = SingleVerifier::new(&params);
         let mut transcript = Blake2bRead::<_, _, Challenge255<_>>::init(&proof[..]);
         assert!(verify_proof(&params, pk.get_vk(), strategy, &[&[]], &mut transcript).is_ok());
```
