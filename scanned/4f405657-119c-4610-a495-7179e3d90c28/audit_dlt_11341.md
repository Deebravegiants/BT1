# [?] fix: Change panic to error in interpreter (#5446)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-07-08
Source: https://github.com/noir-lang/noir/commit/d44f882be094bf492b1742370fd3896b0c371f59
Type: security-commit

## Details
fix: Change panic to error in interpreter (#5446)

# Description

## Problem\*

Working towards https://github.com/noir-lang/noir/issues/5428

## Summary\*

Changes the panic in https://github.com/noir-lang/noir/issues/5428 to an
error instead. The original error message was no longer appropriate
either since this was occurring in the interpreter rather than the
monomorphizer.

## Additional Context

This doesn't fix the issue, I just thought it'd be slightly nicer UX
going forward if we didn't panic here.

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
@@ -50,6 +50,7 @@ pub enum InterpreterError {
     NonComptimeFnCallInSameCrate { function: String, location: Location },
     NoImpl { location: Location },
     NoMatchingImplFound { error: NoMatchingImplFoundError, file: FileId },
+    ImplMethodTypeMismatch { expected: Type, actual: Type, location: Location },
 
     Unimplemented { item: String, location: Location },
 
@@ -114,6 +115,7 @@ impl InterpreterError {
             | InterpreterError::NonComptimeFnCallInSameCrate { location, .. }
             | InterpreterError::Unimplemented { location, .. }
             | InterpreterError::NoImpl { location, .. }
+            | InterpreterError::ImplMethodTypeMismatch { location, .. }
             | InterpreterError::BreakNotInLoop { location, .. }
             | InterpreterError::ContinueNotInLoop { location, .. } => *location,
             InterpreterError::FailedToParseMacro { error, file, .. } => {
@@ -344,6 +346,12 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
                 let msg = "No impl found due to prior type error".into();
                 CustomDiagnostic::simple_error(msg, String::new(), location.span)
             }
+            InterpreterError::ImplMethodTypeMismatch { expected, actual, location } => {
+                let msg = format!(
+                    "Impl method type {actual} does not unify with trait method type {expected}"
+                );
+                CustomDiagnostic::simple_error(msg, String::new(), location.span)
+            }
             InterpreterError::NoMatchingImplFound { error, .. } => error.into(),
             InterpreterError::Break => unreachable!("Uncaught InterpreterError::Break"),
             InterpreterError::Continue => unreachable!("Uncaught InterpreterError::Continue"),
```

### compiler/noirc_frontend/src/hir/comptime/interpreter.rs
```diff
@@ -74,7 +74,7 @@ impl<'a> Interpreter<'a> {
         let trait_method = self.interner.get_trait_method_id(function);
 
         perform_instantiation_bindings(&instantiation_bindings);
-        let impl_bindings = perform_impl_bindings(self.interner, trait_method, function);
+        let impl_bindings = perform_impl_bindings(self.interner, trait_method, function, location)?;
         let result = self.call_function_inner(function, arguments, location);
         undo_instantiation_bindings(impl_bindings);
         undo_instantiation_bindings(instantiation_bindings);
```

### compiler/noirc_frontend/src/monomorphization/mod.rs
```diff
@@ -72,7 +72,7 @@ struct Monomorphizer<'interner> {
 
     /// Queue of functions to monomorphize next each item in the queue is a tuple of:
     /// (old_id, new_monomorphized_id, any type bindings to apply, the trait method if old_id is from a trait impl)
-    queue: VecDeque<(node_interner::FuncId, FuncId, TypeBindings, Option<TraitMethodId>)>,
+    queue: VecDeque<(node_interner::FuncId, FuncId, TypeBindings, Option<TraitMethodId>, Location)>,
 
     /// When a function finishes being monomorphized, the monomorphized ast::Function is
     /// stored here along with its FuncId.
@@ -124,11 +124,15 @@ pub fn monomorphize_debug(
     let function_sig = monomorphizer.compile_main(main)?;
 
     while !monomorphizer.queue.is_empty() {
-        let (next_fn_id, new_id, bindings, trait_method) = monomorphizer.queue.pop_front().unwrap();
+        let (next_fn_id, new_id, bindings, trait_method, location) =
+            monomorphizer.queue.pop_front().unwrap();
         monomorphizer.locals.clear();
 
         perform_instantiation_bindings(&bindings);
-        let impl_bindings = perform_impl_bindings(monomorphizer.interner, trait_method, next_fn_id);
+        let interner = &monomorphizer.interner;
+        let impl_bindings = perform_impl_bindings(interner, trait_method, next_fn_id, location)
+            .map_err(MonomorphizationError::InterpreterError)?;
+
         monomorphizer.function(next_fn_id, new_id)?;
         undo_instantiation_bindings(impl_bindings);
         undo_instantiation_bindings(bindings);
@@ -1275,9 +1279,10 @@ impl<'interner> Monomorphizer<'interner> {
         let new_id = self.next_function_id();
         self.define_function(id, function_type.clone(), turbofish_generics, new_id);
 
+        let location = self.interner.expr_location(&expr_id);
         let bindings = self.interner.get_instantiation_bindings(expr_id);
         let bindings = self.follow_bindings(bindings);
-        self.queue.push_back((id, new_id, bindings, trait_method));
+        self.queue.push_back((id, new_id, bindings, trait_method, location));
         new_id
     }
 
@@ -1747,7 +1752,8 @@ pub fn perform_impl_bindings(
     interner: &NodeInterner,
     trait_method: Option<TraitMethodId>,
     impl_method: node_interner::FuncId,
-) -> TypeBindings {
+    location: Location,
+) -> Result<TypeBindings, InterpreterError> {
     let mut bindings = TypeBindings::new();
 
     if let Some(trait_method) = trait_method {
@@ -1767,14 +1773,18 @@ pub fn perform_impl_bindings(
         let type_bindings = generics.iter().map(replace_type_variable).collect();
         let impl_method_type = impl_method_type.force_substitute(&type_bindings);
 
-        trait_method_type.try_unify(&impl_method_type, &mut bindings).unwrap_or_else(|_| {
-            unreachable!("Impl method type {} does not unify with trait method type {} during monomorphization", impl_method_type, trait_method_type)
-        });
+        trait_method_type.try_unify(&impl_method_type, &mut bindings).map_err(|_| {
+            InterpreterError::ImplMethodTypeMismatch {
+                expected: trait_method_type.clone(),
+                actual: impl_method_type,
+                location,
+            }
+        })?;
 
         perform_instantiation_bindings(&bindings);
     }
 
-    bindings
+    Ok(bindings)
 }
 
 pub fn resolve_trait_method(
```
