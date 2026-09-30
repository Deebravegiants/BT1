# [?] fix: increase lookup overflow slack to accomodate calibration for complex models (#640)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2023-12-02
Source: https://github.com/zkonduit/ezkl/commit/166c41eca0d0a4426f60b0bafa3220ddbd9a4b6a
Type: security-commit

## Details
fix: increase lookup overflow slack to accomodate calibration for complex models (#640)

## Patch
### src/graph/mod.rs
```diff
@@ -902,7 +902,7 @@ impl GraphCircuit {
         let num_cols = Table::<Fp>::num_cols_required(safe_range, max_col_size);
 
         // empirically determined that this is when performance starts to degrade significantly
-        if num_cols > 4 {
+        if num_cols > 5 {
             let err_string = format!(
                 "No possible lookup range can accomodate max value min and max value ({}, {})",
                 safe_range.0, safe_range.1
```

### src/graph/model.rs
```diff
@@ -599,13 +599,15 @@ impl Model {
                         debug!("intermediate min lookup inputs: {}", min);
                     }
                     debug!(
-                        "------------ output node int {}: {} \n ------------ float: {}",
+                        "------------ output node int {}: {} \n ------------ float: {} \n ------------ max: {} \n ------------ min: {}",
                         idx,
                         res.output.map(crate::fieldutils::felt_to_i32).show(),
                         res.output
                             .map(|x| crate::fieldutils::felt_to_f64(x)
                                 / scale_to_multiplier(n.out_scale))
-                            .show()
+                            .show(), 
+                        res.output.clone().into_iter().map(crate::fieldutils::felt_to_i128).max().unwrap_or(0),
+                        res.output.clone().into_iter().map(crate::fieldutils::felt_to_i128).min().unwrap_or(0),
                     );
                     results.insert(idx, vec![res.output]);
                 }
```

### tests/output_comparison.py
```diff
@@ -96,7 +96,7 @@ def compare_outputs(zk_output, onnx_output):
     witness_file = sys.argv[3]
     # settings file is fourth argument to script
     settings_file = sys.argv[4]
-    # target 
+    # target
     target = float(sys.argv[5])
     # get the ezkl output
     ezkl_output = get_ezkl_output(witness_file, settings_file)
```
