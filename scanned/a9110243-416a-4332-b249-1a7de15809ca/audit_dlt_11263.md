# [?] fix: error instead of stack overflowing on more cyclic aliases (#11185)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-15
Source: https://github.com/noir-lang/noir/commit/d8a674a8a759417323db4ea3ff622cdd095a338e
Type: security-commit

## Details
fix: error instead of stack overflowing on more cyclic aliases (#11185)

Co-authored-by: Ary Borenszweig <asterite@gmail.com>
Co-authored-by: Maxim Vezenov <mvezenov@gmail.com>

## Patch
### compiler/noirc_frontend/src/hir_def/types.rs
```diff
@@ -291,6 +291,14 @@ impl Kind {
     pub(crate) fn is_normal_or_any(&self) -> bool {
         matches!(self, Kind::Normal | Kind::Any)
     }
+
+    /// See [`Type::has_cyclic_alias`] for more detail
+    pub fn has_cyclic_alias(&self, aliases: &mut HashSet<TypeAliasId>) -> bool {
+        match self {
+            Self::Numeric(typ) => typ.has_cyclic_alias(aliases),
+            Self::Any | Self::Normal | Self::Integer | Self::IntegerOrField => false,
+        }
+    }
 }
 
 impl std::fmt::Display for Kind {
@@ -1041,6 +1049,14 @@ impl TypeVariable {
     pub(crate) fn into_implicit_named_generic(self, name: Rc<String>) -> Type {
         Type::NamedGeneric(NamedGeneric { type_var: self, name, implicit: true })
     }
+
+    /// See [`Type::has_cyclic_alias`] for more detail
+    pub fn has_cyclic_alias(&self, aliases: &mut HashSet<TypeAliasId>) -> bool {
+        match &*self.borrow() {
+            TypeBinding::Bound(typ) => typ.has_cyclic_alias(aliases),
+            TypeBinding::Unbound(_, _) => false,
+        }
+    }
 }
 
 /// TypeBindings are the mutable insides of a TypeVariable.
@@ -1492,18 +1508,18 @@ impl Type {
     ///
     /// - `aliases` is a mutable set of TypeAliasId to track visited aliases
     /// - it returns `true` if a cyclic alias is detected, `false` otherwise
+    ///
+    /// Note: cloning the `aliases` parameter when calling this function recursively in multiple
+    /// branches, e.g. as done with [`Type::InfixExpr`], can prevent tests like
+    /// `ensure_repeated_aliases_in_tuples_are_not_detected_as_cyclic_aliases` and
+    /// `ensure_repeated_aliases_in_arrays_are_not_detected_as_cyclic_aliases` from failing
+    /// due to the same non-cyclic alias being detected twice in different recursive calls
     pub fn has_cyclic_alias(&self, aliases: &mut HashSet<TypeAliasId>) -> bool {
         match self {
-            Type::CheckedCast { to, .. } => to.has_cyclic_alias(aliases),
-            Type::NamedGeneric(NamedGeneric { type_var, .. }) => {
-                Type::TypeVariable(type_var.clone()).has_cyclic_alias(aliases)
-            }
-            Type::TypeVariable(var) => match &*var.borrow() {
-                TypeBinding::Bound(typ) => typ.has_cyclic_alias(aliases),
-                TypeBinding::Unbound(_, _) => false,
-            },
+            Type::NamedGeneric(NamedGeneric { type_var, .. }) => type_var.has_cyclic_alias(aliases),
+            Type::TypeVariable(var) => var.has_cyclic_alias(aliases),
             Type::InfixExpr(lhs, _op, rhs, _) => {
-                lhs.has_cyclic_alias(aliases) || rhs.has_cyclic_alias(aliases)
+                lhs.has_cyclic_alias(&mut aliases.clone()) || rhs.has_cyclic_alias(aliases)
             }
             Type::Alias(def, generics) => {
                 let alias_id = def.borrow().id;
@@ -1514,7 +1530,62 @@ impl Type {
                     def.borrow().get_type(generics).has_cyclic_alias(aliases)
                 }
             }
-            _ => false,
+            Type::TraitAsType(_id, _name, generics) => {
+                generics
+                    .ordered
+                    .iter()
+                    .any(|generic| generic.has_cyclic_alias(&mut aliases.clone()))
+                    || generics
+                        .named
+                        .iter()
+                        .any(|generic| generic.typ.has_cyclic_alias(&mut aliases.clone()))
+            }
+            Type::String(len) => len.has_cyclic_alias(aliases),
+            Type::Array(len, typ) => {
+                len.has_cyclic_alias(&mut aliases.clone()) || typ.has_cyclic_alias(aliases)
+            }
+            Type::Vector(typ) => typ.has_cyclic_alias(aliases),
+            Type::DataType(s, args) => {
+                let data_type = s.borrow();
+                data_type
+                    .get_fields(args)
+                    .unwrap_or_else(Vec::new)
+                    .iter()
+                    .any(|(_name, field, _visibility)| field.has_cyclic_alias(&mut aliases.clone()))
+                    || data_type.get_variants(args).unwrap_or_else(Vec::new).iter().any(
+                        |(_name, variant)| {
+                            variant.iter().any(|variant_field| {
+                                variant_field.has_cyclic_alias(&mut aliases.clone())
+                            })
+                        },
+                    )
+            }
+            Type::Tuple(elements) => {
+                elements.iter().any(|element| element.has_cyclic_alias(&mut aliases.clone()))
+            }
+            Type::FmtString(len, elements) => {
+                len.has_cyclic_alias(&mut aliases.clone()) || (*elements).has_cyclic_alias(aliases)
+            }
+            Type::CheckedCast { to, from } => {
+                to.has_cyclic_alias(&mut aliases.clone()) || from.has_cyclic_alias(aliases)
+            }
+            Type::Constant(_x, kind) => kind.has_cyclic_alias(aliases),
+            Type::Forall(typevars, typ) => {
+                typevars.iter().any(|typevar| typevar.has_cyclic_alias(&mut aliases.clone()))
+                    || typ.has_cyclic_alias(aliases)
+            }
+            Type::Function(args, ret, env, _unconstrained) => {
+                args.iter().any(|arg| arg.has_cyclic_alias(&mut aliases.clone()))
+                    || ret.has_cyclic_alias(&mut aliases.clone())
+                    || env.has_cyclic_alias(aliases)
+            }
+            Type::Reference(element, _mutable) => element.has_cyclic_alias(aliases),
+            Type::FieldElement
+            | Type::Integer(_, _)
+            | Type::Bool
+            | Type::Unit
+            | Type::Error
+            | Type::Quoted(_) => false,
         }
     }
 
```

### compiler/noirc_frontend/src/tests/aliases.rs
```diff
@@ -1,4 +1,4 @@
-use crate::tests::{assert_no_errors, check_errors};
+use crate::tests::{UnstableFeature, assert_no_errors, check_errors, check_errors_using_features};
 
 #[test]
 fn allows_usage_of_type_alias_as_argument_type() {
@@ -433,3 +433,254 @@ fn regression_10429_with_trait() {
     "#;
     assert_no_errors(src);
 }
+
+#[test]
+fn regression_10352_parameter() {
+    let src = r#"
+    type Alias = Alias;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_tuple() {
+    let src = r#"
+    type Alias = (Alias,);
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_struct() {
+    let src = r#"
+    struct Foo<T> {
+        x: T
+    }
+
+    type Alias = Foo<Alias>;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_enum() {
+    let src = r#"
+    enum Foo<T> {
+        Bar(T),
+        Baz,
+    }
+
+    type Alias = Foo<Alias>;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_array() {
+    let src = r#"
+    type Alias = [Alias; 3];
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_slice() {
+    let src = r#"
+    type Alias = [Alias];
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_trait_as_type() {
+    let src = r#"
+    trait Foo<T> {}
+
+    type Alias = impl Foo<Alias>;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors_using_features(src, &[UnstableFeature::TraitAsType]);
+}
+
+#[test]
+fn regression_10352_string() {
+    let src = r#"
+    type Alias = str<Alias>;
+    
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_format_string_len() {
+    let src = r#"
+    type Alias = fmtstr<Alias, ()>;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_format_string_env() {
+    let src = r#"
+    type Alias = fmtstr<0, (Alias,)>;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_function_parameter() {
+    let src = r#"
+    type Alias = fn(Alias);
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_function_return() {
+    let src = r#"
+    type Alias = fn() -> Alias;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_function_env() {
+    let src = r#"
+    type Alias = fn[(Alias,)]();
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn regression_10352_immutable_reference() {
+    let src = r#"
+    type Alias = &Alias;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors_using_features(src, &[UnstableFeature::Ownership]);
+}
+
+#[test]
+fn regression_10352_mutable_reference() {
+    let src = r#"
+    type Alias = &mut Alias;
+
+    fn main(_: Alias) {}
+               ^^^^^ Binding `Alias` here to the `_` inside would create a cyclic type
+               ~~~~~ Cyclic types have unlimited size and are prohibited in Noir
+    "#;
+    check_errors(src);
+}
+
+#[test]
+fn ensure_repeated_aliases_in_tuples_are_not_detected_as_cyclic_aliases() {
+    let src = r#"
+    type K = Field;
+    type V = Field;
+
+    fn field_lt(_x: Field, _y: Field) -> bool { true }
+
+    pub global KV_CMP: fn((K, V), (K, V)) -> bool = |a: (K, V), b: (K, V)| field_lt(a.0, b.0);
+
+    fn main() {}
+    "#;
+    assert_no_errors(src);
+}
+
+#[test]
+fn ensure_repeated_aliases_in_arrays_are_not_detected_as_cyclic_aliases() {
+    let src = r#"
+    pub type TReturnElem = [Field; 3];
+    pub type TReturn = [TReturnElem; 2];
+
+    pub fn t_return_elem() -> TReturnElem {
+        [0; 3]
+    }
+
+    pub fn t_return() -> TReturn {
+        [t_return_elem(); 2]
+    }
+
+    pub unconstrained fn two_nested_return_unconstrained() -> (Field, TReturn, Field, TReturn) {
+        (0, t_return(), 0, t_return())
+    }
+
+    pub unconstrained fn foo_return_unconstrained() -> (Field, TReturn, TestTypeFoo) {
+        (0, t_return(), test_type_foo())
+    }
+
+    pub struct TestTypeFoo {
+        a: Field,
+        b: [[[Field; 3]; 4]; 2],
+        c: [TReturnElem; 2],
+        d: TReturnElem,
+    }
+
+    pub fn test_type_foo() -> TestTypeFoo {
+        TestTypeFoo {
+            a: 0,
+            b: [[[0; 3]; 4]; 2],
+            c: [t_return_elem(); 2],
+            d: t_return_elem(),
+        }
+    }
+
+    pub unconstrained fn complex_struct_return() {
+        let _: (Field, [[Field; 3]; 2], TestTypeFoo) = foo_return_unconstrained();
+    }
+    "#;
+    assert_no_errors(src);
+}
```
