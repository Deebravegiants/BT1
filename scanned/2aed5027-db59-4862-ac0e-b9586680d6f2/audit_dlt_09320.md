# [?] fix(invariant): panic when decoding logs with None value (#7956)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-05-21
Source: https://github.com/foundry-rs/foundry/commit/0a5b22f07ba4f2ddf525089c8ee9cdcb05e44bd9
Type: security-commit

## Details
fix(invariant): panic when decoding logs with None value (#7956)

* fix(invariant): panic when decoding logs with None value

* Changes after review: code cleanup

## Patch
### crates/evm/fuzz/src/strategies/state.rs
```diff
@@ -267,18 +267,18 @@ impl FuzzDictionary {
     /// If collected samples limit is reached then values are inserted as regular values.
     pub fn insert_sample_values(&mut self, sample_values: Vec<DynSolValue>, limit: u32) {
         for sample in sample_values {
-            let sample_type = sample.as_type().unwrap();
-            let sample_value = sample.as_word().unwrap().into();
-
-            if let Some(values) = self.sample_values.get_mut(&sample_type) {
-                if values.len() < limit as usize {
-                    values.insert(sample_value);
+            if let (Some(sample_type), Some(sample_value)) = (sample.as_type(), sample.as_word()) {
+                let sample_value = sample_value.into();
+                if let Some(values) = self.sample_values.get_mut(&sample_type) {
+                    if values.len() < limit as usize {
+                        values.insert(sample_value);
+                    } else {
+                        // Insert as state value (will be removed at the end of the run).
+                        self.insert_value(sample_value, true);
+                    }
                 } else {
-                    // Insert as state value (will be removed at the end of the run).
-                    self.insert_value(sample_value, true);
+                    self.sample_values.entry(sample_type).or_default().insert(sample_value);
                 }
-            } else {
-                self.sample_values.entry(sample_type).or_default().insert(sample_value);
             }
         }
     }
```
