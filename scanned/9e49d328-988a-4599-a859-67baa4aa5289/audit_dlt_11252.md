# [?] fix: avoiding panic from cyclic global (#11537)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-02-25
Source: https://github.com/noir-lang/noir/commit/34e3758fba436ed6cf1565e15fc0efccab059f6a
Type: security-commit

## Details
fix: avoiding panic from cyclic global (#11537)

Co-authored-by: Akosh Farkash <aakoshh@gmail.com>

## Patch
### compiler/noirc_frontend/src/elaborator/enums.rs
```diff
@@ -340,10 +340,10 @@ impl Elaborator<'_> {
                 CompilationError::ResolverError(ResolverError::DuplicateDefinition { .. })
             ) {
                 // Expecting a DefCollectorErrorKind::Duplicate error in this case
-                TypeCheckError::ExpectingOtherError {
-                    message: "define_enum_variant_function: duplicate definition".to_string(),
+                TypeCheckError::expecting_other_error(
+                    "define_enum_variant_function: duplicate definition",
                     location,
-                }
+                )
                 .into()
             } else {
                 error
```

### compiler/noirc_frontend/src/elaborator/lints.rs
```diff
@@ -5,6 +5,7 @@ use crate::{
     ast::{Ident, NoirFunction},
     graph::CrateId,
     hir::{
+        def_collector::dc_crate::CompilationError,
         resolution::errors::{PubPosition, ResolverError},
         type_check::TypeCheckError,
     },
@@ -325,9 +326,13 @@ pub(super) fn unconstrained_function_return(
 pub(super) fn error_if_verify_proof_with_type(
     interner: &NodeInterner,
     func_expr_id: ExprId,
-) -> Option<TypeCheckError> {
+    location: Location,
+) -> Option<CompilationError> {
     // Called function
-    let func_id = interner.lookup_function_from_expr(&func_expr_id)?;
+    let func_id = match interner.lookup_function_from_expr(&func_expr_id, location) {
+        Ok(func_id) => func_id?,
+        Err(error) => return Some(error.into()),
+    };
     let func_name = interner.function_name(&func_id);
 
     // Check if it is verify_proof_with_type and is from the standard library
@@ -336,7 +341,7 @@ pub(super) fn error_if_verify_proof_with_type(
         if module_id.krate.is_stdlib() {
             // Get the function location for the error
             let location = interner.expr_location(&func_expr_id);
-            return Some(TypeCheckError::VerifyProofWithTypeInBrillig { location });
+            return Some(TypeCheckError::VerifyProofWithTypeInBrillig { location }.into());
         }
     }
 
```

### compiler/noirc_frontend/src/elaborator/trait_impls.rs
```diff
@@ -85,10 +85,10 @@ impl Elaborator<'_> {
             });
         } else if get_type_method_key(&self_type).is_none() {
             let error: CompilationError = if self_type == Type::Error {
-                TypeCheckError::ExpectingOtherError {
-                    message: "collect_trait_impl: missing trait type".to_string(),
-                    location: self_type_location,
-                }
+                TypeCheckError::expecting_other_error(
+                    "collect_trait_impl: missing trait type",
+                    self_type_location,
+                )
                 .into()
             } else {
                 ResolverError::TypeUnsupportedForTraitImpl {
@@ -137,10 +137,10 @@ impl Elaborator<'_> {
                         // This too can happen if the associated type is specified directly in the impl trait generics,
                         // like `impl<H> BuildHasher<H = H>`, where `H` is a named generic but its resolution isn't delayed.
                         // This can't be done in code, but it could happen with unquoted types.
-                        self.push_err(TypeCheckError::ExpectingOtherError {
-                            message: "collect_trait_impl: missing associated type".to_string(),
-                            location: trait_impl.object_type.location,
-                        });
+                        self.push_err(TypeCheckError::expecting_other_error(
+                            "collect_trait_impl: missing associated type",
+                            trait_impl.object_type.location,
+                        ));
                         continue;
                     };
                     let wildcard_allowed =
@@ -202,10 +202,10 @@ impl Elaborator<'_> {
             for func_id in &methods {
                 if self.interner.set_function_trait(*func_id, self_type.clone(), trait_id).is_some()
                 {
-                    self.push_err(TypeCheckError::ExpectingOtherError {
-                        message: "collect_trait_impl: overlapping function trait".to_string(),
+                    self.push_err(TypeCheckError::expecting_other_error(
+                        "collect_trait_impl: overlapping function trait",
                         location,
-                    });
+                    ));
                 }
 
                 // A trait impl method has the same visibility as its trait
@@ -225,10 +225,10 @@ impl Elaborator<'_> {
                     Ident::new(name, trait_impl.r#trait.location)
                 }
                 _ => {
-                    self.push_err(TypeCheckError::ExpectingOtherError {
-                        message: "collect_trait_impl: missing trait type".to_string(),
+                    self.push_err(TypeCheckError::expecting_other_error(
+                        "collect_trait_impl: missing trait type",
                         location,
-                    });
+                    ));
                     Ident::new(trait_impl.r#trait.to_string(), trait_impl.r#trait.location)
                 }
             };
@@ -582,31 +582,26 @@ impl Elaborator<'_> {
         trait_impl: &UnresolvedTraitImpl,
     ) {
         let Some(trait_id) = trait_impl.trait_id else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message:
-                    "check_trait_impl_where_clause_matches_trait_where_clause: missing trait ID"
-                        .to_string(),
-                location: trait_impl.object_type.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "check_trait_impl_where_clause_matches_trait_where_clause: missing trait ID",
+                trait_impl.object_type.location,
+            ));
             return;
         };
 
         let Some(impl_id) = trait_impl.impl_id else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message:
-                    "check_trait_impl_where_clause_matches_trait_where_clause: missing impl ID"
-                        .to_string(),
-                location: trait_impl.object_type.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "check_trait_impl_where_clause_matches_trait_where_clause: missing impl ID",
+                trait_impl.object_type.location,
+            ));
             return;
         };
 
         let Some(the_trait) = self.interner.try_get_trait(trait_id) else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message: "check_trait_impl_where_clause_matches_trait_where_clause: missing trait"
-                    .to_string(),
-                location: trait_impl.object_type.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "check_trait_impl_where_clause_matches_trait_where_clause: missing trait",
+                trait_impl.object_type.location,
+            ));
             return;
         };
 
@@ -640,10 +635,10 @@ impl Elaborator<'_> {
             let Some(trait_constraint_trait) =
                 self.interner.try_get_trait(trait_constraint.trait_bound.trait_id)
             else {
-                self.push_err(TypeCheckError::ExpectingOtherError {
-                    message: "check_trait_impl_where_clause_matches_trait_where_clause: missing trait constraint trait".to_string(),
-                    location: *error_location,
-                });
+                self.push_err(TypeCheckError::expecting_other_error(
+                    "check_trait_impl_where_clause_matches_trait_where_clause: missing trait constraint trait",
+                    *error_location,
+                ));
                 continue;
             };
             let trait_constraint_trait_name = trait_constraint_trait.name.to_string();
@@ -721,34 +716,34 @@ impl Elaborator<'_> {
 
     pub(super) fn check_parent_traits_are_implemented(&mut self, trait_impl: &UnresolvedTraitImpl) {
         let Some(trait_id) = trait_impl.trait_id else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message: "check_parent_traits_are_implemented: missing trait ID".to_string(),
-                location: trait_impl.object_type.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "check_parent_traits_are_implemented: missing trait ID",
+                trait_impl.object_type.location,
+            ));
             return;
         };
 
         let Some(object_type) = &trait_impl.resolved_object_type else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message: "check_parent_traits_are_implemented: missing object type".to_string(),
-                location: trait_impl.object_type.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "check_parent_traits_are_implemented: missing object type",
+                trait_impl.object_type.location,
+            ));
             return;
         };
 
         let Some(the_trait) = self.interner.try_get_trait(trait_id) else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message: "check_parent_traits_are_implemented: missing trait".to_string(),
-                location: trait_impl.object_type.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "check_parent_traits_are_implemented: missing trait",
+                trait_impl.object_type.location,
+            ));
             return;
         };
 
         let Some(impl_id) = trait_impl.impl_id else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message: "check_parent_traits_are_implemented: missing impl ID".to_string(),
-                location: trait_impl.object_type.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "check_parent_traits_are_implemented: missing impl ID",
+                trait_impl.object_type.location,
+            ));
             return;
         };
 
```

### compiler/noirc_frontend/src/elaborator/traits.rs
```diff
@@ -368,10 +368,10 @@ impl Elaborator<'_> {
         let Ok(PathResolutionItem::Trait(trait_id)) =
             self.resolve_path_or_error(trait_path.clone(), PathResolutionTarget::Type)
         else {
-            self.push_err(TypeCheckError::ExpectingOtherError {
-                message: "add_missing_named_generics: missing trait".to_string(),
-                location: trait_path.location,
-            });
+            self.push_err(TypeCheckError::expecting_other_error(
+                "add_missing_named_generics: missing trait",
+                object.location,
+            ));
             return Vec::new();
         };
 
@@ -626,10 +626,10 @@ impl Elaborator<'_> {
                 return;
             }
             Err(error) => {
-                self.push_err(TypeCheckError::ExpectingOtherError {
-                    message: format!("Elaborator::add_trait_bound_to_scope: encountered error while running add_assumed_trait_implementation: {error:?}"),
+                self.push_err(TypeCheckError::expecting_other_error(
+                    format!("Elaborator::add_trait_bound_to_scope: encountered error while running add_assumed_trait_implementation: {error:?}"),
                     location,
-                });
+                ));
             }
         }
 
@@ -855,10 +855,10 @@ pub(crate) fn check_trait_impl_method_matches_declaration(
     // If the trait implementation is not defined in the interner then there was a previous
     // error in resolving the trait path and there is likely no trait for this impl.
     let Some(impl_) = interner.try_get_trait_implementation(impl_id) else {
-        errors.push(TypeCheckError::ExpectingOtherError {
-            message: "check_trait_impl_method_matches_declaration: missing trait impl".to_string(),
-            location: noir_function.def.location,
-        });
+        errors.push(TypeCheckError::expecting_other_error(
+            "check_trait_impl_method_matches_declaration: missing trait impl",
+            meta.name.location,
+        ));
         return errors;
     };
 
@@ -943,11 +943,10 @@ pub(crate) fn check_trait_impl_method_matches_declaration(
             &mut errors,
         );
     } else {
-        errors.push(TypeCheckError::ExpectingOtherError {
-            message: "check_trait_impl_method_matches_declaration: missing trait method function"
-                .to_string(),
-            location: meta.name.location,
-        });
+        errors.push(TypeCheckError::expecting_other_error(
+            "check_trait_impl_method_matches_declaration: missing trait method function",
+            meta.name.location,
+        ));
     }
 
     errors
```

### compiler/noirc_frontend/src/elaborator/types.rs
```diff
@@ -818,10 +818,10 @@ impl Elaborator<'_> {
                 };
 
                 if !suffix_kind.unifies(expected_kind) {
-                    self.push_err(TypeCheckError::ExpectingOtherError {
-                        message: format!("convert_expression_type: {suffix_kind} does not unify with expected {expected_kind}"),
+                    self.push_err(TypeCheckError::expecting_other_error(
+                        format!("convert_expression_type: {suffix_kind} does not unify with expected {expected_kind}"),
                         location,
-                    });
+                    ));
                 }
 
                 Type::Constant(int, suffix_kind)
@@ -1988,11 +1988,10 @@ impl Elaborator<'_> {
                 });
             }
             Type::Error => {
-                self.push_err(TypeCheckError::ExpectingOtherError {
-                    message: "type_check_operator_method: encountered method_type of type 'error'"
-                        .to_string(),
+                self.push_err(TypeCheckError::expecting_other_error(
+                    "type_check_operator_method: encountered method_type of type 'error'",
                     location,
-                });
+                ));
             }
             other => {
                 unreachable!(
@@ -2555,8 +2554,7 @@ impl Elaborator<'_> {
         if !is_current_func_constrained {
             // Check if we're calling verify_proof_with_type in an unconstrained context
             self.run_lint(|elaborator| {
-                lints::error_if_verify_proof_with_type(elaborator.interner, call.func)
-                    .map(Into::into)
+                lints::error_if_verify_proof_with_type(elaborator.interner, call.func, location)
             });
         }
 
@@ -2567,8 +2565,14 @@ impl Elaborator<'_> {
                 false
             };
 
-        let is_unconstrained_call =
-            func_type_is_unconstrained || self.is_unconstrained_call(call.func);
+        let func_is_unconstrained_call = match self.is_unconstrained_call(call.func, location) {
+            Ok(result) => result,
+            Err(error) => {
+                self.push_err(error);
+                false
+            }
+        };
+        let is_unconstrained_call = func_type_is_unconstrained || func_is_unconstrained_call;
         let crossing_runtime_boundary = is_current_func_constrained && is_unconstrained_call;
 
         if crossing_runtime_boundary {
@@ -2599,11 +2603,16 @@ impl Elaborator<'_> {
     }
 
     /// Check if the callee is an unconstrained function, or a variable referring to one.
-    fn is_unconstrained_call(&self, expr: ExprId) -> bool {
-        if let Some(func_id) = self.interner.lookup_function_from_expr(&expr) {
-            self.interner.function_meta(&func_id).is_unconstrained()
+    fn is_unconstrained_call(
+        &self,
+        expr: ExprId,
+        location: Location,
+    ) -> Result<bool, CompilationError> {
+        if let Some(func_id) = self.interner.lookup_function_from_expr(&expr, location)? {
+            let meta = self.interner.function_meta(&func_id);
+            Ok(meta.is_unconstrained())
         } else {
-            false
+            Ok(false)
         }
     }
 
```

### compiler/noirc_frontend/src/elaborator/variable.rs
```diff
@@ -151,7 +151,7 @@ impl Elaborator<'_> {
                 let message = format!(
                     "elaborate_variable_inner: unused resolved_turbofish: {unused_resolved_turbofish:?}"
                 );
-                self.push_err(TypeCheckError::ExpectingOtherError { message, location });
+                self.push_err(TypeCheckError::expecting_other_error(message, location));
             }
 
             None
@@ -620,6 +620,21 @@ impl Elaborator<'_> {
             );
         }
 
+        // If a global variable hasn't been defined yet, then we are most likely dealing with a self-dependency-cycle.
+        let definition = self.interner.definition(ident.id);
+        // Some associated constants also have Global as Kind, and they are not defined when look them up here; want to restrict to global `let` statements.
+        if self.in_comptime_context()
+            && definition.kind.is_global()
+            && self.interner.try_definition_type(ident.id).is_none()
+        {
+            self.push_err(ResolverError::DependencyCycle {
+                location: ident.location,
+                item: definition.name.clone(),
+                cycle: "the variable definition type hasn't been resolved yet".to_string(),
+            });
+            return Type::Error;
+        }
+
         // An identifiers type may be forall-quantified in the case of generic functions.
         // E.g. `fn foo<T>(t: T, field: Field) -> T` has type `forall T. fn(T, Field) -> T`.
         // We must instantiate identifiers at every call site to replace this T with a new type
```

### compiler/noirc_frontend/src/hir/comptime/errors.rs
```diff
@@ -6,7 +6,7 @@ use crate::{
     ast::{Ident, TraitBound},
     hir::{
         def_collector::dc_crate::CompilationError,
-        type_check::{NoMatchingImplFoundError, TypeCheckError},
+        type_check::{ExpectingOtherError, NoMatchingImplFoundError, TypeCheckError},
     },
     parser::ParserError,
     signed_field::SignedField,
@@ -307,6 +307,7 @@ pub enum InterpreterError {
     TraitImplResolutionRecursionLimitReached {
         location: Location,
     },
+    ExpectingOtherError(ExpectingOtherError),
     CannotModifyExternalItem {
         item: String,
         module: String,
@@ -419,6 +420,7 @@ impl InterpreterError {
             | InterpreterError::AttributeRecursionLimitExceeded { location }
             | InterpreterError::CannotCastNumericToBool { location, .. }
             | InterpreterError::CannotModifyExternalItem { location, .. } => *location,
+            InterpreterError::ExpectingOtherError(error) => error.location,
             InterpreterError::FailedToParseMacro { error, .. } => error.location(),
             InterpreterError::NoMatchingImplFound { error } => error.location,
             InterpreterError::DuplicateStructFieldInSetFields { name, .. } => name.location(),
@@ -443,6 +445,17 @@ impl InterpreterError {
         );
         InterpreterError::DebugEvaluateComptime { diagnostic, location }
     }
+
+    /// An error which is only shown to the user if there are no other errors emitted.
+    pub(crate) fn expecting_other_error<S: Into<String>>(
+        message: S,
+        location: Location,
+    ) -> InterpreterError {
+        InterpreterError::ExpectingOtherError(ExpectingOtherError {
+            message: message.into(),
+            location,
+        })
+    }
 }
 
 impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
@@ -880,6 +893,7 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
                 let secondary = String::new();
                 CustomDiagnostic::simple_warning(primary, secondary, *location)
             }
+            InterpreterError::ExpectingOtherError(error) => error.into(),
             InterpreterError::CannotModifyExternalItem { item, module, location } => {
                 let primary = "Cannot mutate something from an external crate".to_string();
                 let secondary = format!("`{item}` was declared in `{module}`");
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/builtin.rs
```diff
@@ -1419,7 +1419,7 @@ fn typed_expr_as_function_definition(
     let self_argument = check_one_argument(arguments, location)?;
     let typed_expr = get_typed_expr(self_argument)?;
     let option_value = if let TypedExpr::ExprId(expr_id) = typed_expr {
-        let func_id = interner.lookup_function_from_expr(&expr_id);
+        let func_id = interner.lookup_function_from_expr(&expr_id, location)?;
         func_id.map(Value::FunctionDefinition)
     } else {
         None
```

### compiler/noirc_frontend/src/hir/def_collector/dc_crate.rs
```diff
@@ -5,7 +5,7 @@ use crate::graph::CrateId;
 use crate::hir::comptime::{ComptimeError, InterpreterError};
 use crate::hir::def_map::{CrateDefMap, LocalModuleId, ModuleId};
 use crate::hir::resolution::errors::ResolverError;
-use crate::hir::type_check::TypeCheckError;
+use crate::hir::type_check::{ExpectingOtherError, TypeCheckError};
 use crate::locations::ReferencesTracker;
 use crate::token::SecondaryAttribute;
 use crate::usage_tracker::UnusedItem;
@@ -32,7 +32,7 @@ use noirc_errors::{CustomDiagnostic, Location, Span};
 use fm::FileId;
 use iter_extended::vecmap;
 use rustc_hash::FxHashMap as HashMap;
-use std::collections::BTreeMap;
+use std::collections::{BTreeMap, HashSet};
 use std::fmt::Write;
 use std::ops::IndexMut;
 use std::path::PathBuf;
@@ -213,8 +213,18 @@ impl CompilationError {
         CustomDiagnostic::from(self).is_error()
     }
 
-    pub(crate) fn is_expecting_other_error_error(&self) -> bool {
-        matches!(self, CompilationError::TypeError(TypeCheckError::ExpectingOtherError { .. }))
+    pub(crate) fn is_expecting_other_error(&self) -> bool {
+        self.as_expecting_other_error().is_some()
+    }
+
+    pub(crate) fn as_expecting_other_error(&self) -> Option<&ExpectingOtherError> {
+        match self {
+            CompilationError::TypeError(TypeCheckError::ExpectingOtherError(e))
+            | CompilationError::InterpreterError(InterpreterError::ExpectingOtherError(e)) => {
+                Some(e)
+            }
+            _ => None,
+        }
     }
 
     pub(crate) fn should_be_filtered(&self) -> bool {
@@ -375,10 +385,7 @@ impl DefCollector {
 
         Self::check_unused_items(context, crate_id, &mut errors);
 
-        if errors.iter().any(|error| !error.is_expecting_other_error_error()) {
-            errors.retain(|error| !error.is_expecting_other_error_error());
-        }
-        errors
+        filter_expecting_other_errors(errors)
     }
 
     /// This method does several things:
@@ -712,3 +719,35 @@ fn inject_prelude(
         }
     }
 }
+
+/// Filter the errors so that:
+/// * if we have any errors which are _not_ [ExpectingOtherError], then we remove all [ExpectingOtherError] instances
+/// * if there are no other kind of errors, then we leave and deduplicate the [ExpectingOtherError]s
+fn filter_expecting_other_errors(mut errors: Vec<CompilationError>) -> Vec<CompilationError> {
+    let has_expected_errors =
+        errors.iter().any(|error| !error.is_expecting_other_error() && error.is_error());
+
+    if has_expected_errors {
+        errors.retain(|error| !error.is_expecting_other_error());
+        errors
+    } else {
+        dedup_expecting_other_errors(errors)
+    }
+}
+
+/// The same `ExpectingOtherError` can be emitted multiple times.
+/// This function removes duplicates so we don't see the same error
+/// in the output repeatedly.
+fn dedup_expecting_other_errors(mut errors: Vec<CompilationError>) -> Vec<CompilationError> {
+    // Using a HashSet of the inner error, because CompilationError does not implement Ord or Hash.
+    let mut seen: HashSet<ExpectingOtherError> = HashSet::new();
+    errors.retain(|error| match error.as_expecting_other_error() {
+        Some(e) if seen.contains(e) => false,
+        Some(e) => {
+            seen.insert(e.clone());
+            true
+        }
+        None => true,
+    });
+    errors
+}
```

### compiler/noirc_frontend/src/hir/type_check/errors.rs
```diff
@@ -261,12 +261,26 @@ pub enum TypeCheckError {
     },
     #[error("Type annotation needed on array literal")]
     TypeAnnotationNeededOnArrayLiteral { is_array: bool, location: Location },
-    #[error("Expecting another error: {message}")]
-    ExpectingOtherError { message: String, location: Location },
+    #[error("Expecting another error: {}", (.0).message)]
+    ExpectingOtherError(ExpectingOtherError),
     #[error("Cannot call `std::verify_proof_with_type` in unconstrained context")]
     VerifyProofWithTypeInBrillig { location: Location },
 }
 
+/// An error which is only shown to the user if there are no other errors emitted.
+#[derive(Debug, Clone, PartialEq, Eq, Hash)]
+pub struct ExpectingOtherError {
+    pub message: String,
+    pub location: Location,
+}
+
+impl<'a> From<&'a ExpectingOtherError> for Diagnostic {
+    fn from(error: &'a ExpectingOtherError) -> Self {
+        let secondary = "".to_string();
+        Diagnostic::simple_error(error.message.to_string(), secondary, error.location)
+    }
+}
+
 #[derive(Debug, Clone, PartialEq, Eq)]
 pub struct NoMatchingImplFoundError {
     pub(crate) constraints: Vec<(Type, String)>,
@@ -359,8 +373,8 @@ impl TypeCheckError {
             | TypeCheckError::TupleMismatch { location, .. }
             | TypeCheckError::TypeAnnotationNeededOnItem { location, .. }
             | TypeCheckError::TypeAnnotationNeededOnArrayLiteral { location, .. }
-            | TypeCheckError::ExpectingOtherError { location, .. }
             | TypeCheckError::VerifyProofWithTypeInBrillig { location } => *location,
+            TypeCheckError::ExpectingOtherError(error) => error.location,
             TypeCheckError::DuplicateNamedTypeArg { name: ident, .. }
             | TypeCheckError::NoSuchNamedTypeArg { name: ident, .. } => ident.location(),
 
@@ -371,6 +385,17 @@ impl TypeCheckError {
             TypeCheckError::ResolverError(resolver_error) => resolver_error.location(),
         }
     }
+
+    /// An error which is only shown to the user if there are no other errors emitted.
+    pub(crate) fn expecting_other_error<S: Into<String>>(
+        message: S,
+        location: Location,
+    ) -> TypeCheckError {
+        TypeCheckError::ExpectingOtherError(ExpectingOtherError {
+            message: message.into(),
+            location,
+        })
+    }
 }
 
 impl<'a> From<&'a TypeCheckError> for Diagnostic {
@@ -802,10 +827,7 @@ impl<'a> From<&'a TypeCheckError> for Diagnostic {
                 let secondary = format!("Could not determine the type of the {array_or_vector}");
                 Diagnostic::simple_error(message, secondary, *location)
             }
-            TypeCheckError::ExpectingOtherError { message, location } => {
-                let secondary = "".to_string();
-                Diagnostic::simple_error(message.to_string(), secondary, *location)
-            }
+            TypeCheckError::ExpectingOtherError(error) => error.into()
         }
     }
 }
