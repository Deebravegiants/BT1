# [?] fix: add oob checks when reading call_data (#11133)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-16
Source: https://github.com/noir-lang/noir/commit/7aa4e3660c41b7d00e45e4ca0d9e2077ac8170b4
Type: security-commit

## Details
fix: add oob checks when reading call_data (#11133)

## Patch
### compiler/noirc_evaluator/src/acir/arrays.rs
```diff
@@ -600,6 +600,31 @@ impl Context<'_> {
             .iter()
             .find_map(|cd| cd.index_map.get(&array).map(|idx| (cd.array_id, *idx)));
         if let Some((array_id, bus_index)) = call_data_info {
+            // Get the length of the array we want to read:
+            let array_typ = dfg.type_of_value(array);
+            let flattened_len = array_typ.flattened_size();
+            // Get the total call_data array length
+            let call_data_typ = dfg.type_of_value(array_id);
+            let call_data_len = call_data_typ.flattened_size();
+            let is_last_in_call_data =
+                bus_index + flattened_len.0 as usize == call_data_len.0 as usize;
+
+            // Check index for out of bounds in the call_data because
+            // the databus aggregates them into the call_data array.
+            // This is not needed when we access the last element, because
+            // we can benefit from the out-of-bound on call data.
+            if !is_last_in_call_data {
+                let length_var =
+                    self.acir_context.add_constant(FieldElement::from(i128::from(flattened_len.0)));
+                // Compute out-of-bounds value:
+                let in_bound = self.acir_context.less_than_var(var_index, length_var, 32)?;
+                // Add the out-of-bounds check:
+                let assert_message = "Index out of bounds".to_string();
+                let one = self.acir_context.add_constant(FieldElement::one());
+                let message = self.acir_context.generate_assertion_message_payload(assert_message);
+                self.acir_context.assert_eq_var(in_bound, one, Some(message))?;
+            }
+
             let call_data_block = self.ensure_array_is_initialized(array_id, dfg)?;
             let bus_index = self.acir_context.add_constant(FieldElement::from(bus_index as i128));
             let mut current_index = self.acir_context.add_var(bus_index, var_index)?;
```

### test_programs/execution_failure/regression_databus_out_of_bounds/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "regression_databus_out_of_bounds"
+version = "0.1.0"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/regression_databus_out_of_bounds/Prover.toml
```diff
@@ -0,0 +1,4 @@
+_x = ["0", "1", "2", "3"]
+y = ["4", "5", "6", "7"]
+_z = ["8", "9", "10", "11"]
+i = "7"
\ No newline at end of file
```

### test_programs/execution_failure/regression_databus_out_of_bounds/src/main.nr
```diff
@@ -0,0 +1,8 @@
+pub fn main(
+    _x: call_data(1) [u32; 4],
+    y: call_data(1) [u32; 4],
+    _z: call_data(1) [u32; 4],
+    i: u32,
+) -> pub u32 {
+    y[i]
+}
```
