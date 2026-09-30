# [?] fix: Don't panic when using undefined variables in the interpreter (#5381)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-07-03
Source: https://github.com/noir-lang/noir/commit/94d209acb70064d5f8a5d427bade18d3cd975be0
Type: security-commit

## Details
fix: Don't panic when using undefined variables in the interpreter (#5381)

# Description

## Problem\*

Resolves https://github.com/noir-lang/noir/issues/5378

## Summary\*



## Additional Context



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
### compiler/noirc_frontend/src/hir/comptime/errors.rs
```diff
@@ -19,6 +19,7 @@ pub enum InterpreterError {
     ArgumentCountMismatch { expected: usize, actual: usize, location: Location },
     TypeMismatch { expected: Type, value: Value, location: Location },
     NonComptimeVarReferenced { name: String, location: Location },
+    VariableNotInScope { location: Location },
     IntegerOutOfRangeForType { value: FieldElement, typ: Type, location: Location },
     ErrorNodeEncountered { location: Location },
     NonFunctionCalled { value: Value, location: Location },
@@ -83,6 +84,7 @@ impl InterpreterError {
             InterpreterError::ArgumentCountMismatch { location, .. }
             | InterpreterError::TypeMismatch { location, .. }
             | InterpreterError::NonComptimeVarReferenced { location, .. }
+            | InterpreterError::VariableNotInScope { location, .. }
             | InterpreterError::IntegerOutOfRangeForType { location, .. }
             | InterpreterError::ErrorNodeEncountered { location, .. }
             | InterpreterError::NonFunctionCalled { location, .. }
@@ -152,6 +154,11 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
                 let secondary = "Non-comptime variables can't be used in comptime code".to_string();
                 CustomDiagnostic::simple_error(msg, secondary, location.span)
             }
+            InterpreterError::VariableNotInScope { location } => {
+                let msg = "Variable not in scope".to_string();
+                let secondary = "Could not find variable".to_string();
+                CustomDiagnostic::simple_error(msg, secondary, location.span)
+            }
             InterpreterError::IntegerOutOfRangeForType { value, typ, location } => {
                 let int = match value.try_into_u128() {
                     Some(int) => int.to_string(),
```

### compiler/noirc_frontend/src/hir/comptime/interpreter.rs
```diff
@@ -298,8 +298,7 @@ impl<'a> Interpreter<'a> {
                 return Ok(());
             }
         }
-        let name = self.interner.definition(id).name.clone();
-        Err(InterpreterError::NonComptimeVarReferenced { name, location })
+        Err(InterpreterError::VariableNotInScope { location })
     }
 
     pub(super) fn lookup(&self, ident: &HirIdent) -> IResult<Value> {
@@ -313,12 +312,12 @@ impl<'a> Interpreter<'a> {
             }
         }
 
-        // Justification for `NonComptimeVarReferenced`:
-        // If we have an id to lookup at all that means name resolution successfully
-        // found another variable in scope for this name. If the name is in scope
-        // but unknown by the interpreter it must be because it was not a comptime variable.
-        let name = self.interner.definition(id).name.clone();
-        Err(InterpreterError::NonComptimeVarReferenced { name, location })
+        if id == DefinitionId::dummy_id() {
+            Err(InterpreterError::VariableNotInScope { location })
+        } else {
+            let name = self.interner.definition_name(id).to_string();
+            Err(InterpreterError::NonComptimeVarReferenced { name, location })
+        }
     }
 
     /// Evaluate an expression and return the result
@@ -354,7 +353,10 @@ impl<'a> Interpreter<'a> {
     }
 
     pub(super) fn evaluate_ident(&mut self, ident: HirIdent, id: ExprId) -> IResult<Value> {
-        let definition = self.interner.definition(ident.id);
+        let definition = self.interner.try_definition(ident.id).ok_or_else(|| {
+            let location = self.interner.expr_location(&id);
+            InterpreterError::VariableNotInScope { location }
+        })?;
 
         if let ImplKind::TraitMethod(method, _, _) = ident.impl_kind {
             let method_id = resolve_trait_method(self.interner, method, id)?;
@@ -375,7 +377,12 @@ impl<'a> Interpreter<'a> {
                 if let Ok(value) = self.lookup(&ident) {
                     Ok(value)
                 } else {
-                    let let_ = self.interner.get_global_let_statement(*global_id).unwrap();
+                    let let_ =
+                        self.interner.get_global_let_statement(*global_id).ok_or_else(|| {
+                            let location = self.interner.expr_location(&id);
+                            InterpreterError::VariableNotInScope { location }
+                        })?;
+
                     if let_.comptime {
                         self.evaluate_let(let_.clone())?;
                     }
```

### test_programs/compile_failure/comptime_var_not_defined/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "comptime_var_not_defined"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.31.0"
+
+[dependencies]
```

### test_programs/compile_failure/comptime_var_not_defined/src/main.nr
```diff
@@ -0,0 +1,5 @@
+fn main() {
+    comptime {
+        foo();
+    }
+}
```
