# [?] fix: avoid nondeterminism when reporting "Type annotation needed" (#12087)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-01
Source: https://github.com/noir-lang/noir/commit/279aafbe81a0a976912fc4df6a73cc52f3c42298
Type: security-commit

## Details
fix: avoid nondeterminism when reporting "Type annotation needed" (#12087)

Co-authored-by: jfecher <jfecher11@gmail.com>

## Patch
### compiler/noirc_frontend/src/elaborator/variable.rs
```diff
@@ -24,7 +24,7 @@ use crate::node_interner::{
     DefinitionId, DefinitionInfo, DefinitionKind, ExprId, TraitImplKind, TypeAliasId,
 };
 use crate::{Kind, Type, TypeBindings, TypeVariable};
-use iter_extended::vecmap;
+use iter_extended::{btree_map, vecmap};
 use noirc_errors::Location;
 
 /// The result of [`Elaborator::resolve_variable`].
@@ -895,10 +895,16 @@ impl Elaborator<'_> {
         }
 
         if push_required_type_variables {
-            for (type_variable, _kind, typ) in bindings.values() {
+            // Record required type variables in a predictable order to avoid nondeterminism in error messages.
+            let required_type_variables =
+                btree_map(bindings.values(), |(type_variable, _, typ)| {
+                    (type_variable.id(), typ.clone())
+                });
+
+            for (type_variable_id, typ) in required_type_variables {
                 self.push_required_type_variable(
-                    type_variable.id(),
-                    typ.clone(),
+                    type_variable_id,
+                    typ,
                     BindableTypeVariableKind::Ident(ident.id),
                     ident.location,
                 );
```
