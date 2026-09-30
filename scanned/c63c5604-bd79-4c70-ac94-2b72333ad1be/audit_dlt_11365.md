# [?] fix: Fix crash when using undeclared traits (#3509)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2023-11-20
Source: https://github.com/noir-lang/noir/commit/8bb095af77d3b4043855841f1ae5799d75ed94f0
Type: security-commit

## Details
fix: Fix crash when using undeclared traits (#3509)

## Patch
### compiler/noirc_frontend/src/hir/type_check/expr.rs
```diff
@@ -317,12 +317,19 @@ impl<'interner> TypeChecker<'interner> {
         match self.interner.lookup_trait_implementation(object_type, trait_id) {
             Ok(impl_kind) => self.interner.select_impl_for_ident(function_ident_id, impl_kind),
             Err(erroring_constraints) => {
-                let constraints = vecmap(erroring_constraints, |constraint| {
-                    let r#trait = self.interner.get_trait(constraint.trait_id);
-                    (constraint.typ, r#trait.name.to_string())
-                });
+                // Don't show any errors where try_get_trait returns None.
+                // This can happen if a trait is used that was never declared.
+                let constraints = erroring_constraints
+                    .into_iter()
+                    .map(|constraint| {
+                        let r#trait = self.interner.try_get_trait(constraint.trait_id)?;
+                        Some((constraint.typ, r#trait.name.to_string()))
+                    })
+                    .collect::<Option<Vec<_>>>();
 
-                self.errors.push(TypeCheckError::NoMatchingImplFound { constraints, span });
+                if let Some(constraints) = constraints {
+                    self.errors.push(TypeCheckError::NoMatchingImplFound { constraints, span });
+                }
             }
         }
     }
@@ -902,13 +909,15 @@ impl<'interner> TypeChecker<'interner> {
 
                 for constraint in func_meta.trait_constraints {
                     if *object_type == constraint.typ {
-                        let the_trait = self.interner.get_trait(constraint.trait_id);
-
-                        for (method_index, method) in the_trait.methods.iter().enumerate() {
-                            if method.name.0.contents == method_name {
-                                let trait_method =
-                                    TraitMethodId { trait_id: constraint.trait_id, method_index };
-                                return Some(HirMethodReference::TraitMethodId(trait_method));
+                        if let Some(the_trait) = self.interner.try_get_trait(constraint.trait_id) {
+                            for (method_index, method) in the_trait.methods.iter().enumerate() {
+                                if method.name.0.contents == method_name {
+                                    let trait_method = TraitMethodId {
+                                        trait_id: constraint.trait_id,
+                                        method_index,
+                                    };
+                                    return Some(HirMethodReference::TraitMethodId(trait_method));
+                                }
                             }
                         }
                     }
```

### compiler/noirc_frontend/src/hir/type_check/mod.rs
```diff
@@ -58,10 +58,12 @@ pub fn type_check_func(interner: &mut NodeInterner, func_id: FuncId) -> Vec<Type
         let trait_id = constraint.trait_id;
 
         if !type_checker.interner.add_assumed_trait_implementation(object, trait_id) {
-            let trait_name = type_checker.interner.get_trait(trait_id).name.to_string();
-            let typ = constraint.typ.clone();
-            let span = meta.name.location.span;
-            errors.push(TypeCheckError::UnneededTraitConstraint { trait_name, typ, span });
+            if let Some(the_trait) = type_checker.interner.try_get_trait(trait_id) {
+                let trait_name = the_trait.name.to_string();
+                let typ = constraint.typ.clone();
+                let span = meta.name.location.span;
+                errors.push(TypeCheckError::UnneededTraitConstraint { trait_name, typ, span });
+            }
         }
     }
 
```

### compiler/noirc_frontend/src/node_interner.rs
```diff
@@ -845,6 +845,10 @@ impl NodeInterner {
         self.traits[&id].clone()
     }
 
+    pub fn try_get_trait(&self, id: TraitId) -> Option<Trait> {
+        self.traits.get(&id).cloned()
+    }
+
     pub fn get_type_alias(&self, id: TypeAliasId) -> &TypeAliasType {
         &self.type_aliases[id.0]
     }
```
