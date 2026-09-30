# [?] fix: builtin with body now errors instead of crashing (#10474)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-11
Source: https://github.com/noir-lang/noir/commit/e794b78f57948a0555fdf43b78bc12b90982dc0e
Type: security-commit

## Details
fix: builtin with body now errors instead of crashing (#10474)

## Patch
### compiler/noirc_frontend/src/elaborator/function.rs
```diff
@@ -496,9 +496,9 @@ impl Elaborator<'_> {
             | FunctionKind::LowLevel
             | FunctionKind::TraitFunctionWithoutBody => {
                 if !body.statements.is_empty() {
-                    panic!(
-                        "Builtin, low-level, and trait function declarations cannot have a body"
-                    );
+                    self.push_err(ResolverError::BuiltinWithBody {
+                        location: func_meta.name.location,
+                    });
                 }
                 (HirFunction::empty(), Type::Error)
             }
```

### compiler/noirc_frontend/src/hir/resolution/errors.rs
```diff
@@ -194,6 +194,8 @@ pub enum ResolverError {
     ReferencesNotAllowedInGlobals { location: Location },
     #[error("Functions marked with #[oracle] must have no body")]
     OracleWithBody { location: Location },
+    #[error("Builtin and low-level function declarations cannot have a body")]
+    BuiltinWithBody { location: Location },
 }
 
 impl ResolverError {
@@ -261,7 +263,8 @@ impl ResolverError {
             | ResolverError::AmbiguousAssociatedType { location, .. }
             | ResolverError::WildcardTypeDisallowed { location }
             | ResolverError::ReferencesNotAllowedInGlobals { location }
-            | ResolverError::OracleWithBody { location } => *location,
+            | ResolverError::OracleWithBody { location }
+            | ResolverError::BuiltinWithBody { location } => *location,
             ResolverError::UnusedVariable { ident }
             | ResolverError::UnusedItem { ident, .. }
             | ResolverError::DuplicateField { field: ident }
@@ -827,7 +830,14 @@ impl<'a> From<&'a ResolverError> for Diagnostic {
                     "This function body will never be run so should be removed".to_string(),
                     *location,
                 )
+            }
+            ResolverError::BuiltinWithBody { location } => {
+                Diagnostic::simple_error(
+                    "Builtin and low-level function declarations cannot have a body".to_string(),
+                    "This function body should be removed".to_string(),
+                    *location,
+                )
+            }
         }
     }
-    }
 }
```

### compiler/noirc_frontend/src/tests/functions.rs
```diff
@@ -198,3 +198,18 @@ fn cannot_return_slice_from_main() {
         "#;
     check_errors(src);
 }
+
+#[test]
+fn builtin_function_with_body() {
+    let src = r#"
+    #[builtin(foo)]
+    ^^^^^^^^^^^^^^^ Definition of low-level function outside of standard library
+    ~~~~~~~~~~~~~~~ Usage of the `#[foreign]` or `#[builtin]` function attributes are not allowed outside of the Noir standard library
+    pub fn foo() {
+           ^^^ Builtin and low-level function declarations cannot have a body
+           ~~~ This function body should be removed
+        let x = 1;
+    }
+    "#;
+    check_errors(src);
+}
```
