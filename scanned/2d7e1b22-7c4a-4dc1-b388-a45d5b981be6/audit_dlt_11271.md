# [?] fix: oob check for arrays with 0-size elements (#10738)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-12-08
Source: https://github.com/noir-lang/noir/commit/16cad49bed299e97f664251e6086f3c6a61c0ba2
Type: security-commit

## Details
fix: oob check for arrays with 0-size elements (#10738)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -495,19 +495,20 @@ impl FunctionContext<'_> {
     ) -> Result<Values, RuntimeError> {
         // base_index = index * type_size
         let index = self.make_array_index(index);
-        let type_size = Self::convert_type(element_type).size_of_type();
+        let type_size_usize = Self::convert_type(element_type).size_of_type();
         let type_size =
-            self.builder.numeric_constant(type_size as u128, NumericType::length_type());
+            self.builder.numeric_constant(type_size_usize as u128, NumericType::length_type());
 
         let array_type = &self.builder.type_of_value(array);
         let runtime = self.builder.current_function.runtime();
 
         // Checks for index Out-of-bounds
         match array_type {
             Type::Array(_, len) => {
-                // Out of bounds array accesses are guaranteed to fail in ACIR so this check is performed implicitly.
-                // We then only need to inject it for brillig functions.
-                if runtime.is_brillig() {
+                // Out of bounds array accesses are guaranteed to fail in ACIR so this check is performed implicitly,
+                // except when the inner elements have no size, because the array access can be optimized out in that case.
+                // We then only need to inject it for brillig functions or for 'unit' elements.
+                if runtime.is_brillig() || type_size_usize == 0 {
                     let len =
                         self.builder.numeric_constant(u128::from(*len), NumericType::length_type());
                     self.codegen_access_check(index, len);
```

### test_programs/execution_failure/regression_10967/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_10967"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_failure/regression_10967/src/main.nr
```diff
@@ -0,0 +1,4 @@
+fn main() {
+    let mut unit_array: [(); 1] = [()];
+    unit_array[3];
+}
\ No newline at end of file
```
