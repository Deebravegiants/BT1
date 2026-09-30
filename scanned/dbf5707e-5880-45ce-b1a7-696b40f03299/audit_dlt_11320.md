# [?] fix: checks for index out of bounds also for arrays (#7827)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-04-10
Source: https://github.com/noir-lang/noir/commit/7d47ca334754536cb314b87709f22f6b339a8d6c
Type: security-commit

## Details
fix: checks for index out of bounds also for arrays (#7827)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>
Co-authored-by: Maxim Vezenov <mvezenov@gmail.com>
Co-authored-by: Ary Borenszweig <asterite@gmail.com>

## Patch
### .github/benchmark_projects.yml
```diff
@@ -37,7 +37,7 @@ projects:
     timeout: 15
     compilation-timeout: 20
     execution-timeout: 1
-    compilation-memory-limit: 1500
+    compilation-memory-limit: 1600
     execution-memory-limit: 650
   rollup-base-public:
     repo: AztecProtocol/aztec-packages
```

### compiler/noirc_evaluator/src/brillig/brillig_gen/brillig_block.rs
```diff
@@ -787,13 +787,6 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
 
                 let index_variable = self.convert_ssa_single_addr_value(*index, dfg);
 
-                // Slice access checks are generated separately against the slice's dynamic length field.
-                if matches!(dfg.type_of_value(*array), Type::Array(..))
-                    && !dfg.is_safe_brillig_index(*index, *array)
-                {
-                    self.validate_array_index(array_variable, index_variable);
-                }
-
                 if dfg.is_constant(*index) {
                     self.brillig_context.codegen_load_with_offset(
                         array_variable.extract_register(),
@@ -825,13 +818,6 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
                     dfg,
                 );
 
-                // Slice access checks are generated separately against the slice's dynamic length field.
-                if matches!(dfg.type_of_value(*array), Type::Array(..))
-                    && !dfg.is_safe_index(*index, *array)
-                {
-                    self.validate_array_index(source_variable, index_register);
-                }
-
                 self.convert_ssa_array_set(
                     source_variable,
                     destination_variable,
@@ -1105,29 +1091,6 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
         }
     }
 
-    fn validate_array_index(
-        &mut self,
-        array_variable: BrilligVariable,
-        index_register: SingleAddrVariable,
-    ) {
-        let size = self.brillig_context.codegen_make_array_or_vector_length(array_variable);
-
-        let condition = SingleAddrVariable::new(self.brillig_context.allocate_register(), 1);
-
-        self.brillig_context.memory_op_instruction(
-            index_register.address,
-            size.address,
-            condition.address,
-            BrilligBinaryOp::LessThan,
-        );
-
-        self.brillig_context
-            .codegen_constrain(condition, Some("Array index out of bounds".to_owned()));
-
-        self.brillig_context.deallocate_single_addr(size);
-        self.brillig_context.deallocate_single_addr(condition);
-    }
-
     /// Array set operation in SSA returns a new array or slice that is a copy of the parameter array or slice
     /// With a specific value changed.
     ///
```

### compiler/noirc_evaluator/src/brillig/brillig_ir/codegen_memory.rs
```diff
@@ -377,13 +377,6 @@ impl<F: AcirField + DebugToString, Registers: RegisterAllocator> BrilligContext<
         self.deallocate_register(read_pointer);
     }
 
-    /// Returns a variable holding the length of a given array
-    pub(crate) fn codegen_make_array_length(&mut self, array: BrilligArray) -> SingleAddrVariable {
-        let result = SingleAddrVariable::new_usize(self.allocate_register());
-        self.usize_const_instruction(result.address, array.size.into());
-        result
-    }
-
     /// Returns a pointer to the items of a given array
     pub(crate) fn codegen_make_array_items_pointer(
         &mut self,
@@ -394,17 +387,6 @@ impl<F: AcirField + DebugToString, Registers: RegisterAllocator> BrilligContext<
         result
     }
 
-    pub(crate) fn codegen_make_array_or_vector_length(
-        &mut self,
-        variable: BrilligVariable,
-    ) -> SingleAddrVariable {
-        match variable {
-            BrilligVariable::BrilligArray(array) => self.codegen_make_array_length(array),
-            BrilligVariable::BrilligVector(vector) => self.codegen_make_vector_length(vector),
-            _ => unreachable!("ICE: Expected array or vector, got {variable:?}"),
-        }
-    }
-
     pub(crate) fn codegen_make_array_or_vector_items_pointer(
         &mut self,
         variable: BrilligVariable,
```

### compiler/noirc_evaluator/src/ssa/ir/dfg.rs
```diff
@@ -678,19 +678,6 @@ impl DataFlowGraph {
         }
     }
 
-    /// Arrays are represented as `[RC, ...items]` where RC stands for reference count.
-    /// By the time of Brillig generation we expect all constant indices
-    /// to already account for the extra offset from the RC.
-    pub(crate) fn is_safe_brillig_index(&self, index: ValueId, array: ValueId) -> bool {
-        #[allow(clippy::match_like_matches_macro)]
-        match (self.type_of_value(array), self.get_numeric_constant(index)) {
-            (Type::Array(elements, len), Some(index)) => {
-                (index.to_u128() - 1) < (len as u128 * elements.len() as u128)
-            }
-            _ => false,
-        }
-    }
-
     /// Sets the terminator instruction for the given basic block
     pub(crate) fn set_block_terminator(
         &mut self,
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -445,8 +445,25 @@ impl FunctionContext<'_> {
         let type_size = Self::convert_type(element_type).size_of_type();
         let type_size =
             self.builder.numeric_constant(type_size as u128, NumericType::length_type());
-        // This shouldn't overflow as we are reaching for an initial array offset
-        // (otherwise it would have overflowed when creating the array)
+
+        let array_type = &self.builder.type_of_value(array);
+
+        // Checks for index Out-of-bounds
+        match array_type {
+            Type::Slice(_) => {
+                self.codegen_access_check(
+                    index,
+                    length.expect("ICE: a length must be supplied for checking index"),
+                );
+            }
+            Type::Array(_, len) => {
+                let len = self.builder.numeric_constant(*len as u128, NumericType::length_type());
+                self.codegen_access_check(index, len);
+            }
+            _ => unreachable!("must have array or slice but got {array_type}"),
+        }
+
+        // This shouldn't overflow because the initial index is within array bounds
         let base_index = self.builder.set_location(location).insert_binary(
             index,
             BinaryOp::Mul { unchecked: true },
@@ -458,17 +475,6 @@ impl FunctionContext<'_> {
             let offset = self.make_offset(base_index, field_index);
             field_index += 1;
 
-            let array_type = &self.builder.type_of_value(array);
-            match array_type {
-                Type::Slice(_) => {
-                    self.codegen_slice_access_check(index, length);
-                }
-                Type::Array(..) => {
-                    // Nothing needs to done to prepare an array access on an array
-                }
-                _ => unreachable!("must have array or slice but got {array_type}"),
-            }
-
             // Reference counting in brillig relies on us incrementing reference
             // counts when nested arrays/slices are constructed or indexed. This
             // has no effect in ACIR code.
@@ -480,11 +486,10 @@ impl FunctionContext<'_> {
     /// Prepare a slice access.
     /// Check that the index being used to access a slice element
     /// is less than the dynamic slice length.
-    fn codegen_slice_access_check(&mut self, index: ValueId, length: Option<ValueId>) {
+    fn codegen_access_check(&mut self, index: ValueId, length: ValueId) {
         let index = self.make_array_index(index);
         // We convert the length as an array index type for comparison
-        let array_len = self
-            .make_array_index(length.expect("ICE: a length must be supplied for indexing slices"));
+        let array_len = self.make_array_index(length);
 
         let is_offset_out_of_bounds = self.builder.insert_binary(index, BinaryOp::Lt, array_len);
         let true_const = self.builder.numeric_constant(true, NumericType::bool());
@@ -996,10 +1001,10 @@ impl FunctionContext<'_> {
                         one,
                     );
 
-                    self.codegen_slice_access_check(arguments[2], Some(len_plus_one));
+                    self.codegen_access_check(arguments[2], len_plus_one);
                 }
                 Intrinsic::SliceRemove => {
-                    self.codegen_slice_access_check(arguments[2], Some(arguments[0]));
+                    self.codegen_access_check(arguments[2], arguments[0]);
                 }
                 _ => {
                     // Do nothing as the other intrinsics do not require checks
```

### compiler/noirc_frontend/src/tests/unused_items.rs
```diff
@@ -332,12 +332,13 @@ fn considers_struct_as_constructed_if_trait_method_is_called() {
 #[test]
 fn considers_struct_as_constructed_if_mentioned_in_let_type() {
     let src = "
-    struct Bar {}
+    pub struct Bar {}
 
-    pub fn main() {
-        let array = [];
+    pub fn foo(array: [Bar; 1]) {
         let _: Bar = array[0];
     }
+
+    fn main() {}
     ";
     assert_no_errors!(src);
 }
@@ -346,16 +347,13 @@ fn considers_struct_as_constructed_if_mentioned_in_let_type() {
 #[test]
 fn considers_struct_as_constructed_if_mentioned_in_return_type() {
     let src = "
-    struct Bar {}
+    pub struct Bar {}
 
-    fn main() {
-        let _ = foo();
-    }
-
-    fn foo() -> Bar {
-        let array = [];
+    pub fn foo(array: [Bar; 1]) -> Bar {
         array[0]
     }
+
+    fn main() {}
     ";
     assert_no_errors!(src);
 }
```

### test_programs/compile_success_no_bug/noirc_frontend_tests_unused_items_considers_struct_as_constructed_if_mentioned_in_let_type/src/main.nr
```diff
@@ -1,8 +1,9 @@
 
-    struct Bar {}
+    pub struct Bar {}
 
-    pub fn main() {
-        let array = [];
+    pub fn foo(array: [Bar; 1]) {
         let _: Bar = array[0];
     }
+
+    fn main() {}
     
\ No newline at end of file
```

### test_programs/compile_success_no_bug/noirc_frontend_tests_unused_items_considers_struct_as_constructed_if_mentioned_in_let_type/src_hash.txt
```diff
@@ -1 +1 @@
-12495805612126484999
\ No newline at end of file
+38851938633219158
\ No newline at end of file
```

### test_programs/compile_success_no_bug/noirc_frontend_tests_unused_items_considers_struct_as_constructed_if_mentioned_in_return_type/src/main.nr
```diff
@@ -1,12 +1,9 @@
 
-    struct Bar {}
+    pub struct Bar {}
 
-    fn main() {
-        let _ = foo();
-    }
-
-    fn foo() -> Bar {
-        let array = [];
+    pub fn foo(array: [Bar; 1]) -> Bar {
         array[0]
     }
+
+    fn main() {}
     
\ No newline at end of file
```

### test_programs/compile_success_no_bug/noirc_frontend_tests_unused_items_considers_struct_as_constructed_if_mentioned_in_return_type/src_hash.txt
```diff
@@ -1 +1 @@
-6802476024805115768
\ No newline at end of file
+2517654725056587726
\ No newline at end of file
```

### test_programs/execution_failure/regression_7759/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "regression_7759"
+version = "0.1.0"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/regression_7759/Prover.toml
```diff
@@ -0,0 +1,5 @@
+"v1" = "2"
+"v2" = "3"
+"v3" = "4"
+"v4" = "5"
+"index" = "2147483648" # 2 **31
\ No newline at end of file
```
