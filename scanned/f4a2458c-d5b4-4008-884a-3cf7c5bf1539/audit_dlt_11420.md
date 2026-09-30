# [?] fix: lookup range from calibrate i128 overflow on `--release` compile (#619)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2023-11-18
Source: https://github.com/zkonduit/ezkl/commit/e01765d909846e258363189c686aa19ea9c10900
Type: security-commit

## Details
fix: lookup range from calibrate i128 overflow on `--release` compile (#619)

## Patch
### src/graph/mod.rs
```diff
@@ -851,6 +851,14 @@ impl GraphCircuit {
         let max_logrows = std::cmp::max(max_logrows, MIN_LOGROWS);
 
         let reserved_blinding_rows = Self::reserved_blinding_rows();
+        // check if has overflowed i128 max
+        if res.max_lookup_inputs > i128::MAX / RANGE_MULTIPLIER
+            || res.min_lookup_inputs < i128::MIN / RANGE_MULTIPLIER
+        {
+            let err_string = format!("max lookup input ({}) is too large", res.max_lookup_inputs);
+            return Err(err_string.into());
+        }
+
         let safe_range = Self::calc_safe_range(res);
 
         let max_col_size =
@@ -1063,6 +1071,7 @@ impl GraphCircuit {
         model_path: &std::path::Path,
         check_mode: CheckMode,
     ) -> Result<Self, Box<dyn std::error::Error>> {
+        params.run_args.validate()?;
         let model = Model::from_run_args(&params.run_args, model_path)?;
         Self::new_from_settings(model, params.clone(), check_mode)
     }
```

### src/lib.rs
```diff
@@ -113,6 +113,23 @@ pub struct RunArgs {
 }
 
 impl RunArgs {
+    ///
+    pub fn validate(&self) -> Result<(), Box<dyn std::error::Error>> {
+        if self.scale_rebase_multiplier < 1 {
+            return Err("scale_rebase_multiplier must be >= 1".into());
+        }
+        if self.lookup_range.0 > self.lookup_range.1 {
+            return Err("lookup_range min is greater than max".into());
+        }
+        if self.logrows < 1 {
+            return Err("logrows must be >= 1".into());
+        }
+        if self.num_inner_cols < 1 {
+            return Err("num_inner_cols must be >= 1".into());
+        }
+        Ok(())
+    }
+
     /// Export the ezkl configuration as json
     pub fn as_json(&self) -> Result<String, Box<dyn std::error::Error>> {
         let serialized = match serde_json::to_string(&self) {
```
