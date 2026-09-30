# [?] fix: correct index out of bounds location (#11685)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-02-25
Source: https://github.com/noir-lang/noir/commit/fffdad07c7a6ba5e2555285d907b4f3dbf2ab842
Type: security-commit

## Details
fix: correct index out of bounds location (#11685)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -522,6 +522,8 @@ impl FunctionContext<'_> {
         location: Location,
         length: Option<ValueId>,
     ) -> Result<Values, RuntimeError> {
+        self.builder.set_location(location);
+
         // base_index = index * type_size
         let index = self.make_array_index(index);
         let type_size_usize = Self::convert_type(element_type).size_of_type();
@@ -564,11 +566,7 @@ impl FunctionContext<'_> {
         // so it's okay to use unchecked operations. The SSA interpreter has been updated to have similar semantics.
         let unchecked = true;
 
-        let base_index = self.builder.set_location(location).insert_binary(
-            index,
-            BinaryOp::Mul { unchecked },
-            type_size,
-        );
+        let base_index = self.builder.insert_binary(index, BinaryOp::Mul { unchecked }, type_size);
 
         let mut field_index = 0u128;
         Ok(Self::map_type(element_type, |typ| {
```

### test_programs/execution_failure/regression_10238/src/main.nr
```diff
@@ -1,4 +1,4 @@
-fn main(b: i64, mut c: bool) -> pub Field {
+fn main(b: i64) -> pub Field {
     if ((6863985126385003285_i64 - b) != 0) {
         10
     } else {
```

### tooling/nargo_cli/tests/snapshots/compile_success_with_bug/regression_9872/execute__tests__stderr.snap
```diff
@@ -3,10 +3,10 @@ source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
 bug: Assertion is always false: Index out of bounds
-  ┌─ src/main.nr:3:8
+  ┌─ src/main.nr:3:6
   │
 3 │     *b[2]
-  │        - As a result, the compiled circuit is ensured to fail. Other assertions may also fail during execution
+  │      ---- As a result, the compiled circuit is ensured to fail. Other assertions may also fail during execution
   │
   = Call stack:
-    1. src/main.nr:3:8
+    1. src/main.nr:3:6
```
