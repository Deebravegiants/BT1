# [?] fix: correct error message on comptime overflow (#8238)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-04-29
Source: https://github.com/noir-lang/noir/commit/68e83809f2f87adfa8c6fb30e29f4ac66509ca67
Type: security-commit

## Details
fix: correct error message on comptime overflow (#8238)

## Patch
### compiler/noirc_frontend/src/hir/comptime/errors.rs
```diff
@@ -126,6 +126,10 @@ pub enum InterpreterError {
         operator: &'static str,
         location: Location,
     },
+    MathError {
+        operator: &'static str,
+        location: Location,
+    },
     CastToNonNumericType {
         typ: Type,
         location: Location,
@@ -300,6 +304,7 @@ impl InterpreterError {
             | InterpreterError::TypeUnsupported { location, .. }
             | InterpreterError::InvalidValueForUnary { location, .. }
             | InterpreterError::InvalidValuesForBinary { location, .. }
+            | InterpreterError::MathError { location, .. }
             | InterpreterError::CastToNonNumericType { location, .. }
             | InterpreterError::QuoteInRuntimeCode { location, .. }
             | InterpreterError::NonStructInConstructor { location, .. }
@@ -493,7 +498,23 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
                 CustomDiagnostic::simple_error(msg, String::new(), *location)
             }
             InterpreterError::InvalidValuesForBinary { lhs, rhs, operator, location } => {
-                let msg = format!("No implementation for `{lhs}` {operator} `{rhs}`",);
+                let msg = format!("No implementation for `{lhs}` {operator} `{rhs}`");
+                CustomDiagnostic::simple_error(msg, String::new(), *location)
+            }
+            InterpreterError::MathError { operator, location } => {
+                let msg = if *operator == "/" {
+                    "Attempt to divide by zero".to_string()
+                } else {
+                    let operator = match *operator {
+                        "+" => "add",
+                        "-" => "subtract",
+                        "*" => "multiply",
+                        ">>" => "shift right",
+                        "<<" => "shift left",
+                        _ => operator,
+                    };
+                    format!("Attempt to {operator} with overflow")
+                };
                 CustomDiagnostic::simple_error(msg, String::new(), *location)
             }
             InterpreterError::CastToNonNumericType { typ, location } => {
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -19,6 +19,8 @@ pub(super) fn evaluate_infix(
         InterpreterError::InvalidValuesForBinary { lhs, rhs, location, operator }
     };
 
+    let math_error = |operator| InterpreterError::MathError { location, operator };
+
     /// Generate matches that can promote the type of one side to the other if they are compatible.
     macro_rules! match_values {
         (($lhs_value:ident as $lhs:ident $op:literal $rhs_value:ident as $rhs:ident) {
@@ -31,7 +33,7 @@ pub(super) fn evaluate_infix(
             match ($lhs_value, $rhs_value) {
                 $(
                 (Value::$lhs_var($lhs), Value::$rhs_var($rhs)) => {
-                    Ok(Value::$res_var(($expr).ok_or(error($op))?))
+                    Ok(Value::$res_var(($expr).ok_or(math_error($op))?))
                 },
                 )*
                 (_, _) => {
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -4643,3 +4643,33 @@ fn resolves_generic_type_argument_via_self() {
     ";
     check_monomorphization_error!(src);
 }
+
+#[named]
+#[test]
+fn attempt_to_add_with_overflow_at_comptime() {
+    let src = r#"
+        fn main() -> pub u8 {
+            comptime {
+                255 as u8 + 1 as u8
+                ^^^^^^^^^^^^^^^^^^^ Attempt to add with overflow
+            }
+        }
+
+        "#;
+    check_errors!(src);
+}
+
+#[named]
+#[test]
+fn attempt_to_divide_by_zero_at_comptime() {
+    let src = r#"
+        fn main() -> pub u8 {
+            comptime {
+                255 as u8 / 0
+                ^^^^^^^^^^^^^ Attempt to divide by zero
+            }
+        }
+
+        "#;
+    check_errors!(src);
+}
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_add_with_overflow_at_comptime/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+
+            [package]
+            name = "noirc_frontend_tests_attempt_to_add_with_overflow_at_comptime"
+            type = "bin"
+            authors = [""]
+            
+            [dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_add_with_overflow_at_comptime/src/main.nr
```diff
@@ -0,0 +1,8 @@
+
+        fn main() -> pub u8 {
+            comptime {
+                255 as u8 + 1 as u8
+            }
+        }
+
+        
\ No newline at end of file
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_add_with_overflow_at_comptime/src_hash.txt
```diff
@@ -0,0 +1 @@
+13522078675290589745
\ No newline at end of file
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_add_with_overflow_at_comptime/stderr.txt
```diff
@@ -0,0 +1,8 @@
+error: Attempt to add with overflow
+  ┌─ src/main.nr:4:17
+  │
+4 │                 255 as u8 + 1 as u8
+  │                 -------------------
+  │
+
+Aborting due to 1 previous error
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_divide_by_zero_at_comptime/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+
+            [package]
+            name = "noirc_frontend_tests_attempt_to_divide_by_zero_at_comptime"
+            type = "bin"
+            authors = [""]
+            
+            [dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_divide_by_zero_at_comptime/src/main.nr
```diff
@@ -0,0 +1,8 @@
+
+        fn main() -> pub u8 {
+            comptime {
+                255 as u8 / 0
+            }
+        }
+
+        
\ No newline at end of file
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_divide_by_zero_at_comptime/src_hash.txt
```diff
@@ -0,0 +1 @@
+13409194042539933503
\ No newline at end of file
```

### test_programs/compile_failure/noirc_frontend_tests_attempt_to_divide_by_zero_at_comptime/stderr.txt
```diff
@@ -0,0 +1,8 @@
+error: Attempt to divide by zero
+  ┌─ src/main.nr:4:17
+  │
+4 │                 255 as u8 / 0
+  │                 -------------
+  │
+
+Aborting due to 1 previous error
```
