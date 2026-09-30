# [?] fix: handle panic during shape vkey setup

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2024-12-12
Source: https://github.com/succinctlabs/sp1/commit/489324b16ee973cfcd273387a907ea9f28d2feea
Type: security-commit

## Details
fix: handle panic during shape vkey setup

## Patch
### crates/prover/src/shapes.rs
```diff
@@ -130,7 +130,7 @@ pub fn check_shapes<C: SP1ProverComponents>(
     compress_ok
 }
 
-pub fn build_vk_map<C: SP1ProverComponents>(
+pub fn build_vk_map<C: SP1ProverComponents + 'static>(
     reduce_batch_size: usize,
     dummy: bool,
     num_compiler_workers: usize,
@@ -196,8 +196,9 @@ pub fn build_vk_map<C: SP1ProverComponents>(
                         let prover = prover.clone();
                         let shape_clone = shape.clone();
                         // Spawn on another thread to handle panics.
-                        let program_thread =
-                            s.spawn(move || prover.program_from_shape(false, shape_clone, None));
+                        let program_thread = std::thread::spawn(move || {
+                            prover.program_from_shape(false, shape_clone, None)
+                        });
                         match program_thread.join() {
                             Ok(program) => program_tx.send((i, program, is_shrink)).unwrap(),
                             Err(e) => {
@@ -219,18 +220,29 @@ pub fn build_vk_map<C: SP1ProverComponents>(
                 let vk_tx = vk_tx.clone();
                 let program_rx = &program_rx;
                 let prover = &prover;
+                let panic_tx = panic_tx.clone();
                 s.spawn(move || {
                     let mut done = 0;
                     while let Ok((i, program, is_shrink)) = program_rx.lock().unwrap().recv() {
-                        let vk = tracing::debug_span!("setup for program {}", i).in_scope(|| {
+                        let prover = prover.clone();
+                        let vk_thread = std::thread::spawn(move || {
                             if is_shrink {
                                 prover.shrink_prover.setup(&program).1
                             } else {
                                 prover.compress_prover.setup(&program).1
                             }
                         });
+                        let vk = tracing::debug_span!("setup for program {}", i)
+                            .in_scope(|| vk_thread.join());
                         done += 1;
 
+                        if let Err(e) = vk {
+                            tracing::error!("failed to setup program {}: {:?}", i, e);
+                            panic_tx.send(i).unwrap();
+                            continue;
+                        }
+                        let vk = vk.unwrap();
+
                         let vk_digest = vk.hash_babybear();
                         tracing::info!(
                             "program {} = {:?}, {}% done",
@@ -269,7 +281,7 @@ pub fn build_vk_map<C: SP1ProverComponents>(
     (vk_set, panic_indices, height)
 }
 
-pub fn build_vk_map_to_file<C: SP1ProverComponents>(
+pub fn build_vk_map_to_file<C: SP1ProverComponents + 'static>(
     build_dir: PathBuf,
     reduce_batch_size: usize,
     dummy: bool,
```
