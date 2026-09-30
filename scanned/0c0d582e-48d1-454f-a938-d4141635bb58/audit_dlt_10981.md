# [?] fix: use wrapping add to prevent overflowing (#737)

## Summary
Severity: Unknown
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-08-21
Source: https://github.com/succinctlabs/sp1/commit/3c778419c4376b5a2de4f564037681359a2469f5
Type: security-commit

## Details
fix: use wrapping add to prevent overflowing (#737)

* make test serial

* ok

* ok

## Patch
### crates/core/machine/src/control_flow/jal/trace.rs
```diff
@@ -52,7 +52,7 @@ impl<F: PrimeField32> MachineAir<F> for JalChip {
                     if idx < input.jal_events.len() {
                         let event = &input.jal_events[idx];
                         cols.is_real = F::one();
-                        let low_limb = ((event.0.pc + event.0.b) & 0xFFFF) as u16;
+                        let low_limb = (event.0.pc.wrapping_add(event.0.b) & 0xFFFF) as u16;
                         blu.add_bit_range_check(low_limb / 4, 14);
                         cols.add_operation.populate(&mut blu, event.0.pc, event.0.b);
                         if !event.0.op_a_0 {
```

### crates/core/machine/src/control_flow/jalr/trace.rs
```diff
@@ -87,7 +87,7 @@ impl JalrChip {
         // `event.c` is unused, since we ought to use a `JalrEvent` rather than a `JumpEvent`.
         cols.is_real = F::one();
         cols.op_a_value = event.a.into();
-        let low_limb = ((event.b + imm) & 0xFFFF) as u16;
+        let low_limb = (event.b.wrapping_add(imm) & 0xFFFF) as u16;
         blu.add_bit_range_check(low_limb / 4, 14);
         cols.add_operation.populate(blu, event.b, imm);
         if !event.op_a_0 {
```

### crates/prover/src/shapes.rs
```diff
@@ -632,6 +632,7 @@ mod tests {
         recursion::normalize_program_from_input,
         CORE_LOG_BLOWUP,
     };
+    use serial_test::serial;
     use sp1_core_executor::{SP1Context, ELEMENT_THRESHOLD, MAX_PROGRAM_SIZE};
     use sp1_core_machine::{
         bytes::columns::NUM_BYTE_PREPROCESSED_COLS, io::SP1Stdin,
@@ -746,6 +747,7 @@ mod tests {
     }
 
     #[tokio::test]
+    #[serial]
     async fn test_core_shape_fit() {
         setup_logger();
         let elf = test_artifacts::FIBONACCI_ELF;
@@ -779,8 +781,17 @@ mod tests {
     }
 
     #[tokio::test]
+    #[serial]
     async fn test_build_vk_map() {
         setup_logger();
+
+        // Use a temporary directory for the vk_map file to avoid conflicts
+        let temp_dir = std::env::temp_dir();
+        let vk_map_path = temp_dir.join("vk_map.bin");
+
+        // Clean up any existing file from previous runs
+        let _ = std::fs::remove_file(&vk_map_path);
+
         let prover = SP1ProverBuilder::new().build().await;
 
         let elf = test_artifacts::FIBONACCI_ELF;
@@ -821,7 +832,7 @@ mod tests {
         let shape_indices_len = shape_indices.len();
 
         build_vk_map_to_file(
-            "../../../".into(),
+            temp_dir,
             DEFAULT_ARITY,
             false,
             1,
@@ -835,8 +846,10 @@ mod tests {
         tracing::info!("Built vk map with {} shapes", shape_indices_len);
 
         // Build a new prover that performs the vk verification check using the built vk map.
-        let prover =
-            SP1ProverBuilder::new().with_vk_map_path("../../../vk_map.bin".into()).build().await;
+        let prover = SP1ProverBuilder::new()
+            .with_vk_map_path(vk_map_path.display().to_string())
+            .build()
+            .await;
 
         tracing::info!("Rebuilt prover with vk map.");
 
@@ -862,6 +875,6 @@ mod tests {
             .verify_shrink(&shrink_proof, &vk)
             .expect("Failed to verify shrink proof");
 
-        std::fs::remove_file("../../../vk_map.bin").unwrap();
+        std::fs::remove_file(vk_map_path).unwrap();
     }
 }
```
