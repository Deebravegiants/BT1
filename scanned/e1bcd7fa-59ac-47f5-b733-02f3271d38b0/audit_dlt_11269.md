# [?] fix: error on wrong Ordering trait, instead of panic. (#10895)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-12-12
Source: https://github.com/noir-lang/noir/commit/10ab9a54ad8c8640c9a08495904404a3d0822e43
Type: security-commit

## Details
fix: error on wrong Ordering trait, instead of panic. (#10895)

Co-authored-by: jfecher <jfecher11@gmail.com>
Co-authored-by: Akosh Farkash <aakoshh@gmail.com>

## Patch
### compiler/noirc_frontend/src/hir/comptime/interpreter.rs
```diff
@@ -922,7 +922,9 @@ impl<'local, 'interner> Interpreter<'local, 'interner> {
         use BinaryOpKind::*;
         match operator {
             NotEqual => evaluate_prefix_with_value(value, UnaryOp::Not, location),
-            Less | LessEqual | Greater | GreaterEqual => self.evaluate_ordering(value, operator),
+            Less | LessEqual | Greater | GreaterEqual => {
+                self.evaluate_ordering(value, operator, location)
+            }
             _ => Ok(value),
         }
     }
@@ -946,13 +948,41 @@ impl<'local, 'interner> Interpreter<'local, 'interner> {
     }
 
     /// Given the result of a `cmp` operation, convert it into the boolean result of the given operator.
-    fn evaluate_ordering(&self, ordering: Value, operator: BinaryOpKind) -> IResult<Value> {
-        let ordering = match ordering {
-            Value::Struct(fields, _) => match &*fields.into_iter().next().unwrap().1.borrow() {
-                Value::Field(ordering) => *ordering,
-                _ => unreachable!("`cmp` should always return an Ordering value"),
-            },
-            _ => unreachable!("`cmp` should always return an Ordering value"),
+    fn evaluate_ordering(
+        &self,
+        ordering: Value,
+        operator: BinaryOpKind,
+        location: Location,
+    ) -> IResult<Value> {
+        let field_ordering = match &ordering {
+            Value::Struct(fields, typ) => {
+                // Check the struct is named "Ordering"
+                let is_ordering_type = match typ.follow_bindings() {
+                    Type::DataType(def, _) => def.borrow().name.as_str() == "Ordering",
+                    _ => false,
+                };
+                if is_ordering_type {
+                    let first_field = fields.iter().next();
+                    match first_field {
+                        Some((_, value)) => match &*value.borrow() {
+                            Value::Field(ordering) => Some(*ordering),
+                            _ => None,
+                        },
+                        None => None,
+                    }
+                } else {
+                    None
+                }
+            }
+            _ => None,
+        };
+        // Error if there is no ordering field
+        let Some(ordering) = field_ordering else {
+            return Err(InterpreterError::TypeMismatch {
+                expected: "Ordering".to_string(),
+                actual: ordering.get_type().into_owned(),
+                location,
+            });
         };
 
         // Ordering::Less: 0, Ordering::Equal: 1, Ordering::Greater: 2
```

### test_programs/compile_failure/cmp_wrong_return_type/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "cmp_wrong_return_type"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.33.0"
+
+[dependencies]
```

### test_programs/compile_failure/cmp_wrong_return_type/src/main.nr
```diff
@@ -0,0 +1,17 @@
+struct Foo {}
+
+// Intentionally incorrect Ord impl that returns wrong type
+impl std::cmp::Ord for Foo {
+    fn cmp(self, _other: Self) -> std::cmp::Ordering {
+        // Returns unit instead of Ordering
+        ()
+    }
+}
+
+fn main() {
+    comptime {
+        let a = Foo {};
+        let b = Foo {};
+        let _ = a < b;
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/compile_failure/cmp_wrong_return_type/execute__tests__stderr.snap
```diff
@@ -0,0 +1,22 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: expected type Ordering, found type ()
+  ┌─ src/main.nr:5:35
+  │
+5 │     fn cmp(self, _other: Self) -> std::cmp::Ordering {
+  │                                   ------------------ expected Ordering because of return type
+6 │         // Returns unit instead of Ordering
+7 │         ()
+  │         -- () returned here
+  │
+
+error: Expected `Ordering` but a value of type `()` was given
+   ┌─ src/main.nr:15:17
+   │
+15 │         let _ = a < b;
+   │                 -----
+   │
+
+Aborting due to 2 previous errors
```
