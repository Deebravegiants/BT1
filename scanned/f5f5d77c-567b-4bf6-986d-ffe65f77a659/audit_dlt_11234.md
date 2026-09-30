# [?] fix: ensure index-out-of-bounds for empty-sized arrays (#12807)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-04
Source: https://github.com/noir-lang/noir/commit/7c08b6d46140e63312bb3f24b9ee5cb124ad1dcf
Type: security-commit

## Details
fix: ensure index-out-of-bounds for empty-sized arrays (#12807)

## Patch
### compiler/noirc_evaluator/src/acir/acir_context/generated_acir/mod.rs
```diff
@@ -674,11 +674,11 @@ impl<F: AcirField> GeneratedAcir<F> {
                 .insert(procedure_id.to_debug_id(), (*start_index, *end_index));
         }
 
+        // Ensure every Brillig function we compile has a `brillig_locations`
+        // entry, even when it emits no per-opcode locations.
+        let brillig_locations = self.brillig_locations.entry(brillig_function_index).or_default();
         for (brillig_index, call_stack) in &generated_brillig.locations {
-            self.brillig_locations
-                .entry(brillig_function_index)
-                .or_default()
-                .insert(BrilligOpcodeLocation(*brillig_index), *call_stack);
+            brillig_locations.insert(BrilligOpcodeLocation(*brillig_index), *call_stack);
         }
     }
 
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -112,6 +112,23 @@ pub(super) struct Loop {
 /// The queue of functions remaining to compile
 type FunctionQueue = Vec<(FuncId, IrFunctionId)>;
 
+/// True if `array[i]` requires an explicit SSA out-of-bounds check rather
+/// than relying on ACIR's implicit OOB check on the underlying memory op.
+///
+/// ACIR derives the implicit check from the memory op emitted for
+/// `array_get` / `array_set`. When the array's element flattens to zero
+/// ACIR cells (e.g. `[(); N]`), no memory op is laid down — for `array_get`
+/// the access can be optimized away, and for `array_set` the value to
+/// store has zero cells to write — so the implicit check is missing and an
+/// explicit one must be emitted. Brillig has no implicit check at all and
+/// always needs the explicit one. `array_type` must be a `Type::Array`.
+pub(super) fn array_index_needs_explicit_oob_check(
+    runtime: RuntimeType,
+    array_type: &Type,
+) -> bool {
+    runtime.is_brillig() || array_type.element_size().0 == 0
+}
+
 impl<'a> FunctionContext<'a> {
     /// Create a new FunctionContext to compile the first function in the shared_context's
     /// function queue.
@@ -861,16 +878,16 @@ impl<'a> FunctionContext<'a> {
             LValue::Ident => unreachable!("Cannot assign to a variable without a reference"),
             LValue::Index { old_array: mut array, index, array_lvalue, location } => {
                 let array_type = &self.builder.type_of_value(array);
+                let runtime = self.builder.current_function.runtime();
 
                 // Checks for index Out-of-bounds
                 match array_type {
                     Type::Array(_, len) => {
-                        // Out of bounds array accesses are guaranteed to fail in ACIR so this check is performed implicitly.
-                        // We then only need to inject it for brillig functions.
-                        if self.builder.current_function.runtime().is_brillig() {
+                        if array_index_needs_explicit_oob_check(runtime, array_type) {
                             let len = self
                                 .builder
                                 .numeric_constant(u128::from(len.0), NumericType::length_type());
+                            self.builder.set_location(location);
                             self.codegen_access_check(index, len);
                         }
                     }
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -550,10 +550,7 @@ impl FunctionContext<'_> {
         // Checks for index Out-of-bounds
         match array_type {
             Type::Array(_, len) => {
-                // Out of bounds array accesses are guaranteed to fail in ACIR so this check is performed implicitly,
-                // except when the inner elements have no size, because the array access can be optimized out in that case.
-                // We then only need to inject it for brillig functions or for 'unit' elements.
-                if runtime.is_brillig() || type_size_usize == 0 {
+                if context::array_index_needs_explicit_oob_check(runtime, array_type) {
                     let len = self
                         .builder
                         .numeric_constant(u128::from(len.0), NumericType::length_type());
```

### test_programs/execution_failure/oob_array_set_unit_element/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "oob_array_set_unit_element"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.31.0"
+
+[dependencies]
```

### test_programs/execution_failure/oob_array_set_unit_element/Prover.toml
```diff
@@ -0,0 +1 @@
+x = "1"
```

### test_programs/execution_failure/oob_array_set_unit_element/src/main.nr
```diff
@@ -0,0 +1,4 @@
+fn main(x: u32) {
+    let mut array: [(); 1] = [()];
+    array[x] = ();
+}
```

### tooling/nargo_cli/tests/snapshots/execution_failure/oob_array_set_unit_element/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+  ┌─ src/main.nr:3:5
+  │
+3 │     array[x] = ();
+  │     --------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:3:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/oob_array_set_unit_element/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+  ┌─ src/main.nr:3:5
+  │
+3 │     array[x] = ();
+  │     --------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:3:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/oob_array_set_unit_element/execute__tests__comptime_stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Index out of bounds: 1 is out of bounds for the array of length 1
+  ┌─ src/main.nr:3:5
+  │
+3 │     array[x] = ();
+  │     --------
+  │
+
+Error interpreting main function
```

### tooling/nargo_cli/tests/snapshots/execution_failure/unused_array_set_unknown_index_out_of_bounds/execute__tests__brillig_stderr.snap
```diff
@@ -3,13 +3,13 @@ source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
 error: Assertion failed: Index out of bounds
-  ┌─ src/main.nr:3:16
+  ┌─ src/main.nr:3:5
   │
 3 │     array[x] = 1; // Index out of bounds
-  │                -
+  │     --------
   │
   = Call stack:
     1: main
-            at src/main.nr:3:16
+            at src/main.nr:3:5
 
 Failed assertion
```
