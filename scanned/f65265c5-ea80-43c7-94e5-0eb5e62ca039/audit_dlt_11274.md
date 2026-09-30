# [?] fix: Error when slice_insert is OOB during comptime (#10645)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-26
Source: https://github.com/noir-lang/noir/commit/b47e62a186971a47540ff9e961da12332a5f5ec2
Type: security-commit

## Details
fix: Error when slice_insert is OOB during comptime (#10645)

## Patch
### compiler/noirc_frontend/src/hir/comptime/interpreter/builtin.rs
```diff
@@ -181,7 +181,7 @@ impl Interpreter<'_, '_> {
             "quoted_eq" => quoted_eq(self.elaborator.interner, arguments, location),
             "quoted_hash" => quoted_hash(arguments, location),
             "quoted_tokens" => quoted_tokens(arguments, location),
-            "slice_insert" => slice_insert(arguments, location),
+            "slice_insert" => slice_insert(arguments, location, call_stack),
             "slice_pop_back" => slice_pop_back(arguments, location, call_stack),
             "slice_pop_front" => slice_pop_front(arguments, location, call_stack),
             "slice_push_back" => slice_push_back(arguments, location),
@@ -799,11 +799,25 @@ fn slice_pop_back(
     }
 }
 
-fn slice_insert(arguments: Vec<(Value, Location)>, location: Location) -> IResult<Value> {
+fn slice_insert(
+    arguments: Vec<(Value, Location)>,
+    location: Location,
+    call_stack: &Vector<Location>,
+) -> IResult<Value> {
     let (slice, index, (element, _)) = check_three_arguments(arguments, location)?;
 
     let (mut values, typ) = get_slice(slice)?;
     let index = get_u32(index)? as usize;
+
+    // If index is equal to the length, the insert is equivalent to a push
+    if index > values.len() {
+        let message = format!(
+            "slice_insert: index {index} is out of bounds for a slice of length {}",
+            values.len()
+        );
+        return failing_constraint(message, location, call_stack);
+    }
+
     values.insert(index, element);
     Ok(Value::Slice(values, typ))
 }
```

### tooling/nargo_cli/build.rs
```diff
@@ -171,9 +171,7 @@ const IGNORED_COMPTIME_INTERPRET_EXECUTION_TESTS: [&str; 29] = [
     "regression_7323",
 ];
 
-const IGNORED_COMPTIME_INTERPRET_EXECUTION_FAILURE_TESTS: [&str; 3] = [
-    // TODO(https://github.com/noir-lang/noir/issues/10623): Panic on OOB insertion
-    "slice_insert_failure",
+const IGNORED_COMPTIME_INTERPRET_EXECUTION_FAILURE_TESTS: [&str; 2] = [
     // TODO(https://github.com/noir-lang/noir/issues/10625): Bits and byte decomposition does not validate output size in comptime
     "invalid_comptime_bits_decomposition",
     "invalid_comptime_bytes_decomposition",
```
