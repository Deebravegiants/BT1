# [?] fix: Avoid panic in type system (#5332)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-06-25
Source: https://github.com/noir-lang/noir/commit/52d48ff1cf1415fa87fbaf76249b2e0d042de8bd
Type: security-commit

## Details
fix: Avoid panic in type system (#5332)

# Description

## Problem\*

Resolves a panic in the type system found in the slices test here
https://github.com/noir-lang/noir/pull/5331

## Summary\*

We weren't recurring in `substitute` before, so if we had multiple
bindings: `1 -> 2` and `2 -> 3` then we may not catch the case were
adding `3 -> 1` as well would cause a recursive binding. This simple
case was caught previously, but mixing in more bound type variable links
would fail this.

## Additional Context

Repro is the slices test in https://github.com/noir-lang/noir/pull/5331

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
### compiler/noirc_frontend/src/hir_def/types.rs
```diff
@@ -547,7 +547,7 @@ impl TypeVariable {
             TypeBinding::Unbound(id) => *id,
         };
 
-        assert!(!typ.occurs(id));
+        assert!(!typ.occurs(id), "{self:?} occurs within {typ:?}");
         *self.1.borrow_mut() = TypeBinding::Bound(typ);
     }
 
@@ -1343,8 +1343,7 @@ impl Type {
             TypeBinding::Unbound(id) => *id,
         };
 
-        let this = self.substitute(bindings);
-
+        let this = self.substitute(bindings).follow_bindings();
         if let Some(binding) = this.get_inner_type_variable() {
             match &*binding.borrow() {
                 TypeBinding::Bound(typ) => return typ.try_bind_to(var, bindings),
@@ -1743,6 +1742,15 @@ impl Type {
         }
     }
 
+    fn type_variable_id(&self) -> Option<TypeVariableId> {
+        match self {
+            Type::TypeVariable(variable, _) | Type::NamedGeneric(variable, _, _) => {
+                Some(variable.0)
+            }
+            _ => None,
+        }
+    }
+
     /// Substitute any type variables found within this type with the
     /// given bindings if found. If a type variable is not found within
     /// the given TypeBindings, it is unchanged.
@@ -1777,18 +1785,29 @@ impl Type {
             return self.clone();
         }
 
+        let recur_on_binding = |id, replacement: &Type| {
+            // Prevent recuring forever if there's a `T := T` binding
+            if replacement.type_variable_id() == Some(id) {
+                replacement.clone()
+            } else {
+                replacement.substitute_helper(type_bindings, substitute_bound_typevars)
+            }
+        };
+
         let substitute_binding = |binding: &TypeVariable| {
             // Check the id first to allow substituting to
             // type variables that have already been bound over.
             // This is needed for monomorphizing trait impl methods.
             match type_bindings.get(&binding.0) {
-                Some((_, binding)) if substitute_bound_typevars => binding.clone(),
+                Some((_, replacement)) if substitute_bound_typevars => {
+                    recur_on_binding(binding.0, replacement)
+                }
                 _ => match &*binding.borrow() {
                     TypeBinding::Bound(binding) => {
                         binding.substitute_helper(type_bindings, substitute_bound_typevars)
                     }
                     TypeBinding::Unbound(id) => match type_bindings.get(id) {
-                        Some((_, binding)) => binding.clone(),
+                        Some((_, replacement)) => recur_on_binding(binding.0, replacement),
                         None => self.clone(),
                     },
                 },
```
