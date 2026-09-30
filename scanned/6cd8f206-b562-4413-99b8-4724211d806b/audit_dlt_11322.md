# [?] fix(experimental): Replace most remaining match panics with errors (#7536)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-02-26
Source: https://github.com/noir-lang/noir/commit/d118e170a33d1307ccc1240374e22d86180216ed
Type: security-commit

## Details
fix(experimental): Replace most remaining match panics with errors (#7536)

## Patch
### compiler/noirc_frontend/src/elaborator/enums.rs
```diff
@@ -334,44 +334,30 @@ impl Elaborator<'_> {
                 // - Possible diagnostics improvement: warn if `a` is defined as a variable
                 //   when there is a matching enum variant with name `Foo::a` which can
                 //   be imported. The user likely intended to reference the enum variant.
-                let path_len = path.segments.len();
                 let location = path.location;
                 let last_ident = path.last_ident();
 
+                // Setting this to `Some` allows us to shadow globals with the same name.
+                // We should avoid this if there is a `::` in the path since that means the
+                // user is trying to resolve to a non-local item.
+                let shadow_existing = path.is_ident().then_some(last_ident);
+
                 match self.resolve_path_or_error(path) {
                     Ok(resolution) => self.path_resolution_to_constructor(
                         resolution,
+                        shadow_existing,
                         Vec::new(),
                         expected_type,
                         location,
                         variables_defined,
                     ),
-                    Err(_) if path_len == 1 => {
-                        // Define the variable
-                        let kind = DefinitionKind::Local(None);
-
-                        if let Some(existing) =
-                            variables_defined.iter().find(|elem| *elem == &last_ident)
-                        {
-                            // Allow redefinition of `_` only, to ignore variables
-                            if last_ident.0.contents != "_" {
-                                let error = ResolverError::VariableAlreadyDefinedInPattern {
-                                    existing: existing.clone(),
-                                    new_location: last_ident.location(),
-                                };
-                                self.push_err(error);
-                            }
+                    Err(error) => {
+                        if let Some(name) = shadow_existing {
+                            self.define_pattern_variable(name, expected_type, variables_defined)
                         } else {
-                            variables_defined.push(last_ident.clone());
+                            self.push_err(error);
+                            Pattern::Error
                         }
-
-                        let id = self.add_variable_decl(last_ident, false, true, true, kind).id;
-                        self.interner.push_definition_type(id, expected_type.clone());
-                        Pattern::Binding(id)
-                    }
-                    Err(error) => {
-                        self.push_err(error);
-                        Pattern::Error
                     }
                 }
             }
@@ -436,6 +422,32 @@ impl Elaborator<'_> {
         }
     }
 
+    fn define_pattern_variable(
+        &mut self,
+        name: Ident,
+        expected_type: &Type,
+        variables_defined: &mut Vec<Ident>,
+    ) -> Pattern {
+        // Define the variable
+        let kind = DefinitionKind::Local(None);
+
+        if let Some(existing) = variables_defined.iter().find(|elem| *elem == &name) {
+            // Allow redefinition of `_` only, to ignore variables
+            if name.0.contents != "_" {
+                self.push_err(ResolverError::VariableAlreadyDefinedInPattern {
+                    existing: existing.clone(),
+                    new_location: name.location(),
+                });
+            }
+        } else {
+            variables_defined.push(name.clone());
+        }
+
+        let id = self.add_variable_decl(name, false, true, true, kind).id;
+        self.interner.push_definition_type(id, expected_type.clone());
+        Pattern::Binding(id)
+    }
+
     fn constructor_to_pattern(
         &mut self,
         constructor: ConstructorExpression,
@@ -490,13 +502,21 @@ impl Elaborator<'_> {
         expected_type: &Type,
         variables_defined: &mut Vec<Ident>,
     ) -> Pattern {
+        let syntax_error = |this: &mut Self| {
+            this.push_err(ResolverError::InvalidSyntaxInPattern { location: name.location });
+            Pattern::Error
+        };
+
         match name.kind {
             ExpressionKind::Variable(path) => {
                 let location = path.location;
 
                 match self.resolve_path_or_error(path) {
+                    // Use None for `name` here - we don't want to define a variable if this
+                    // resolves to an existing item.
                     Ok(resolution) => self.path_resolution_to_constructor(
                         resolution,
+                        None,
                         args,
                         expected_type,
                         location,
@@ -526,28 +546,47 @@ impl Elaborator<'_> {
                         variables_defined,
                     )
                 } else {
-                    panic!("Invalid expr kind {name}")
+                    syntax_error(self)
                 }
             }
-            other => todo!("invalid constructor `{other}`"),
+            _ => syntax_error(self),
         }
     }
 
+    /// Convert a PathResolutionItem - usually an enum variant or global - to a Constructor.
+    /// If `name` is `Some`, we'll define a Pattern::Binding instead of erroring if the
+    /// item doesn't resolve to a variant or global. This would shadow an existing
+    /// value such as a free function. Generally this is desired unless the variable was
+    /// a path with multiple components such as `foo::bar` which should always be treated as
+    /// a path to an existing item.
     fn path_resolution_to_constructor(
         &mut self,
-        name: PathResolutionItem,
+        resolution: PathResolutionItem,
+        name: Option<Ident>,
         args: Vec<Expression>,
         expected_type: &Type,
         location: Location,
         variables_defined: &mut Vec<Ident>,
     ) -> Pattern {
-        let (actual_type, expected_arg_types, variant_index) = match name {
+        let (actual_type, expected_arg_types, variant_index) = match &resolution {
             PathResolutionItem::Global(id) => {
                 // variant constant
-                let global = self.interner.get_global(id);
-                let variant_index = match global.value {
-                    GlobalValue::Resolved(Value::Enum(tag, ..)) => tag,
-                    _ => todo!("Value is not an enum constant"),
+                self.elaborate_global_if_unresolved(id);
+                let global = self.interner.get_global(*id);
+                let variant_index = match &global.value {
+                    GlobalValue::Resolved(Value::Enum(tag, ..)) => *tag,
+                    // This may be a global constant. Treat it like a normal constant
+                    GlobalValue::Resolved(value) => {
+                        let value = value.clone();
+                        return self.global_constant_to_integer_constructor(
+                            value,
+                            expected_type,
+                            location,
+                        );
+                    }
+                    // We tried to resolve this value above so there must have been an error
+                    // in doing so. Avoid reporting an additional error.
+                    _ => return Pattern::Error,
                 };
 
                 let global_type = self.interner.definition_type(global.definition_id);
@@ -556,8 +595,12 @@ impl Elaborator<'_> {
             }
             PathResolutionItem::Method(_type_id, _type_turbofish, func_id) => {
                 // TODO(#7430): Take type_turbofish into account when instantiating the function's type
-                let meta = self.interner.function_meta(&func_id);
-                let Some(variant_index) = meta.enum_variant_index else { todo!("not a variant") };
+                let meta = self.interner.function_meta(func_id);
+                let Some(variant_index) = meta.enum_variant_index else {
+                    let item = resolution.description();
+                    self.push_err(ResolverError::UnexpectedItemInPattern { location, item });
+                    return Pattern::Error;
+                };
 
                 let (actual_type, expected_arg_types) = match meta.typ.instantiate(self.interner).0
                 {
@@ -567,18 +610,22 @@ impl Elaborator<'_> {
 
                 (actual_type, expected_arg_types, variant_index)
             }
-            PathResolutionItem::Module(_) => todo!("path_resolution_to_constructor {name:?}"),
-            PathResolutionItem::Type(_) => todo!("path_resolution_to_constructor {name:?}"),
-            PathResolutionItem::TypeAlias(_) => todo!("path_resolution_to_constructor {name:?}"),
-            PathResolutionItem::Trait(_) => todo!("path_resolution_to_constructor {name:?}"),
-            PathResolutionItem::ModuleFunction(_) => {
-                todo!("path_resolution_to_constructor {name:?}")
-            }
-            PathResolutionItem::TypeAliasFunction(_, _, _) => {
-                todo!("path_resolution_to_constructor {name:?}")
-            }
-            PathResolutionItem::TraitFunction(_, _, _) => {
-                todo!("path_resolution_to_constructor {name:?}")
+            PathResolutionItem::Module(_)
+            | PathResolutionItem::Type(_)
+            | PathResolutionItem::TypeAlias(_)
+            | PathResolutionItem::Trait(_)
+            | PathResolutionItem::ModuleFunction(_)
+            | PathResolutionItem::TypeAliasFunction(_, _, _)
+            | PathResolutionItem::TraitFunction(_, _, _) => {
+                // This variable refers to an existing item
+                if let Some(name) = name {
+                    // If name is set, shadow the existing item
+                    return self.define_pattern_variable(name, expected_type, variables_defined);
+                } else {
+                    let item = resolution.description();
+                    self.push_err(ResolverError::UnexpectedItemInPattern { location, item });
+                    return Pattern::Error;
+                }
             }
         };
 
@@ -591,7 +638,10 @@ impl Elaborator<'_> {
         });
 
         if args.len() != expected_arg_types.len() {
-            // error expected N args, found M?
+            let expected = expected_arg_types.len();
+            let found = args.len();
+            self.push_err(TypeCheckError::ArityMisMatch { expected, found, location });
+            return Pattern::Error;
         }
 
         let args = args.into_iter().zip(expected_arg_types);
@@ -602,6 +652,55 @@ impl Elaborator<'_> {
         Pattern::Constructor(constructor, args)
     }
 
+    fn global_constant_to_integer_constructor(
+        &mut self,
+        constant: Value,
+        expected_type: &Type,
+        location: Location,
+    ) -> Pattern {
+        let actual_type = constant.get_type();
+        self.unify(&actual_type, expected_type, || TypeCheckError::TypeMismatch {
+            expected_typ: expected_type.to_string(),
+            expr_typ: actual_type.to_string(),
+            expr_location: location,
+        });
+
+        // Convert a signed integer type like i32 to SignedField
+        macro_rules! signed_to_signed_field {
+            ($value:expr) => {{
+                let negative = $value < 0;
+                // Widen the value so that SignedType::MIN does not wrap to 0 when negated below
+                let mut widened = $value as i128;
+                if negative {
+                    widened = -widened;
+                }
+                SignedField::new(widened.into(), negative)
+            }};
+        }
+
+        let value = match constant {
+            Value::Bool(value) => SignedField::positive(value),
+            Value::Field(value) => SignedField::positive(value),
+            Value::I8(value) => signed_to_signed_field!(value),
+            Value::I16(value) => signed_to_signed_field!(value),
+            Value::I32(value) => signed_to_signed_field!(value),
+            Value::I64(value) => signed_to_signed_field!(value),
+            Value::U1(value) => SignedField::positive(value),
+            Value::U8(value) => SignedField::positive(value as u128),
+            Value::U16(value) => SignedField::positive(value as u128),
+            Value::U32(value) => SignedField::positive(value),
+            Value::U64(value) => SignedField::positive(value),
+            Value::U128(value) => SignedField::positive(value),
+            Value::Zeroed(_) => SignedField::positive(0u32),
+            _ => {
+                self.push_err(ResolverError::NonIntegerGlobalUsedInPattern { location });
+                return Pattern::Error;
+            }
+        };
+
+        Pattern::Int(value)
+    }
+
     fn struct_name_and_field_types(
         &mut self,
         typ: &Type,
@@ -663,8 +762,6 @@ impl Elaborator<'_> {
                 Ok(HirMatch::Switch(branch_var, cases, Some(fallback)))
             }
 
-            Type::Array(_, _) => todo!(),
-            Type::Slice(_) => todo!(),
             Type::Bool => {
                 let cases = vec![
                     (Constructor::False, Vec::new(), Vec::new()),
@@ -715,12 +812,16 @@ impl Elaborator<'_> {
                 } else {
                     drop(def);
                     let typ = Type::DataType(type_def, generics);
-                    todo!("Cannot match on type {typ}")
+                    Err(ResolverError::TypeUnsupportedInMatch { typ, location })
                 }
             }
-            typ @ (Type::Alias(_, _)
-            | Type::TypeVariable(_)
+            // We could match on these types in the future
+            typ @ (Type::Array(_, _)
+            | Type::Slice(_)
             | Type::String(_)
+            // But we'll never be able to match on these
+            | Type::Alias(_, _)
+            | Type::TypeVariable(_)
             | Type::FmtString(_, _)
             | Type::TraitAsType(_, _, _)
             | Type::NamedGeneric(_, _)
@@ -731,7 +832,9 @@ impl Elaborator<'_> {
             | Type::Constant(_, _)
             | Type::Quoted(_)
             | Type::InfixExpr(_, _, _, _)
-            | Type::Error) => todo!("Cannot match on type {typ:?}"),
+            | Type::Error) => {
+                Err(ResolverError::TypeUnsupportedInMatch { typ, location })
+            },
         }
     }
 
@@ -769,11 +872,9 @@ impl Elaborator<'_> {
                 let (key, cons) = match col.pattern {
                     Pattern::Int(val) => ((val, val), Constructor::Int(val)),
                     Pattern::Range(start, stop) => ((start, stop), Constructor::Range(start, stop)),
-                    Pattern::Error => continue,
-                    pattern => {
-                        eprintln!("Unexpected pattern for integer type: {pattern:?}");
-                        continue;
-                    }
+                    // Any other pattern shouldn't have an integer type and we expect a type
+                    // check error to already have been issued.
+                    _ => continue,
                 };
 
                 if let Some(index) = tested.get(&key) {
```

### compiler/noirc_frontend/src/hir/resolution/errors.rs
```diff
@@ -188,6 +188,12 @@ pub enum ResolverError {
     InvalidSyntaxInPattern { location: Location },
     #[error("Variable '{existing}' was already defined in the same match pattern")]
     VariableAlreadyDefinedInPattern { existing: Ident, new_location: Location },
+    #[error("Only integer globals can be used in match patterns")]
+    NonIntegerGlobalUsedInPattern { location: Location },
+    #[error("Cannot match on values of type `{typ}`")]
+    TypeUnsupportedInMatch { typ: Type, location: Location },
+    #[error("Expected a struct, enum, or literal value in pattern, but found a {item}")]
+    UnexpectedItemInPattern { location: Location, item: &'static str },
 }
 
 impl ResolverError {
@@ -254,6 +260,9 @@ impl ResolverError {
             | ResolverError::MutatingComptimeInNonComptimeContext { location, .. }
             | ResolverError::InvalidInternedStatementInExpr { location, .. }
             | ResolverError::InvalidSyntaxInPattern { location }
+            | ResolverError::NonIntegerGlobalUsedInPattern { location, .. }
+            | ResolverError::TypeUnsupportedInMatch { location, .. }
+            | ResolverError::UnexpectedItemInPattern { location, .. }
             | ResolverError::VariableAlreadyDefinedInPattern { new_location: location, .. } => {
                 *location
             }
@@ -796,6 +805,25 @@ impl<'a> From<&'a ResolverError> for Diagnostic {
                 error.add_secondary(format!("`{existing}` was previously defined here"), existing.location());
                 error
             },
+            ResolverError::NonIntegerGlobalUsedInPattern { location } => {
+                let message = "Only integer or boolean globals can be used in match patterns".to_string();
+                let secondary = "This global is not an integer or boolean".to_string();
+                Diagnostic::simple_error(message, secondary, *location)
+            },
+            ResolverError::TypeUnsupportedInMatch { typ, location } => {
+                Diagnostic::simple_error(
+                    format!("Cannot match on values of type `{typ}`"), 
+                    String::new(),
+                    *location,
+                )
+            },
+            ResolverError::UnexpectedItemInPattern { item, location } => {
+                Diagnostic::simple_error(
+                    format!("Expected a struct, enum, or literal pattern, but found a {item}"), 
+                    String::new(),
+                    *location,
+                )
+            },
         }
     }
 }
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -3,6 +3,7 @@
 mod aliases;
 mod arithmetic_generics;
 mod bound_checks;
+mod enums;
 mod imports;
 mod metaprogramming;
 mod name_shadowing;
@@ -4213,28 +4214,6 @@ fn regression_7088() {
     assert_no_errors(src);
 }
 
-#[test]
-fn error_with_duplicate_enum_variant() {
-    let src = r#"
-    enum Foo {
-        Bar(i32),
-        Bar(u8),
-    }
-
-    fn main() {}
-    "#;
-    let errors = get_program_errors(src);
-    assert_eq!(errors.len(), 2);
-    assert!(matches!(
-        &errors[0],
-        CompilationError::DefinitionError(DefCollectorErrorKind::Duplicate { .. })
-    ));
-    assert!(matches!(
-        &errors[1],
-        CompilationError::ResolverError(ResolverError::UnusedItem { .. })
-    ));
-}
-
 #[test]
 fn errors_on_empty_loop_no_break() {
     let src = r#"
@@ -4410,69 +4389,6 @@ fn errors_if_while_body_type_is_not_unit() {
     };
 }
 
-#[test]
-fn errors_on_unspecified_unstable_enum() {
-    // Enums are experimental - this will need to be updated when they are stabilized
-    let src = r#"
-    enum Foo { Bar }
-
-    fn main() {
-        let _x = Foo::Bar;
-    }
-    "#;
-
-    let no_features = &[];
-    let errors = get_program_using_features(src, no_features).2;
-    assert_eq!(errors.len(), 1);
-
-    let CompilationError::ParseError(error) = &errors[0] else {
-        panic!("Expected a ParseError experimental feature error");
-    };
-
-    assert!(matches!(error.reason(), Some(ParserErrorReason::ExperimentalFeature(_))));
-}
-
-#[test]
-fn errors_on_unspecified_unstable_match() {
-    // Enums are experimental - this will need to be updated when they are stabilized
-    let src = r#"
-    fn main() {
-        match 3 {
-            _ => (),
-        }
-    }
-    "#;
-
-    let no_features = &[];
-    let errors = get_program_using_features(src, no_features).2;
-    assert_eq!(errors.len(), 1);
-
-    let CompilationError::ParseError(error) = &errors[0] else {
-        panic!("Expected a ParseError experimental feature error");
-    };
-
-    assert!(matches!(error.reason(), Some(ParserErrorReason::ExperimentalFeature(_))));
-}
-
-#[test]
-fn errors_on_repeated_match_variables_in_pattern() {
-    let src = r#"
-    fn main() {
-        match (1, 2) {
-            (_x, _x) => (),
-        }
-    }
-    "#;
-
-    let errors = get_program_errors(src);
-    assert_eq!(errors.len(), 1);
-
-    assert!(matches!(
-        &errors[0],
-        CompilationError::ResolverError(ResolverError::VariableAlreadyDefinedInPattern { .. })
-    ));
-}
-
 #[test]
 fn check_impl_duplicate_method_without_self() {
     let src = "
@@ -4494,81 +4410,6 @@ fn check_impl_duplicate_method_without_self() {
     ));
 }
 
-#[test]
-fn duplicate_field_in_match_struct_pattern() {
-    let src = r#"
-fn main() {
-    let foo = Foo { x: 10, y: 20 };
-    match foo {
-        Foo { x: _, x: _, y: _ } => {}
-    }
-}
-
-struct Foo {
-    x: i32,
-    y: Field,
-}
-    "#;
-
-    let errors = get_program_errors(src);
-    assert_eq!(errors.len(), 1);
-
-    assert!(matches!(
-        &errors[0],
-        CompilationError::ResolverError(ResolverError::DuplicateField { .. })
-    ));
-}
-
-#[test]
-fn missing_field_in_match_struct_pattern() {
-    let src = r#"
-fn main() {
-    let foo = Foo { x: 10, y: 20 };
-    match foo {
-        Foo { x: _ } => {}
-    }
-}
-
-struct Foo {
-    x: i32,
-    y: Field,
-}
-    "#;
-
-    let errors = get_program_errors(src);
-    assert_eq!(errors.len(), 1);
-
-    assert!(matches!(
-        &errors[0],
-        CompilationError::ResolverError(ResolverError::MissingFields { .. })
-    ));
-}
-
-#[test]
-fn no_such_field_in_match_struct_pattern() {
-    let src = r#"
-fn main() {
-    let foo = Foo { x: 10, y: 20 };
-    match foo {
-        Foo { x: _, y: _, z: _ } => {}
-    }
-}
-
-struct Foo {
-    x: i32,
-    y: Field,
-}
-    "#;
-
-    let errors = get_program_errors(src);
-    assert_eq!(errors.len(), 1);
-
-    assert!(matches!(
-        &errors[0],
-        CompilationError::ResolverError(ResolverError::NoSuchField { .. })
-    ));
-}
-
 #[test]
 fn int_min_global() {
     let src = r#"
```

### compiler/noirc_frontend/src/tests/enums.rs
```diff
@@ -0,0 +1,228 @@
+use crate::{
+    hir::{
+        def_collector::{dc_crate::CompilationError, errors::DefCollectorErrorKind},
+        resolution::errors::ResolverError,
+        type_check::TypeCheckError,
+    },
+    parser::ParserErrorReason,
+    tests::{get_program_errors, get_program_using_features},
+};
+use CompilationError::*;
+use DefCollectorErrorKind::Duplicate;
+use ResolverError::*;
+use TypeCheckError::{ArityMisMatch, TypeMismatch};
+
+#[test]
+fn error_with_duplicate_enum_variant() {
+    let src = r#"
+        enum Foo {
+            Bar(i32),
+            Bar(u8),
+        }
+
+        fn main() {}
+    "#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 2);
+    assert!(matches!(&errors[0], DefinitionError(Duplicate { .. })));
+    assert!(matches!(&errors[1], ResolverError(UnusedItem { .. })));
+}
+
+#[test]
+fn errors_on_unspecified_unstable_enum() {
+    // Enums are experimental - this will need to be updated when they are stabilized
+    let src = r#"
+        enum Foo { Bar }
+
+        fn main() {
+            let _x = Foo::Bar;
+        }
+    "#;
+
+    let no_features = &[];
+    let errors = get_program_using_features(src, no_features).2;
+    assert_eq!(errors.len(), 1);
+
+    let CompilationError::ParseError(error) = &errors[0] else {
+        panic!("Expected a ParseError experimental feature error");
+    };
+
+    assert!(matches!(error.reason(), Some(ParserErrorReason::ExperimentalFeature(_))));
+}
+
+#[test]
+fn errors_on_unspecified_unstable_match() {
+    // Enums are experimental - this will need to be updated when they are stabilized
+    let src = r#"
+        fn main() {
+            match 3 {
+                _ => (),
+            }
+        }
+    "#;
+
+    let no_features = &[];
+    let errors = get_program_using_features(src, no_features).2;
+    assert_eq!(errors.len(), 1);
+
+    let CompilationError::ParseError(error) = &errors[0] else {
+        panic!("Expected a ParseError experimental feature error");
+    };
+
+    assert!(matches!(error.reason(), Some(ParserErrorReason::ExperimentalFeature(_))));
+}
+
+#[test]
+fn errors_on_repeated_match_variables_in_pattern() {
+    let src = r#"
+        fn main() {
+            match (1, 2) {
+                (_x, _x) => (),
+            }
+        }
+    "#;
+
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    assert!(matches!(&errors[0], ResolverError(VariableAlreadyDefinedInPattern { .. })));
+}
+
+#[test]
+fn duplicate_field_in_match_struct_pattern() {
+    let src = r#"
+        fn main() {
+            let foo = Foo { x: 10, y: 20 };
+            match foo {
+                Foo { x: _, x: _, y: _ } => {}
+            }
+        }
+
+        struct Foo {
+            x: i32,
+            y: Field,
+        }
+    "#;
+
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    assert!(matches!(&errors[0], ResolverError(DuplicateField { .. })));
+}
+
+#[test]
+fn missing_field_in_match_struct_pattern() {
+    let src = r#"
+        fn main() {
+            let foo = Foo { x: 10, y: 20 };
+            match foo {
+                Foo { x: _ } => {}
+            }
+        }
+
+        struct Foo {
+            x: i32,
+            y: Field,
+        }
+    "#;
+
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    assert!(matches!(&errors[0], ResolverError(MissingFields { .. })));
+}
+
+#[test]
+fn no_such_field_in_match_struct_pattern() {
+    let src = r#"
+        fn main() {
+            let foo = Foo { x: 10, y: 20 };
+            match foo {
+                Foo { x: _, y: _, z: _ } => {}
+            }
+        }
+
+        struct Foo {
+            x: i32,
+            y: Field,
+        }
+    "#;
+
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    assert!(matches!(&errors[0], ResolverError(NoSuchField { .. })));
+}
+
+#[test]
+fn match_integer_type_mismatch_in_pattern() {
+    let src = r#"
+        fn main() {
+            match 2 {
+                Foo::One(_) => (),
+            }
+        }
+
+        enum Foo {
+            One(i32),
+        }
+    "#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 1);
+
+    assert!(matches!(&errors[0], TypeError(TypeMismatch { .. })));
+}
+
+#[test]
+fn match_shadow_global() {
+    let src = r#"
+        fn main() {
+            match 2 {
+                foo => assert_eq(foo, 2),
+            }
+        }
+
+        fn foo() {}
+    "#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 0);
+}
+
+#[test]
+fn match_no_shadow_global() {
+    let src = r#"
+        fn main() {
+            match 2 {
+                crate::foo => (),
+            }
+        }
+
+        fn foo() {}
+    "#;
+    let errors = dbg!(get_program_errors(src));
+    assert_eq!(errors.len(), 1);
+
+    assert!(matches!(&errors[0], ResolverError(UnexpectedItemInPattern { .. })));
+}
+
+#[test]
+fn constructor_arg_arity_mismatch_in_pattern() {
+    let src = r#"
+        fn main() {
+            match Foo::One(1) {
+                Foo::One(_, _) => (), // too many
+                Foo::Two(_) => (),    // too few
+            }
+        }
+
+        enum Foo {
+            One(i32),
+            Two(i32, i32),
+        }
+    "#;
+    let errors = get_program_errors(src);
+    assert_eq!(errors.len(), 2);
+
+    assert!(matches!(&errors[0], TypeError(ArityMisMatch { .. })));
+    assert!(matches!(&errors[1], TypeError(ArityMisMatch { .. })));
+}
```

### test_programs/compile_success_empty/enums/src/main.nr
```diff
@@ -20,8 +20,20 @@ fn primitive_tests() {
         false => fail(),
         true => (),
     }
+
+    // Ensure we can match on MIN and use globals as constants
+    let i64_min = I64_MIN;
+    match i64_min {
+        9_223_372_036_854_775_807 => fail(),
+        -9_223_372_036_854_775_807 => fail(),
+        0 => fail(),
+        I64_MIN => (),
+        _ => fail(),
+    }
 }
 
+global I64_MIN: i64 = -9_223_372_036_854_775_808;
+
 enum Foo<T> {
     A(Field, Field),
     B(u32),
```
