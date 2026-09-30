# [?] fix(acir): Extend slice on dynamic insertion and compilation panic when flattening (#10051)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-10-01
Source: https://github.com/noir-lang/noir/commit/79ef33bd7b9325ea91ec174e53562cb13874c4a1
Type: security-commit

## Details
fix(acir): Extend slice on dynamic insertion and compilation panic when flattening (#10051)

## Patch
### compiler/noirc_evaluator/src/acir/arrays.rs
```diff
@@ -949,7 +949,7 @@ impl Context<'_> {
         }
     }
 
-    fn read_dynamic_array(
+    pub(super) fn read_dynamic_array(
         &mut self,
         source: BlockId,
         array_len: usize,
```

### compiler/noirc_evaluator/src/acir/call/intrinsics/slice_ops.rs
```diff
@@ -279,7 +279,7 @@ impl Context<'_> {
         let one = self.acir_context.add_constant(FieldElement::one());
         let new_slice_length = self.acir_context.add_var(slice_length, one)?;
 
-        let slice_size = super::super::arrays::flattened_value_size(&slice);
+        let mut slice_size = super::arrays::flattened_value_size(&slice);
 
         // Fetch the flattened index from the user provided index argument.
         let element_size = slice_typ.element_size();
@@ -293,12 +293,18 @@ impl Context<'_> {
         // We need to a fully flat list of AcirVar's as a dynamic array is represented with flat memory.
         let mut inner_elem_size_usize = 0;
         let mut flattened_elements = Vec::new();
+        let mut new_value_types = Vec::new();
         for elem in elements_to_insert {
             let element = self.convert_value(*elem, dfg);
-            let elem_size = super::super::super::arrays::flattened_value_size(&element);
+            // Flatten into (AcirVar, NumericType) pairs
+            let flat_element = self.flatten(&element)?;
+            let elem_size = flat_element.len();
             inner_elem_size_usize += elem_size;
-            let mut flat_elem = element.flatten().into_iter().map(|(var, _)| var).collect();
-            flattened_elements.append(&mut flat_elem);
+            slice_size += elem_size;
+            for (var, typ) in flat_element {
+                flattened_elements.push(var);
+                new_value_types.push(typ);
+            }
         }
         let inner_elem_size = self.acir_context.add_constant(inner_elem_size_usize);
         // Set the maximum flattened index at which a new element should be inserted.
@@ -318,10 +324,10 @@ impl Context<'_> {
             let current_index = self.acir_context.add_constant(i);
 
             // Check that we are above the lower bound of the insertion index
-            let greater_eq_than_idx =
+            let is_after_insert =
                 self.acir_context.more_than_eq_var(current_index, flat_user_index, 64)?;
             // Check that we are below the upper bound of the insertion index
-            let less_than_idx =
+            let is_before_insert =
                 self.acir_context.less_than_var(current_index, max_flat_user_index, 64)?;
 
             // Read from the original slice the value we want to insert into our new slice.
@@ -335,9 +341,9 @@ impl Context<'_> {
                     self.acir_context.add_constant(i - inner_elem_size_usize);
 
                 let use_shifted_index_pred =
-                    self.acir_context.mul_var(index_minus_elem_size, greater_eq_than_idx)?;
+                    self.acir_context.mul_var(index_minus_elem_size, is_after_insert)?;
 
-                let not_pred = self.acir_context.sub_var(one, greater_eq_than_idx)?;
+                let not_pred = self.acir_context.sub_var(one, is_after_insert)?;
                 let use_current_index_pred = self.acir_context.mul_var(not_pred, current_index)?;
 
                 self.acir_context.add_var(use_shifted_index_pred, use_current_index_pred)?
@@ -348,7 +354,7 @@ impl Context<'_> {
 
             // Final predicate to determine whether we are within the insertion bounds
             let should_insert_value_pred =
-                self.acir_context.mul_var(greater_eq_than_idx, less_than_idx)?;
+                self.acir_context.mul_var(is_after_insert, is_before_insert)?;
             let insert_value_pred = self
                 .acir_context
                 .mul_var(flattened_elements[current_insert_index], should_insert_value_pred)?;
@@ -378,7 +384,9 @@ impl Context<'_> {
                 None
             };
 
-        let value_types = slice.flat_numeric_types();
+        let mut value_types = slice.flat_numeric_types();
+        // We can safely append the value types to the end as we expect the types to be the same for each element.
+        value_types.append(&mut new_value_types);
         assert_eq!(
             value_types.len(),
             slice_size,
@@ -453,7 +461,7 @@ impl Context<'_> {
         let one = self.acir_context.add_constant(FieldElement::one());
         let new_slice_length = self.acir_context.sub_var(slice_length, one)?;
 
-        let slice_size = super::super::arrays::flattened_value_size(&slice);
+        let slice_size = super::arrays::flattened_value_size(&slice);
 
         let new_slice = self.read_array(slice)?;
 
@@ -482,7 +490,7 @@ impl Context<'_> {
         for res in &result_ids[2..(2 + element_size)] {
             let element =
                 self.array_get_value(&dfg.type_of_value(*res), block_id, &mut temp_index)?;
-            let elem_size = super::super::arrays::flattened_value_size(&element);
+            let elem_size = super::arrays::flattened_value_size(&element);
             popped_elements_size += elem_size;
             popped_elements.push(element);
         }
@@ -528,7 +536,7 @@ impl Context<'_> {
 
         let new_slice_val = AcirValue::Array(new_slice);
         let element_type_sizes =
-            if super::super::arrays::array_has_constant_element_size(&slice_typ).is_none() {
+            if super::arrays::array_has_constant_element_size(&slice_typ).is_none() {
                 Some(self.init_element_type_sizes_array(
                     &slice_typ,
                     slice_contents,
```

### compiler/noirc_evaluator/src/acir/mod.rs
```diff
@@ -847,6 +847,36 @@ impl<'a> Context<'a> {
 
         self.acir_context.truncate_var(var, bit_size, max_bit_size)
     }
+
+    /// Fetch a flat list of ([AcirVar], [AcirType]).
+    ///
+    /// Flattens an [AcirValue] into a vector of `(AcirVar, AcirType)`.
+    ///
+    /// This is an extension of [AcirValue::flatten] that also supports [AcirValue::DynamicArray].
+    fn flatten(&mut self, value: &AcirValue) -> Result<Vec<(AcirVar, NumericType)>, RuntimeError> {
+        Ok(match value {
+            AcirValue::Var(var, typ) => vec![(*var, typ.to_numeric_type())],
+            AcirValue::Array(array) => {
+                let mut result = Vec::new();
+                for elem in array {
+                    result.extend(self.flatten(elem)?);
+                }
+                result
+            }
+            AcirValue::DynamicArray(AcirDynamicArray { block_id, len, .. }) => {
+                let elements = self.read_dynamic_array(*block_id, *len)?;
+                let mut result = Vec::new();
+
+                for value in elements {
+                    match value {
+                        AcirValue::Var(var, typ) => result.push((var, typ.to_numeric_type())),
+                        _ => unreachable!("ICE: Dynamic memory should already be flat"),
+                    }
+                }
+                result
+            }
+        })
+    }
 }
 
 /// Check post ACIR generation properties
```

### compiler/noirc_evaluator/src/acir/tests/intrinsics.rs
```diff
@@ -168,7 +168,6 @@ fn slice_pop_front() {
     ");
 }
 
-// TODO(https://github.com/noir-lang/noir/issues/10015)
 #[test]
 fn slice_insert() {
     let src = "
@@ -178,17 +177,20 @@ fn slice_insert() {
         v6 = array_set v4, index v0, value Field 4
         v10, v11 = call slice_insert(u32 3, v6, v1, Field 10) -> (u32, [Field])
         constrain v10 == v1
-        v13 = array_set v11, index v0, value Field 20
+        v13 = array_set mut v11, index v0, value Field 20
         return
     }
     ";
     let program = ssa_to_acir_program(src);
 
     // Insert does comparisons on every index for the value that should be written into the resulting slice
+    //
     // You can see how w1 is asserted to equal 4
     // Memory block 1 is our original slice
-    // Memory block 2 is our temporary slice while shifting. You can see its contents are all w6 (which is equal to 0).
-    // TODO(https://github.com/noir-lang/noir/issues/10015): Memory block 3 is our final slice which remains three elements. This is incorrect.
+    // Memory block 2 is our slice created by our insert operation. You can see its contents all start as w6 (which is equal to 0).
+    // We then write into b2 four times at the appropriate shifted indices.
+    //
+    // As we have marked the `array_set` as `mut` we then write directly into that slice.
     // The Brillig calls are to our stdlib quotient directive
     assert_circuit_snapshot!(program, @r"
     func 0
@@ -203,7 +205,7 @@ fn slice_insert() {
     ASSERT w5 = 4
     WRITE b1[w0] = w5
     ASSERT w6 = 0
-    INIT b2 = [w6, w6, w6]
+    INIT b2 = [w6, w6, w6, w6]
     BRILLIG CALL func: 0, inputs: [-w1 + 18446744073709551616, 18446744073709551616], outputs: [w7, w8]
     BLACKBOX::RANGE input: w7, bits: 1
     BLACKBOX::RANGE input: w8, bits: 64
@@ -243,14 +245,23 @@ fn slice_insert() {
     ASSERT w29 = w23*w25 - w23 + 1
     ASSERT w30 = -10*w23*w25 + w28*w29 + 10*w23
     WRITE b2[w2] = w30
+    BRILLIG CALL func: 0, inputs: [-w1 + 18446744073709551619, 18446744073709551616], outputs: [w31, w32]
+    BLACKBOX::RANGE input: w31, bits: 1
+    BLACKBOX::RANGE input: w32, bits: 64
+    ASSERT w32 = -w1 - 18446744073709551616*w31 + 18446744073709551619
+    BRILLIG CALL func: 0, inputs: [-w1 + 18446744073709551618, 18446744073709551616], outputs: [w33, w34]
+    BLACKBOX::RANGE input: w33, bits: 1
+    BLACKBOX::RANGE input: w34, bits: 64
+    ASSERT w34 = -w1 - 18446744073709551616*w33 + 18446744073709551618
+    ASSERT w35 = -w31 + 3
+    READ w36 = b1[w35]
+    ASSERT w37 = w31*w33 - w31 + 1
+    ASSERT w38 = -10*w31*w33 + w36*w37 + 10*w31
+    WRITE b2[w3] = w38
     ASSERT w1 = 4
-    READ w31 = b2[w6]
-    READ w32 = b2[w21]
-    READ w33 = b2[w2]
-    INIT b3 = [w31, w32, w33]
-    ASSERT w34 = 20
-    WRITE b3[w0] = w34
-
+    ASSERT w39 = 20
+    WRITE b2[w0] = w39
+    
     unconstrained func 0
     0: @10 = const u32 2
     1: @11 = const u32 0
@@ -273,17 +284,22 @@ fn slice_remove() {
         v11, v12, v13 = call slice_remove(u32 3, v8, v1) -> (u32, [Field], Field)
         constrain v11 == v1
         constrain v13 == v2
-        v15 = array_set v12, index v0, value Field 20
+        v15 = array_set mut v12, index v0, value Field 20
         return
     }
     ";
     let program = ssa_to_acir_program(src);
 
     // Remove does comparisons on every index for the value that should be written into the resulting slice
-    // You can see how w1 is asserted to equal 4
+    // You can see how w1 is asserted to equal 2
+    //
     // Memory block 1 is our original slice
-    // Memory block 2 is our temporary slice while shifting.
-    // Memory block 3 is our final slice which remains three elements.
+    // Memory block 2 is our final slice which remains three elements. You can see that it is initialized to contain the same values as b1.
+    // Two writes to b2 and two reads from b1 at the shifted indices is what we expect as we skip the removal window when reading from
+    // the initial slice input. This logic protects against OOB errors from the skipping the removal window.
+    // We only expect as many writes to b2 and reads b1 as there are elements in the final slice.
+    //
+    // As we have marked the `array_set` as `mut` we then write directly into that slice.
     // The Brillig calls are to our stdlib quotient directive
     assert_circuit_snapshot!(program, @r"
     func 0
@@ -319,13 +335,9 @@ fn slice_remove() {
     WRITE b2[w9] = w20
     ASSERT w1 = 2
     ASSERT w12 = w2
-    READ w21 = b2[w7]
-    READ w22 = b2[w9]
-    READ w23 = b2[w3]
-    INIT b3 = [w21, w22, w23]
-    ASSERT w24 = 20
-    WRITE b3[w0] = w24
-
+    ASSERT w21 = 20
+    WRITE b2[w0] = w21
+    
     unconstrained func 0
     0: @10 = const u32 2
     1: @11 = const u32 0
```

### test_programs/execution_success/slice_dynamic_insert/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "slice_dynamic_insert"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/slice_dynamic_insert/Prover.toml
```diff
@@ -0,0 +1,2 @@
+array = [1, 2, 3, 4, 5]
+x = 5
\ No newline at end of file
```

### test_programs/execution_success/slice_dynamic_insert/src/main.nr
```diff
@@ -0,0 +1,30 @@
+fn main(x: u32, array: [Field; 5]) {
+    insert(x, array);
+    insert_dynamic_array(x, array);
+}
+
+fn insert(x: u32, array: [Field; 5]) {
+    let mut slice = array.as_slice();
+
+    assert_eq(x, 5);
+    slice = slice.insert(x - 2, 10);
+    assert_eq(slice.len(), 6);
+    let expected = &[1, 2, 3, 10, 4, 5];
+    for i in 0..6 {
+        assert_eq(slice[i], expected[i]);
+    }
+}
+
+fn insert_dynamic_array(x: u32, array: [Field; 5]) {
+    let mut value_to_insert = array;
+    value_to_insert[x - 1] = 10;
+    let mut slice = &[array, array, array];
+    slice = slice.insert(x - 3, value_to_insert);
+    assert_eq(slice.len(), 4);
+    let expected = &[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 10], [1, 2, 3, 4, 5]];
+    for i in 0..3 {
+        for j in 0..5 {
+            assert_eq(slice[i][j], expected[i][j]);
+        }
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/slice_dynamic_insert/execute__tests__expanded.snap
```diff
@@ -0,0 +1,41 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main(x: u32, array: [Field; 5]) {
+    insert(x, array);
+    insert_dynamic_array(x, array);
+}
+
+fn insert(x: u32, array: [Field; 5]) {
+    let mut slice: [Field] = array.as_slice();
+    assert(x == 5_u32);
+    slice = slice.insert(x - 2_u32, 10_Field);
+    assert(slice.len() == 6_u32);
+    let expected: [Field] = &[1_Field, 2_Field, 3_Field, 10_Field, 4_Field, 5_Field];
+    for i in 0_u32..6_u32 {
+        assert(slice[i] == expected[i]);
+    }
+}
+
+fn insert_dynamic_array(x: u32, array: [Field; 5]) {
+    let mut value_to_insert: [Field; 5] = array;
+    {
+        let i_4439: u32 = x - 1_u32;
+        value_to_insert[i_4439] = 10_Field;
+    };
+    let mut slice: [[Field; 5]] = &[array, array, array];
+    slice = slice.insert(x - 3_u32, value_to_insert);
+    assert(slice.len() == 4_u32);
+    let expected: [[Field; 5]] = &[
+        [1_Field, 2_Field, 3_Field, 4_Field, 5_Field],
+        [1_Field, 2_Field, 3_Field, 4_Field, 5_Field],
+        [1_Field, 2_Field, 3_Field, 4_Field, 10_Field],
+        [1_Field, 2_Field, 3_Field, 4_Field, 5_Field],
+    ];
+    for i in 0_u32..3_u32 {
+        for j in 0_u32..5_u32 {
+            assert(slice[i][j] == expected[i][j]);
+        }
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/slice_dynamic_insert/execute__tests__stdout.snap
```diff
@@ -0,0 +1,5 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stdout
+---
+
```
