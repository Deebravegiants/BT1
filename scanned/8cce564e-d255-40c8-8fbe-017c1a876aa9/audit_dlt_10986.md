# [?] fix: shape panic handling

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-12-12
Source: https://github.com/succinctlabs/sp1/commit/f7ab24d0a6f50ca4271bac58002cfda7588e77cc
Type: security-commit

## Details
fix: shape panic handling

## Patch
### crates/prover/src/shapes.rs
```diff
@@ -139,6 +139,7 @@ pub fn build_vk_map<C: SP1ProverComponents>(
 ) -> (BTreeSet<[BabyBear; DIGEST_SIZE]>, Vec<usize>, usize) {
     let mut prover = SP1Prover::<C>::new();
     prover.vk_verification = !dummy;
+    let prover = Arc::new(prover);
     let core_shape_config = prover.core_shape_config.as_ref().expect("core shape config not found");
     let recursion_shape_config =
         prover.compress_shape_config.as_ref().expect("recursion shape config not found");
@@ -187,15 +188,17 @@ pub fn build_vk_map<C: SP1ProverComponents>(
             for _ in 0..num_compiler_workers {
                 let program_tx = program_tx.clone();
                 let shape_rx = &shape_rx;
-                let prover = &prover;
+                let prover = prover.clone();
                 let panic_tx = panic_tx.clone();
                 s.spawn(move || {
                     while let Ok((i, shape)) = shape_rx.lock().unwrap().recv() {
-                        let program = catch_unwind(AssertUnwindSafe(|| {
-                            prover.program_from_shape(false, shape.clone(), None)
-                        }));
                         let is_shrink = matches!(shape, SP1CompressProgramShape::Shrink(_));
-                        match program {
+                        let prover = prover.clone();
+                        let shape_clone = shape.clone();
+                        // Spawn on another thread to handle panics.
+                        let program_thread =
+                            s.spawn(move || prover.program_from_shape(false, shape_clone, None));
+                        match program_thread.join() {
                             Ok(program) => program_tx.send((i, program, is_shrink)).unwrap(),
                             Err(e) => {
                                 tracing::warn!(
```
