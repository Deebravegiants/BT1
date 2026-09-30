# [?] fix: Replace panic in monomorphization with an error (#5305)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-06-21
Source: https://github.com/noir-lang/noir/commit/49e1b0c0d45565f3e87469b77f2fef0c283f6ea1
Type: security-commit

## Details
fix: Replace panic in monomorphization with an error (#5305)

# Description

## Problem\*

## Summary\*

Replaces an `unwrap` and panic in the monomorphizer with an ICE issued
to the user instead. This isn't expected to be issued normally, but is
being issued currently when a `comptime let` variable is used in runtime
code since `comptime let` is still unimplemented in the evaluator.

## Additional Context

This does not fix the underlying `comptime let` error, only the
resulting panic.

## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_frontend/src/monomorphization/errors.rs
```diff
@@ -6,13 +6,15 @@ use crate::hir::comptime::InterpreterError;
 pub enum MonomorphizationError {
     UnknownArrayLength { location: Location },
     TypeAnnotationsNeeded { location: Location },
+    InternalError { message: &'static str, location: Location },
     InterpreterError(InterpreterError),
 }
 
 impl MonomorphizationError {
     fn location(&self) -> Location {
         match self {
             MonomorphizationError::UnknownArrayLength { location }
+            | MonomorphizationError::InternalError { location, .. }
             | MonomorphizationError::TypeAnnotationsNeeded { location } => *location,
             MonomorphizationError::InterpreterError(error) => error.get_location(),
         }
@@ -36,6 +38,7 @@ impl MonomorphizationError {
             }
             MonomorphizationError::TypeAnnotationsNeeded { .. } => "Type annotations needed",
             MonomorphizationError::InterpreterError(error) => return (&error).into(),
+            MonomorphizationError::InternalError { message, .. } => message,
         };
 
         let location = self.location();
```

### compiler/noirc_frontend/src/monomorphization/mod.rs
```diff
@@ -889,7 +889,11 @@ impl<'interner> Monomorphizer<'interner> {
             DefinitionKind::Local(_) => match self.lookup_captured_expr(ident.id) {
                 Some(expr) => expr,
                 None => {
-                    let ident = self.local_ident(&ident)?.unwrap();
+                    let Some(ident) = self.local_ident(&ident)? else {
+                        let location = self.interner.id_location(expr_id);
+                        let message = "ICE: Variable not found during monomorphization";
+                        return Err(MonomorphizationError::InternalError { location, message });
+                    };
                     ast::Expression::Ident(ident)
                 }
             },
```