```

### compiler/noirc_frontend/src/hir/type_check/mod.rs
```diff
@@ -2,4 +2,6 @@ mod errors;
 pub mod generics;
 
 pub use self::errors::Source;
-pub use errors::{MAX_MISSING_CASES, NoMatchingImplFoundError, TypeCheckError};
+pub use errors::{
+    ExpectingOtherError, MAX_MISSING_CASES, NoMatchingImplFoundError, TypeCheckError,
+};
```

### compiler/noirc_frontend/src/hir_def/stmt.rs
```diff
@@ -9,7 +9,7 @@ use noirc_errors::{Location, Span};
 /// the Statement AST node. Unlike the AST node, any nested nodes
 /// are referred to indirectly via ExprId or StmtId, which can be
 /// used to retrieve the relevant node via the NodeInterner.
-#[derive(Debug, Clone)]
+#[derive(Debug, Clone, PartialEq, Eq)]
 pub enum HirStatement {
     Let(HirLetStatement),
     Assign(HirAssignStatement),
@@ -24,7 +24,7 @@ pub enum HirStatement {
     Error,
 }
 
-#[derive(Debug, Clone)]
+#[derive(Debug, Clone, PartialEq, Eq)]
 pub struct HirLetStatement {
     pub pattern: HirPattern,
     pub r#type: Type,
@@ -63,7 +63,7 @@ impl HirLetStatement {
     }
 }
 
-#[derive(Debug, Clone)]
+#[derive(Debug, Clone, PartialEq, Eq)]
 pub struct HirForStatement {
     pub identifier: HirIdent,
     pub start_range: ExprId,
@@ -73,7 +73,7 @@ pub struct HirForStatement {
 }
 
 /// Corresponds to `lvalue = expression;` in the source code
-#[derive(Debug, Clone)]
+#[derive(Debug, Clone, PartialEq, Eq)]
 pub struct HirAssignStatement {
     pub lvalue: HirLValue,
     pub expression: ExprId,
```
