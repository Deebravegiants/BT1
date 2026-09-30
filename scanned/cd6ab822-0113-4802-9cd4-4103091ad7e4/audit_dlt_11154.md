# [?] Patch to fix malformed test + non-determinism in trait lookup via iterating through a hashmap (#3154)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-10-27
Source: https://github.com/FuelLabs/sway/commit/f7a387467faef39ea8e96cb2515a7e7e9be89dad
Type: security-commit

## Details
Patch to fix malformed test + non-determinism in trait lookup via iterating through a hashmap (#3154)

Co-authored-by: Joshua Batty <joshpbatty@gmail.com>

## Patch
### sway-core/src/language/call_path.rs
```diff
@@ -6,7 +6,7 @@ use sway_types::{span::Span, Spanned};
 
 /// in the expression `a::b::c()`, `a` and `b` are the prefixes and `c` is the suffix.
 /// `c` can be any type `T`, but in practice `c` is either an `Ident` or a `TypeInfo`.
-#[derive(Debug, Clone, Eq, PartialEq, Hash)]
+#[derive(Debug, Clone, Eq, PartialEq, Hash, Ord, PartialOrd)]
 pub struct CallPath<T = Ident> {
     pub prefixes: Vec<Ident>,
     pub suffix: T,
```

### sway-core/src/semantic_analysis/namespace/trait_map.rs
```diff
@@ -9,7 +9,7 @@ type TraitName = CallPath;
 /// Map of function name to [TyFunctionDeclaration](ty::TyFunctionDeclaration)
 type TraitMethods = im::HashMap<String, ty::TyFunctionDeclaration>;
 /// Map of trait name and type to [TraitMethods].
-type TraitImpls = im::HashMap<(TraitName, TypeId), TraitMethods>;
+type TraitImpls = im::OrdMap<(TraitName, TypeId), TraitMethods>;
 
 /// Map holding trait implementations for types.
 ///
```

### sway-core/src/type_system/mod.rs
```diff
@@ -40,40 +40,50 @@ fn generic_enum_resolution() {
 
     let sp = Span::dummy();
 
+    let generic_type = engine.insert_type_always(TypeInfo::UnknownGeneric {
+        name: Ident::new_with_override("T", sp.clone()),
+    });
     let variant_types = vec![ty::TyEnumVariant {
         name: Ident::new_with_override("a", sp.clone()),
         tag: 0,
-        type_id: engine.insert_type(TypeInfo::UnknownGeneric {
-            name: Ident::new_with_override("T", sp.clone()),
-        }),
-        initial_type_id: engine.insert_type(TypeInfo::UnknownGeneric {
-            name: Ident::new_with_override("T", sp.clone()),
-        }),
+        type_id: generic_type,
+        initial_type_id: generic_type,
         span: sp.clone(),
         type_span: sp.clone(),
         attributes: transform::AttributesMap::default(),
     }];
-
-    let ty_1 = engine.insert_type(TypeInfo::Enum {
+    let ty_1 = engine.insert_type_always(TypeInfo::Enum {
         name: Ident::new_with_override("Result", sp.clone()),
         variant_types,
-        type_parameters: vec![],
+        type_parameters: vec![TypeParameter {
+            type_id: generic_type,
+            initial_type_id: generic_type,
+            name_ident: Ident::new_no_span("T"),
+            trait_constraints: vec![],
+            trait_constraints_span: Span::dummy(),
+        }],
     });
 
+    let boolean_type = engine.insert_type_always(TypeInfo::Boolean);
     let variant_types = vec![ty::TyEnumVariant {
         name: Ident::new_with_override("a", sp.clone()),
         tag: 0,
-        type_id: engine.insert_type(TypeInfo::Boolean),
-        initial_type_id: engine.insert_type(TypeInfo::Boolean),
+        type_id: boolean_type,
+        initial_type_id: boolean_type,
         span: sp.clone(),
         type_span: sp.clone(),
         attributes: transform::AttributesMap::default(),
     }];
-
-    let ty_2 = engine.insert_type(TypeInfo::Enum {
+    let ty_2 = engine.insert_type_always(TypeInfo::Enum {
         name: Ident::new_with_override("Result", sp.clone()),
         variant_types,
-        type_parameters: vec![],
+        type_parameters: vec![TypeParameter {
+            type_id: boolean_type,
+            initial_type_id: boolean_type,
+            name_ident: Ident::new_no_span("T"),
+            trait_constraints: vec![],
+            trait_constraints_span: Span::dummy(),
+        }],
     });
 
     // Unify them together...
@@ -102,8 +112,8 @@ fn basic_numeric_unknown() {
 
     let sp = Span::dummy();
     // numerics
-    let id = engine.insert_type(TypeInfo::Numeric);
-    let id2 = engine.insert_type(TypeInfo::UnsignedInteger(IntegerBits::Eight));
+    let id = engine.insert_type_always(TypeInfo::Numeric);
+    let id2 = engine.insert_type_always(TypeInfo::UnsignedInteger(IntegerBits::Eight));
 
     // Unify them together...
     let (_, errors) = engine.unify(id, id2, &sp, "");
@@ -121,8 +131,8 @@ fn unify_numerics() {
     let sp = Span::dummy();
 
     // numerics
-    let id = engine.insert_type(TypeInfo::Numeric);
-    let id2 = engine.insert_type(TypeInfo::UnsignedInteger(IntegerBits::Eight));
+    let id = engine.insert_type_always(TypeInfo::Numeric);
+    let id2 = engine.insert_type_always(TypeInfo::UnsignedInteger(IntegerBits::Eight));
 
     // Unify them together...
     let (_, errors) = engine.unify(id2, id, &sp, "");
@@ -140,8 +150,8 @@ fn unify_numerics_2() {
     let sp = Span::dummy();
 
     // numerics
-    let id = engine.insert_type(TypeInfo::Numeric);
-    let id2 = engine.insert_type(TypeInfo::UnsignedInteger(IntegerBits::Eight));
+    let id = engine.insert_type_always(TypeInfo::Numeric);
+    let id2 = engine.insert_type_always(TypeInfo::UnsignedInteger(IntegerBits::Eight));
 
     // Unify them together...
     let (_, errors) = engine.unify(id, id2, &sp, "");
```

### sway-core/src/type_system/type_engine.rs
```diff
@@ -44,6 +44,18 @@ impl TypeEngine {
         }
     }
 
+    /// Currently the [TypeEngine] is a lazy static object, so when we run
+    /// cargo tests, we can either choose to use a local [TypeEngine] and bypass
+    /// all of the global methods or we can use the lazy static [TypeEngine].
+    /// This method is for testing to be able to bypass the global methods for
+    /// the lazy static [TypeEngine] (contained within the call to hash in the
+    /// id_map).
+    #[cfg(test)]
+    #[allow(dead_code)]
+    pub(crate) fn insert_type_always(&self, ty: TypeInfo) -> TypeId {
+        TypeId::new(self.slab.insert(ty))
+    }
+
     /// Gets the size of the [TypeEngine].
     fn size(&self) -> usize {
         self.slab.size()
```

### sway-core/src/type_system/type_id.rs
```diff
@@ -3,7 +3,7 @@ use std::fmt;
 use sway_types::{JsonTypeApplication, JsonTypeDeclaration};
 
 /// A identifier to uniquely refer to our type terms
-#[derive(PartialEq, Eq, Hash, Clone, Copy)]
+#[derive(PartialEq, Eq, Hash, Clone, Copy, Ord, PartialOrd)]
 pub struct TypeId(usize);
 
 impl std::ops::Deref for TypeId {
```

### sway-core/src/type_system/unify.rs
```diff
@@ -146,7 +146,7 @@ pub(super) fn unify(
             // if one address is empty, coerce to the other one
             match type_engine
                 .slab
-                .replace(received, r, look_up_type_id(expected))
+                .replace(received, r, type_engine.slab.get(*expected))
             {
                 None => (vec![], vec![]),
                 Some(_) => unify(
@@ -171,7 +171,7 @@ pub(super) fn unify(
             // if one address is empty, coerce to the other one
             match type_engine
                 .slab
-                .replace(expected, e, look_up_type_id(received))
+                .replace(expected, e, type_engine.slab.get(*received))
             {
                 None => (vec![], vec![]),
                 Some(_) => unify(
@@ -361,7 +361,7 @@ pub(super) fn unify_right(
             // if one address is empty, coerce to the other one
             match type_engine
                 .slab
-                .replace(expected, e, look_up_type_id(received))
+                .replace(expected, e, type_engine.slab.get(*received))
             {
                 None => (vec![], vec![]),
                 Some(_) => unify_right(type_engine, received, expected, span, help_text),
```
