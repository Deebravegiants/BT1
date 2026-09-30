# [?] fix: Fix stack overflow on some Type methods (#11203)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-14
Source: https://github.com/noir-lang/noir/commit/8af6f7b777b104599f7a3a8e7a840d1f5cffcac5
Type: security-commit

## Details
fix: Fix stack overflow on some Type methods (#11203)

## Patch
### compiler/noirc_frontend/src/hir_def/types.rs
```diff
@@ -34,6 +34,10 @@ pub(crate) mod validity;
 
 pub use unification::UnificationError;
 
+/// Arbitrary recursion limit when following type variables or recurring on types some other way.
+/// Types form trees but are not likely to be more deep than just a few levels in real code.
+pub const TYPE_RECURSION_LIMIT: u32 = 100;
+
 #[derive(Eq, Clone, Ord, PartialOrd)]
 pub enum Type {
     /// A primitive Field type
@@ -2461,87 +2465,103 @@ impl Type {
     ///
     /// Expected to be called on an instantiated type (with no Type::Foralls)
     pub fn follow_bindings(&self) -> Type {
-        use Type::*;
-        match self {
-            Array(size, elem) => {
-                Array(Box::new(size.follow_bindings()), Box::new(elem.follow_bindings()))
-            }
-            Vector(elem) => Vector(Box::new(elem.follow_bindings())),
-            String(size) => String(Box::new(size.follow_bindings())),
-            FmtString(size, args) => {
-                let size = Box::new(size.follow_bindings());
-                let args = Box::new(args.follow_bindings());
-                FmtString(size, args)
-            }
-            DataType(def, args) => {
-                let args = vecmap(args, |arg| arg.follow_bindings());
-                DataType(def.clone(), args)
-            }
-            Alias(def, args) => {
-                // We don't need to vecmap(args, follow_bindings) since we're recursively
-                // calling follow_bindings here already.
-                def.borrow().get_type(args).follow_bindings()
-            }
-            Tuple(args) => Tuple(vecmap(args, |arg| arg.follow_bindings())),
-            CheckedCast { from, to } => {
-                let from = Box::new(from.follow_bindings());
-                let to = Box::new(to.follow_bindings());
-                CheckedCast { from, to }
-            }
-            TypeVariable(var) | NamedGeneric(types::NamedGeneric { type_var: var, .. }) => {
-                if let TypeBinding::Bound(typ) = &*var.borrow() {
-                    return typ.follow_bindings();
-                }
-                self.clone()
-            }
-            Function(args, ret, env, unconstrained) => {
-                let args = vecmap(args, |arg| arg.follow_bindings());
-                let ret = Box::new(ret.follow_bindings());
-                let env = Box::new(env.follow_bindings());
-                Function(args, ret, env, *unconstrained)
-            }
-
-            Reference(element, mutable) => Reference(Box::new(element.follow_bindings()), *mutable),
-
-            TraitAsType(s, name, args) => {
-                let ordered = vecmap(&args.ordered, |arg| arg.follow_bindings());
-                let named = vecmap(&args.named, |arg| NamedType {
-                    name: arg.name.clone(),
-                    typ: arg.typ.follow_bindings(),
-                });
-                TraitAsType(*s, name.clone(), TraitGenerics { ordered, named })
-            }
-            InfixExpr(lhs, op, rhs, inversion) => {
-                let lhs = lhs.follow_bindings();
-                let rhs = rhs.follow_bindings();
-                InfixExpr(Box::new(lhs), *op, Box::new(rhs), *inversion)
-            }
+        fn helper(this: &Type, i: u32) -> Type {
+            if i >= TYPE_RECURSION_LIMIT {
+                panic!("Type recursion limit reached - types are too large")
+            }
+            let recur = |typ| helper(typ, i);
+
+            use Type::*;
+            match this {
+                Array(size, elem) => Array(Box::new(recur(size)), Box::new(recur(elem))),
+                Vector(elem) => Vector(Box::new(recur(elem))),
+                String(size) => String(Box::new(recur(size))),
+                FmtString(size, args) => {
+                    let size = Box::new(recur(size));
+                    let args = Box::new(recur(args));
+                    FmtString(size, args)
+                }
+                DataType(def, args) => {
+                    let args = vecmap(args, recur);
+                    DataType(def.clone(), args)
+                }
+                Alias(def, args) => {
+                    // We don't need to vecmap(args, recur) since we're recursively
+                    // calling recur here already.
+                    recur(&def.borrow().get_type(args))
+                }
+                Tuple(args) => Tuple(vecmap(args, recur)),
+                CheckedCast { from, to } => {
+                    let from = Box::new(recur(from));
+                    let to = Box::new(recur(to));
+                    CheckedCast { from, to }
+                }
+                TypeVariable(var) | NamedGeneric(types::NamedGeneric { type_var: var, .. }) => {
+                    if let TypeBinding::Bound(typ) = &*var.borrow() {
+                        return recur(typ);
+                    }
+                    this.clone()
+                }
+                Function(args, ret, env, unconstrained) => {
+                    let args = vecmap(args, recur);
+                    let ret = Box::new(recur(ret));
+                    let env = Box::new(recur(env));
+                    Function(args, ret, env, *unconstrained)
+                }
 
-            // Expect that this function should only be called on instantiated types
-            Forall(..) => unreachable!(),
-            FieldElement | Integer(_, _) | Bool | Constant(_, _) | Unit | Quoted(_) | Error => {
-                self.clone()
+                Reference(element, mutable) => Reference(Box::new(recur(element)), *mutable),
+
+                TraitAsType(s, name, args) => {
+                    let ordered = vecmap(&args.ordered, recur);
+                    let named = vecmap(&args.named, |arg| NamedType {
+                        name: arg.name.clone(),
+                        typ: recur(&arg.typ),
+                    });
+                    TraitAsType(*s, name.clone(), TraitGenerics { ordered, named })
+                }
+                InfixExpr(lhs, op, rhs, inversion) => {
+                    let lhs = recur(lhs);
+                    let rhs = recur(rhs);
+                    InfixExpr(Box::new(lhs), *op, Box::new(rhs), *inversion)
+                }
+
+                // Expect that this function should only be called on instantiated types
+                Forall(..) => unreachable!(),
+                FieldElement | Integer(_, _) | Bool | Constant(_, _) | Unit | Quoted(_) | Error => {
+                    this.clone()
+                }
             }
         }
+        helper(self, 0)
     }
 
     /// Follow bindings if this is a type variable or generic to the first non-type-variable
     /// type. Unlike `follow_bindings`, this won't recursively follow any bindings on any
     /// fields or arguments of this type.
     pub fn follow_bindings_shallow(&self) -> Cow<Type> {
-        match self {
-            Type::TypeVariable(var) | Type::NamedGeneric(NamedGeneric { type_var: var, .. }) => {
-                if let TypeBinding::Bound(typ) = &*var.borrow() {
-                    return Cow::Owned(typ.follow_bindings_shallow().into_owned());
+        let mut this = Cow::Borrowed(self);
+        for _ in 0..TYPE_RECURSION_LIMIT {
+            match this.as_ref() {
+                Type::TypeVariable(var)
+                | Type::NamedGeneric(NamedGeneric { type_var: var, .. }) => {
+                    let binding = var.borrow();
+                    if let TypeBinding::Bound(typ) = &*binding {
+                        let typ = typ.clone();
+                        drop(binding);
+                        this = Cow::Owned(typ);
+                    } else {
+                        drop(binding);
+                        return this;
+                    };
                 }
-                Cow::Borrowed(self)
-            }
-            Type::Alias(alias_def, generics) => {
-                let typ = alias_def.borrow().get_type(generics);
-                Cow::Owned(typ.follow_bindings_shallow().into_owned())
-            }
-            other => Cow::Borrowed(other),
+                Type::Alias(alias_def, generics) => {
+                    let typ = alias_def.borrow().get_type(generics);
+                    this = Cow::Owned(typ);
+                }
+                _ => return this,
+            };
         }
+        panic!("Type recursion limit reached - types are too large")
     }
 
     pub fn from_generics(generics: &GenericTypeVars) -> Vec<Type> {
```

### compiler/noirc_frontend/src/hir_def/types/validity.rs
```diff
@@ -1,6 +1,6 @@
 use noirc_errors::Location;
 
-use crate::{NamedGeneric, Type, TypeBinding, ast::Ident};
+use crate::{NamedGeneric, TYPE_RECURSION_LIMIT, Type, TypeBinding, ast::Ident};
 
 /// An type incorrectly used as a program input.
 #[derive(Debug, Clone, PartialEq, Eq)]
@@ -25,94 +25,99 @@ impl Type {
     ///
     /// Returns `None` if this type and its nested types are all valid program inputs.
     pub(crate) fn program_input_validity(&self, allow_empty_arrays: bool) -> Option<InvalidType> {
-        match self {
-            // Type::Error is allowed as usual since it indicates an error was already issued and
-            // we don't need to issue further errors about this likely unresolved type
-            // TypeVariable and Generic are allowed here too as they can only result from
-            // generics being declared on the function itself, but we produce a different error in that case.
-            Type::FieldElement
-            | Type::Integer(_, _)
-            | Type::Bool
-            | Type::Constant(_, _)
-            | Type::TypeVariable(_)
-            | Type::NamedGeneric(_)
-            | Type::Error => None,
+        fn helper(this: &Type, allow_empty_arrays: bool, mut i: u32) -> Option<InvalidType> {
+            if i == TYPE_RECURSION_LIMIT {
+                return None;
+            }
+            i += 1;
+            let recur = |typ| helper(typ, allow_empty_arrays, i);
 
-            Type::Unit
-            | Type::FmtString(_, _)
-            | Type::Function(_, _, _, _)
-            | Type::Reference(..)
-            | Type::Forall(_, _)
-            | Type::Quoted(_)
-            | Type::Vector(_)
-            | Type::TraitAsType(..) => Some(InvalidType::Primitive(self.clone())),
+            match this {
+                // Type::Error is allowed as usual since it indicates an error was already issued and
+                // we don't need to issue further errors about this likely unresolved type
+                // TypeVariable and Generic are allowed here too as they can only result from
+                // generics being declared on the function itself, but we produce a different error in that case.
+                Type::FieldElement
+                | Type::Integer(_, _)
+                | Type::Bool
+                | Type::Constant(_, _)
+                | Type::TypeVariable(_)
+                | Type::NamedGeneric(_)
+                | Type::Error => None,
 
-            Type::CheckedCast { to, .. } => to.program_input_validity(allow_empty_arrays),
+                Type::Unit
+                | Type::FmtString(_, _)
+                | Type::Function(_, _, _, _)
+                | Type::Reference(..)
+                | Type::Forall(_, _)
+                | Type::Quoted(_)
+                | Type::Vector(_)
+                | Type::TraitAsType(..) => Some(InvalidType::Primitive(this.clone())),
 
-            Type::Alias(alias, generics) => {
-                let alias = alias.borrow();
-                if let Some(invalid_type) =
-                    alias.get_type(generics).program_input_validity(allow_empty_arrays)
-                {
-                    let alias_name = alias.name.clone();
-                    Some(InvalidType::Alias { alias_name, invalid_type: Box::new(invalid_type) })
-                } else {
-                    None
+                Type::CheckedCast { to, .. } => recur(to),
+
+                Type::Alias(alias, generics) => {
+                    let alias = alias.borrow();
+                    if let Some(invalid_type) = recur(&alias.get_type(generics)) {
+                        let alias_name = alias.name.clone();
+                        Some(InvalidType::Alias {
+                            alias_name,
+                            invalid_type: Box::new(invalid_type),
+                        })
+                    } else {
+                        None
+                    }
                 }
-            }
 
-            Type::Array(length, element) => {
-                if !length_is_valid_for_entry_point(length, allow_empty_arrays) {
-                    Some(InvalidType::Primitive(self.clone()))
-                } else {
-                    length
-                        .program_input_validity(allow_empty_arrays)
-                        .or_else(|| element.program_input_validity(allow_empty_arrays))
+                Type::Array(length, element) => {
+                    if !length_is_valid_for_entry_point(length, allow_empty_arrays) {
+                        Some(InvalidType::Primitive(this.clone()))
+                    } else {
+                        recur(length).or_else(|| recur(element))
+                    }
                 }
-            }
-            Type::String(length) => {
-                if !length_is_valid_for_entry_point(length, allow_empty_arrays) {
-                    Some(InvalidType::EmptyString(self.clone()))
-                } else {
-                    length.program_input_validity(allow_empty_arrays)
+                Type::String(length) => {
+                    if !length_is_valid_for_entry_point(length, allow_empty_arrays) {
+                        Some(InvalidType::EmptyString(this.clone()))
+                    } else {
+                        recur(length)
+                    }
                 }
-            }
-            Type::Tuple(elements) => {
-                for element in elements {
-                    if let Some(invalid_type) = element.program_input_validity(allow_empty_arrays) {
-                        return Some(invalid_type);
+                Type::Tuple(elements) => {
+                    for element in elements {
+                        if let Some(invalid_type) = recur(element) {
+                            return Some(invalid_type);
+                        }
                     }
+                    None
                 }
-                None
-            }
-            Type::DataType(definition, generics) => {
-                let definition = definition.borrow();
+                Type::DataType(definition, generics) => {
+                    let definition = definition.borrow();
 
-                if let Some(fields) = definition.get_fields(generics) {
-                    for (field_name, field, _) in fields {
-                        if let Some(invalid_type) = field.program_input_validity(allow_empty_arrays)
-                        {
-                            let struct_name = definition.name.clone();
-                            let mut fields_raw = definition.fields_raw().unwrap().iter();
-                            let field = fields_raw.find(|field| field.name.as_str() == field_name);
-                            return Some(InvalidType::StructField {
-                                struct_name,
-                                field_name: field.unwrap().name.clone(),
-                                invalid_type: Box::new(invalid_type),
-                            });
+                    if let Some(fields) = definition.get_fields(generics) {
+                        for (field_name, field, _) in fields {
+                            if let Some(invalid_type) = helper(&field, allow_empty_arrays, i) {
+                                let struct_name = definition.name.clone();
+                                let mut fields_raw = definition.fields_raw().unwrap().iter();
+                                let field =
+                                    fields_raw.find(|field| field.name.as_str() == field_name);
+                                return Some(InvalidType::StructField {
+                                    struct_name,
+                                    field_name: field.unwrap().name.clone(),
+                                    invalid_type: Box::new(invalid_type),
+                                });
+                            }
                         }
+                        None
+                    } else {
+                        // Arbitrarily disallow enums from program input, though we may support them later
+                        Some(InvalidType::Enum(this.clone()))
                     }
-                    None
-                } else {
-                    // Arbitrarily disallow enums from program input, though we may support them later
-                    Some(InvalidType::Enum(self.clone()))
                 }
+                Type::InfixExpr(lhs, _, rhs, _) => recur(lhs).or_else(|| recur(rhs)),
             }
-
-            Type::InfixExpr(lhs, _, rhs, _) => lhs
-                .program_input_validity(allow_empty_arrays)
-                .or_else(|| rhs.program_input_validity(allow_empty_arrays)),
         }
+        helper(self, allow_empty_arrays, 0)
     }
 
     /// Returns this type, or a nested one, if this type can be used as a parameter to an ACIR
```

### compiler/noirc_frontend/src/monomorphization/tests.rs
```diff
@@ -458,6 +458,42 @@ fn multiple_trait_impls_with_different_instantiations() {
     ");
 }
 
+#[test]
+#[should_panic(expected = "Type recursion limit reached - types are too large")]
+fn extreme_type_alias_chain_stack_overflow() {
+    // Generate a chain of 2,000 type aliases programmatically
+    // ```
+    // type Alias2000 = u8;
+    // type Alias1999 = Alias2000;
+    // type Alias1998 = Alias1999;
+    // ...
+    // type Alias1 = Alias2;
+    // ```
+    const DEPTH: usize = 2000;
+    let mut aliases = String::new();
+
+    // Start with the base type
+    aliases.push_str(&format!("    type Alias{DEPTH} = u8;\n"));
+
+    // Chain aliases from top to bottom
+    for i in (1..DEPTH).rev() {
+        aliases.push_str(&format!("    type Alias{} = Alias{};\n", i, i + 1));
+    }
+
+    // Insert the following alias chain:
+    let src = format!(
+        r#"
+        {aliases}
+
+        pub fn main(x: Alias1) -> pub u8 {{
+            x
+        }}
+    "#
+    );
+
+    let _ = get_monomorphized(&src);
+}
+
 #[test]
 fn tuple_pattern_becomes_separate_params() {
     let src = r#"
```
