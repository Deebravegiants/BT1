# [?] fix: attach the logical OOB payload whenever the memory-op index is scaled (#13776)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-09-22
Source: https://github.com/noir-lang/noir/commit/952378fc0d72883c578149e9f00b757d9516b711
Type: security-commit

## Details
fix: attach the logical OOB payload whenever the memory-op index is scaled (#13776)

## Patch
### compiler/noirc_evaluator/src/acir/arrays.rs
```diff
@@ -312,7 +312,7 @@ impl Context<'_> {
     /// this way does not divide, and reports the flattened coordinates as before.
     ///
     /// Returns `None` for an access whose implicit check already reports logical coordinates
-    /// (an element of a single cell), and for a vector, whose length is not known here.
+    /// (see [`index_needs_logical_payload`]), and for a vector, whose length is not known here.
     fn logical_index_out_of_bounds_payload(
         &mut self,
         array_typ: &Type,
@@ -322,13 +322,11 @@ impl Context<'_> {
         let Type::Array(element_types, len) = array_typ else {
             return Ok(None);
         };
-        let element_size = array_typ.element_size().0;
-        let element_flattened_size: FlattenedLength =
-            element_types.iter().map(|typ| typ.flattened_size()).sum();
-        if element_size == 0 || element_flattened_size.0 == 1 {
+        if !index_needs_logical_payload(element_types) {
             return Ok(None);
         }
 
+        let element_size = array_typ.element_size().0;
         let index_var = self.convert_numeric_value(index, dfg)?;
         let index_expr = self.acir_context.var_to_expression(index_var)?;
         let Some(logical_index) = divide_expression(&index_expr, element_size) else {
@@ -1679,6 +1677,26 @@ pub(super) fn flattened_value_size(value: &AcirValue) -> FlattenedLength {
     }
 }
 
+/// Returns whether an out-of-bounds access to an array of these element types needs a payload
+/// to report the logical index and length, because the memory op's own check reports coordinates
+/// scaled away from them.
+///
+/// The index SSA generation hands the memory op is `element_size * logical + field`, and the op
+/// scales that again by the cells each field occupies, so the op's check reports the program's
+/// own coordinates only when neither factor changes anything: one field per element, and one
+/// cell for that field. Either factor alone is not enough. An element whose fields flatten to a
+/// single cell still has its index scaled by `element_size` when it has more than one field —
+/// the others are zero-sized — and an element of a single field still has its index scaled by
+/// that field's width when the field spans several cells.
+///
+/// An element with no fields at all has no index to scale, and no `element_size` to divide by.
+fn index_needs_logical_payload(element_types: &[Type]) -> bool {
+    let element_size = element_types.len();
+    let element_flattened_size: FlattenedLength =
+        element_types.iter().map(|typ| typ.flattened_size()).sum();
+    element_size > 1 || (element_size == 1 && element_flattened_size.0 != 1)
+}
+
 /// Divides every coefficient of `expr` by `divisor`, yielding an expression whose value is
 /// `expr / divisor` rounded down, or `None` unless the division is exact.
 ///
@@ -1739,9 +1757,47 @@ pub(super) fn array_has_constant_element_size(array_typ: &Type) -> Option<u32> {
 
 #[cfg(test)]
 mod tests {
+    use std::sync::Arc;
+
     use acvm::{FieldElement, acir::AcirField, acir::native_types::Witness};
 
-    use super::{Expression, divide_expression};
+    use super::{Expression, SemanticLength, Type, divide_expression, index_needs_logical_payload};
+
+    /// `[Field; len]`
+    fn field_array(len: u32) -> Type {
+        Type::Array(Arc::new(vec![Type::field()]), SemanticLength(len))
+    }
+
+    #[test]
+    fn single_field_of_a_single_cell_needs_no_payload() {
+        // The index is neither multiplied by a field count nor by a cell width, so the memory
+        // op's check already reports the program's index and length.
+        assert!(!index_needs_logical_payload(&[Type::field()]));
+    }
+
+    #[test]
+    fn no_fields_needs_no_payload() {
+        assert!(!index_needs_logical_payload(&[]));
+    }
+
+    #[test]
+    fn several_fields_need_a_payload() {
+        assert!(index_needs_logical_payload(&[Type::field(), Type::field()]));
+    }
+
+    #[test]
+    fn single_field_of_several_cells_needs_a_payload() {
+        // `[[Field; 2]; N]`: one field per element, but the memory op scales the index by its
+        // width of two cells.
+        assert!(index_needs_logical_payload(&[field_array(2)]));
+    }
+
+    #[test]
+    fn several_fields_that_flatten_to_one_cell_need_a_payload() {
+        // `struct S { a: [Field; 0], b: Field }` occupies a single cell, but SSA generation still
+        // reaches `b` at `2 * logical + 1`, so the memory op reports twice the index it was given.
+        assert!(index_needs_logical_payload(&[field_array(0), Type::field()]));
+    }
 
     /// `2 * w1 + 4 * w2 * w3 + 7`, the shape of an index into an array of two fields per element.
     fn index_expression() -> Expression<FieldElement> {
```

### test_programs/execution_failure/dynamic_index_zero_sized_member_failure/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "dynamic_index_zero_sized_member_failure"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/dynamic_index_zero_sized_member_failure/Prover.toml
```diff
@@ -0,0 +1,2 @@
+i = "10"
+x = "5"
```

### test_programs/execution_failure/dynamic_index_zero_sized_member_failure/src/main.nr
```diff
@@ -0,0 +1,10 @@
+// The element has two fields but only one of them occupies an ACIR cell.
+struct S {
+    a: [Field; 0],
+    b: Field,
+}
+
+fn main(i: u32, x: Field) -> pub Field {
+    let arr = [S { a: [], b: x }, S { a: [], b: x + 1 }, S { a: [], b: x + 2 }, S { a: [], b: x + 3 }];
+    arr[i].b
+}
```

### test_programs/execution_failure/dynamic_index_zero_sized_member_write_failure/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "dynamic_index_zero_sized_member_write_failure"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/dynamic_index_zero_sized_member_write_failure/Prover.toml
```diff
@@ -0,0 +1,2 @@
+i = "10"
+x = "5"
```

### test_programs/execution_failure/dynamic_index_zero_sized_member_write_failure/src/main.nr
```diff
@@ -0,0 +1,11 @@
+// The element has two fields but only one of them occupies an ACIR cell.
+struct S {
+    a: [Field; 0],
+    b: Field,
+}
+
+fn main(i: u32, x: Field) -> pub Field {
+    let mut arr = [S { a: [], b: x }, S { a: [], b: x + 1 }, S { a: [], b: x + 2 }, S { a: [], b: x + 3 }];
+    arr[i].a = [];
+    arr[0].b
+}
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_zero_sized_member_failure/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds, array has size 4, but index was 10
+  ┌─ src/main.nr:9:5
+  │
+9 │     arr[i].b
+  │     ------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:9:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_zero_sized_member_failure/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+  ┌─ src/main.nr:9:5
+  │
+9 │     arr[i].b
+  │     ------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:9:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_zero_sized_member_failure/execute__tests__comptime_stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Index out of bounds: 10 is out of bounds for the array of length 4
+  ┌─ src/main.nr:9:5
+  │
+9 │     arr[i].b
+  │     ------
+  │
+
+Error interpreting main function
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_zero_sized_member_write_failure/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds, array has size 4, but index was 10
+  ┌─ src/main.nr:9:5
+  │
+9 │     arr[i].a = [];
+  │     ------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:9:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_zero_sized_member_write_failure/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+  ┌─ src/main.nr:9:5
+  │
+9 │     arr[i].a = [];
+  │     ------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:9:5
+
+Failed assertion
```
