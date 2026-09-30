# [?] fix: accomodate modules in col-overflow (#777)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2024-04-18
Source: https://github.com/zkonduit/ezkl/commit/4a93d318699527394bd533a18baaaae32555d513
Type: security-commit

## Details
fix: accomodate modules in col-overflow (#777)

## Patch
### .github/workflows/rust.yml
```diff
@@ -354,7 +354,7 @@ jobs:
 
   prove-and-verify-tests:
     runs-on: non-gpu
-    needs: [build, library-tests, docs, python-tests, python-integration-tests]
+    needs: [build, library-tests, docs]
     steps:
       - uses: actions/checkout@v4
       - uses: actions-rs/toolchain@v1
@@ -394,14 +394,18 @@ jobs:
       - name: Replace memory definition in nodejs
         run: |
           sed -i "3s|.*|imports['env'] = {memory: new WebAssembly.Memory({initial:20,maximum:65536,shared:true})}|" tests/wasm/nodejs/ezkl.js
+      - name: KZG prove and verify tests (public outputs + column overflow)
+        run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_with_overflow_::w
+      - name: KZG prove and verify tests (public outputs + fixed params + column overflow)
+        run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_with_overflow_fixed_params_
+      - name: KZG prove and verify tests (hashed inputs + column overflow)
+        run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_with_overflow_hashed_inputs_
       - name: KZG prove and verify tests (public outputs)
         run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_tight_lookup_::t
       - name: IPA prove and verify tests
         run: cargo nextest run --release --verbose tests::ipa_prove_and_verify_::t --test-threads 1
       - name: IPA prove and verify tests (ipa outputs)
         run: cargo nextest run --release --verbose tests::ipa_prove_and_verify_ipa_output
-      - name: KZG prove and verify tests (public outputs + column overflow)
-        run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_with_overflow_::w
       - name: KZG prove and verify tests single inner col
         run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_single_col
       - name: KZG prove and verify tests triple inner col
@@ -412,8 +416,6 @@ jobs:
         run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_octuple_col --test-threads 8
       - name: KZG prove and verify tests (kzg outputs)
         run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_kzg_output
-      - name: KZG prove and verify tests (public outputs + fixed params + column overflow)
-        run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_with_overflow_fixed_params_
       - name: KZG prove and verify tests (public outputs)
         run: cargo nextest run --release --verbose tests::kzg_prove_and_verify_::t
       - name: KZG prove and verify tests (public inputs)
```

### src/execute.rs
```diff
@@ -1228,22 +1228,14 @@ pub(crate) fn calibrate(
     );
 
     if matches!(target, CalibrationTarget::Resources { col_overflow: true }) {
-        let lookup_log_rows = ((best_params.run_args.lookup_range.1
-            - best_params.run_args.lookup_range.0) as f32)
-            .log2()
-            .ceil() as u32
-            + 1;
-        let mut reduction = std::cmp::max(
-            (best_params
-                .model_instance_shapes
-                .iter()
-                .map(|x| x.iter().product::<usize>())
-                .sum::<usize>() as f32)
-                .log2()
-                .ceil() as u32
-                + 1,
-            lookup_log_rows,
-        );
+        let lookup_log_rows = best_params.lookup_log_rows_with_blinding();
+        let module_log_row = best_params.module_constraint_logrows_with_blinding();
+        let instance_logrows = best_params.log2_total_instances_with_blinding();
+        let dynamic_lookup_logrows = best_params.dynamic_lookup_and_shuffle_logrows_with_blinding();
+
+        let mut reduction = std::cmp::max(lookup_log_rows, module_log_row);
+        reduction = std::cmp::max(reduction, instance_logrows);
+        reduction = std::cmp::max(reduction, dynamic_lookup_logrows);
         reduction = std::cmp::max(reduction, crate::graph::MIN_LOGROWS);
 
         info!(
```

### src/graph/mod.rs
```diff
@@ -483,7 +483,22 @@ pub struct GraphSettings {
 }
 
 impl GraphSettings {
-    fn model_constraint_logrows(&self) -> u32 {
+    /// Calc the number of rows required for lookup tables
+    pub fn lookup_log_rows(&self) -> u32 {
+        ((self.run_args.lookup_range.1 - self.run_args.lookup_range.0) as f32)
+            .log2()
+            .ceil() as u32
+    }
+
+    /// Calc the number of rows required for lookup tables
+    pub fn lookup_log_rows_with_blinding(&self) -> u32 {
+        ((self.run_args.lookup_range.1 - self.run_args.lookup_range.0) as f32
+            + RESERVED_BLINDING_ROWS as f32)
+            .log2()
+            .ceil() as u32
+    }
+
+    fn model_constraint_logrows_with_blinding(&self) -> u32 {
         (self.num_rows as f64 + RESERVED_BLINDING_ROWS as f64)
             .log2()
             .ceil() as u32
@@ -495,14 +510,31 @@ impl GraphSettings {
             .ceil() as u32
     }
 
+    /// calculate the number of rows required for the dynamic lookup and shuffle
+    pub fn dynamic_lookup_and_shuffle_logrows_with_blinding(&self) -> u32 {
+        (self.total_dynamic_col_size as f64
+            + self.total_shuffle_col_size as f64
+            + RESERVED_BLINDING_ROWS as f64)
+            .log2()
+            .ceil() as u32
+    }
+
     fn dynamic_lookup_and_shuffle_col_size(&self) -> usize {
         self.total_dynamic_col_size + self.total_shuffle_col_size
     }
 
-    fn module_constraint_logrows(&self) -> u32 {
+    /// calculate the number of rows required for the module constraints
+    pub fn module_constraint_logrows(&self) -> u32 {
         (self.module_sizes.max_constraints() as f64).log2().ceil() as u32
     }
 
+    /// calculate the number of rows required for the module constraints
+    pub fn module_constraint_logrows_with_blinding(&self) -> u32 {
+        (self.module_sizes.max_constraints() as f64 + RESERVED_BLINDING_ROWS as f64)
+            .log2()
+            .ceil() as u32
+    }
+
     fn constants_logrows(&self) -> u32 {
         (self.total_const_size as f64 / self.run_args.num_inner_cols as f64)
             .log2()
@@ -529,6 +561,14 @@ impl GraphSettings {
         std::cmp::max((sum as f64).log2().ceil() as u32, 1)
     }
 
+    /// calculate the log2 of the total number of instances
+    pub fn log2_total_instances_with_blinding(&self) -> u32 {
+        let sum = self.total_instances().iter().sum::<usize>() + RESERVED_BLINDING_ROWS;
+
+        // max between 1 and the log2 of the sums
+        std::cmp::max((sum as f64).log2().ceil() as u32, 1)
+    }
+
     /// save params to file
     pub fn save(&self, path: &std::path::PathBuf) -> Result<(), std::io::Error> {
         // buf writer
@@ -1133,7 +1173,7 @@ impl GraphCircuit {
         );
 
         // These are upper limits, going above these is wasteful, but they are not hard limits
-        let model_constraint_logrows = self.settings().model_constraint_logrows();
+        let model_constraint_logrows = self.settings().model_constraint_logrows_with_blinding();
         let min_bits = self.table_size_logrows(safe_lookup_range, max_range_size)?;
         let constants_logrows = self.settings().constants_logrows();
         max_logrows = std::cmp::min(
```

### src/python.rs
```diff
@@ -1168,26 +1168,21 @@ fn prove(
     settings_path=PathBuf::from(DEFAULT_SETTINGS),
     vk_path=PathBuf::from(DEFAULT_VK),
     srs_path=None,
-    non_reduced_srs=DEFAULT_USE_REDUCED_SRS_FOR_VERIFICATION.parse::<bool>().unwrap(),
+    reduced_srs=DEFAULT_USE_REDUCED_SRS_FOR_VERIFICATION.parse::<bool>().unwrap(),
 ))]
 fn verify(
     proof_path: PathBuf,
     settings_path: PathBuf,
     vk_path: PathBuf,
     srs_path: Option<PathBuf>,
-    non_reduced_srs: bool,
+    reduced_srs: bool,
 ) -> Result<bool, PyErr> {
-    crate::execute::verify(
-        proof_path,
-        settings_path,
-        vk_path,
-        srs_path,
-        non_reduced_srs,
-    )
-    .map_err(|e| {
-        let err_str = format!("Failed to run verify: {}", e);
-        PyRuntimeError::new_err(err_str)
-    })?;
+    crate::execute::verify(proof_path, settings_path, vk_path, srs_path, reduced_srs).map_err(
+        |e| {
+            let err_str = format!("Failed to run verify: {}", e);
+            PyRuntimeError::new_err(err_str)
+        },
+    )?;
 
     Ok(true)
 }
```

### tests/integration_tests.rs
```diff
@@ -899,7 +899,7 @@ mod native_tests {
             seq!(N in 0..=45 {
 
                 #(#[test_case(WASM_TESTS[N])])*
-                fn prove_and_verify_with_overflow_(test: &str) {
+                fn kzg_prove_and_verify_with_overflow_(test: &str) {
                     crate::native_tests::init_binary();
                     // crate::native_tests::init_wasm();
                     let test_dir = TempDir::new(test).unwrap();
@@ -912,7 +912,20 @@ mod native_tests {
                 }
 
                 #(#[test_case(WASM_TESTS[N])])*
-                fn prove_and_verify_with_overflow_fixed_params_(test: &str) {
+                fn kzg_prove_and_verify_with_overflow_hashed_inputs_(test: &str) {
+                    crate::native_tests::init_binary();
+                    // crate::native_tests::init_wasm();
+                    let test_dir = TempDir::new(test).unwrap();
+                    env_logger::init();
+                    let path = test_dir.path().to_str().unwrap(); crate::native_tests::mv_test_(path, test);
+                    prove_and_verify(path, test.to_string(), "safe", "hashed", "private", "public", 1, None, true, "single", Commitments::KZG, 2);
+                    #[cfg(not(feature = "icicle"))]
+                    run_js_tests(path, test.to_string(), "testWasm", false);
+                    // test_dir.close().unwrap();
+                }
+
+                #(#[test_case(WASM_TESTS[N])])*
+                fn kzg_prove_and_verify_with_overflow_fixed_params_(test: &str) {
                     crate::native_tests::init_binary();
                     // crate::native_tests::init_wasm();
                     let test_dir = TempDir::new(test).unwrap();
```
