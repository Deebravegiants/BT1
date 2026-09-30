# [?] fix(experimental elaborator): Fix panic in the elaborator (#5082)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-05-28
Source: https://github.com/noir-lang/noir/commit/ffcb410978a362c73783fbfe5bbdc9691499609e
Type: security-commit

## Details
fix(experimental elaborator): Fix panic in the elaborator (#5082)

# Description

## Problem\*

Working towards #4594 

## Summary\*

When run on a program the elaborator would always panic previously due
to `FuncMeta`s not yet being set for other functions while one function
was being elaborated. This is because we used to set them during name
resolution and only check them during type checking, but now that these
two passes are merged we'll need to set them all before elaboration
instead.

This PR creates a new `define_function_metas` function to create the
`FuncMeta`s beforehand. I imagine there are more changes required here
related to scoping / generics / parameters but this at least stops the
panic.

## Additional Context

This is the first of the elaborator PRs to feature only new changes
rather than largely copied code, so feel free to critique as usual if
you think a different approach would be better, notice an issue, etc.

After this PR the elaborator will run on a small example program, only
producing 1052 errors in the standard library :slightly_smiling_face:.
Most of these errors appear to be variants of "no method named '...'
found for ..." and "no matching impl found for ..."

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

---------

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>
Co-authored-by: Maxim Vezenov <mvezenov@gmail.com>

## Patch
### compiler/noirc_frontend/src/elaborator/expressions.rs
```diff
@@ -15,9 +15,9 @@ use crate::{
     hir_def::{
         expr::{
             HirArrayLiteral, HirBinaryOp, HirBlockExpression, HirCallExpression, HirCastExpression,
-            HirConstructorExpression, HirIdent, HirIfExpression, HirIndexExpression,
-            HirInfixExpression, HirLambda, HirMemberAccess, HirMethodCallExpression,
-            HirMethodReference, HirPrefixExpression,
+            HirConstructorExpression, HirIfExpression, HirIndexExpression, HirInfixExpression,
+            HirLambda, HirMemberAccess, HirMethodCallExpression, HirMethodReference,
+            HirPrefixExpression,
         },
         traits::TraitConstraint,
     },
@@ -84,10 +84,10 @@ impl<'context> Elaborator<'context> {
                     expr_type: inner_expr_type.clone(),
                     expr_span: span,
                 });
+            }
 
-                if i + 1 == statements.len() {
-                    block_type = stmt_type;
-                }
+            if i + 1 == statements.len() {
+                block_type = stmt_type;
             }
         }
 
```

### compiler/noirc_frontend/src/elaborator/mod.rs
```diff
@@ -1,58 +1,37 @@
-#![allow(unused)]
 use std::{
     collections::{BTreeMap, BTreeSet},
     rc::Rc,
 };
 
 use crate::{
-    ast::{
-        ArrayLiteral, ConstructorExpression, FunctionKind, IfExpression, InfixExpression, Lambda,
-        UnresolvedTraitConstraint, UnresolvedTypeExpression,
-    },
+    ast::{FunctionKind, UnresolvedTraitConstraint},
     hir::{
         def_collector::{
             dc_crate::{
-                filter_literal_globals, CompilationError, UnresolvedGlobal, UnresolvedStruct,
-                UnresolvedTrait, UnresolvedTypeAlias,
+                filter_literal_globals, CompilationError, ImplMap, UnresolvedGlobal,
+                UnresolvedStruct, UnresolvedTypeAlias,
             },
             errors::DuplicateType,
         },
         resolution::{errors::ResolverError, path_resolver::PathResolver, resolver::LambdaContext},
         scope::ScopeForest as GenericScopeForest,
         type_check::TypeCheckError,
     },
-    hir_def::{
-        expr::{
-            HirArrayLiteral, HirBinaryOp, HirBlockExpression, HirCallExpression, HirCastExpression,
-            HirConstructorExpression, HirIdent, HirIfExpression, HirIndexExpression,
-            HirInfixExpression, HirLambda, HirMemberAccess, HirMethodCallExpression,
-            HirMethodReference, HirPrefixExpression,
-        },
-        stmt::HirLetStatement,
-        traits::TraitConstraint,
-    },
+    hir_def::{expr::HirIdent, function::Parameters, traits::TraitConstraint},
     macros_api::{
-        BlockExpression, CallExpression, CastExpression, Expression, ExpressionKind, HirExpression,
-        HirLiteral, HirStatement, Ident, IndexExpression, Literal, MemberAccessExpression,
-        MethodCallExpression, NodeInterner, NoirFunction, NoirStruct, Pattern, PrefixExpression,
-        SecondaryAttribute, Statement, StatementKind, StructId,
+        Ident, NodeInterner, NoirFunction, NoirStruct, Pattern, SecondaryAttribute, StructId,
     },
-    node_interner::{DefinitionKind, DependencyId, ExprId, FuncId, StmtId, TraitId, TypeAliasId},
-    Shared, StructType, Type, TypeVariable,
+    node_interner::{DefinitionKind, DependencyId, ExprId, FuncId, TraitId, TypeAliasId},
+    Shared, Type, TypeVariable,
 };
 use crate::{
     ast::{TraitBound, UnresolvedGenerics},
     graph::CrateId,
     hir::{
-        def_collector::{
-            dc_crate::{CollectedItems, DefCollector},
-            errors::DefCollectorErrorKind,
-        },
+        def_collector::{dc_crate::CollectedItems, errors::DefCollectorErrorKind},
         def_map::{LocalModuleId, ModuleDefId, ModuleId, MAIN_FUNCTION},
         resolution::{
-            errors::PubPosition,
-            import::{PathResolution, PathResolutionError},
-            path_resolver::StandardPathResolver,
+            errors::PubPosition, import::PathResolution, path_resolver::StandardPathResolver,
         },
         Context,
     },
@@ -81,7 +60,6 @@ mod types;
 use fm::FileId;
 use iter_extended::vecmap;
 use noirc_errors::{Location, Span};
-use regex::Regex;
 use rustc_hash::FxHashSet as HashSet;
 
 /// ResolverMetas are tagged onto each definition to track how many times they are used
@@ -226,6 +204,8 @@ impl<'context> Elaborator<'context> {
             this.define_type_alias(alias_id, alias);
         }
 
+        this.define_function_metas(&mut items.functions, &mut items.impls, &mut items.trait_impls);
+
         this.collect_traits(items.traits);
 
         // Must resolve structs before we resolve globals.
@@ -268,7 +248,6 @@ impl<'context> Elaborator<'context> {
 
         let cycle_errors = this.interner.check_for_dependency_cycles();
         this.errors.extend(cycle_errors);
-
         this.errors
     }
 
@@ -285,7 +264,6 @@ impl<'context> Elaborator<'context> {
 
     fn elaborate_function(&mut self, mut function: NoirFunction, id: FuncId) {
         self.current_function = Some(id);
-        self.resolve_where_clause(&mut function.def.where_clause);
 
         // Without this, impl methods can accidentally be placed in contracts. See #3254
         if self.self_type.is_some() {
@@ -297,9 +275,6 @@ impl<'context> Elaborator<'context> {
 
         // Check whether the function has globals in the local module and add them to the scope
         self.resolve_local_globals();
-        self.add_generics(&function.def.generics);
-
-        self.desugar_impl_trait_args(&mut function, id);
         self.trait_bounds = function.def.where_clause.clone();
 
         let is_low_level_or_oracle = function
@@ -312,8 +287,19 @@ impl<'context> Elaborator<'context> {
             self.in_unconstrained_fn = true;
         }
 
-        let func_meta = self.extract_meta(&function, id);
+        let func_meta = self.interner.func_meta.get(&id);
+        let func_meta = func_meta
+            .expect("FuncMetas should be declared before a function is elaborated")
+            .clone();
 
+        for (parameter, param2) in function.def.parameters.iter().zip(&func_meta.parameters.0) {
+            let definition_kind = DefinitionKind::Local(None);
+            self.elaborate_pattern(parameter.pattern.clone(), param2.1.clone(), definition_kind);
+        }
+
+        self.add_generics(&function.def.generics);
+        self.desugar_impl_trait_args(&mut function, id);
+        self.declare_numeric_generics(&func_meta.parameters, func_meta.return_type());
         self.add_trait_constraints_to_scope(&func_meta);
 
         let (hir_func, body_type) = match function.kind {
@@ -376,7 +362,6 @@ impl<'context> Elaborator<'context> {
 
         self.trait_bounds.clear();
 
-        self.interner.push_fn_meta(func_meta, id);
         self.interner.update_fn(id, hir_func);
         self.current_function = None;
     }
@@ -538,9 +523,23 @@ impl<'context> Elaborator<'context> {
 
     /// Extract metadata from a NoirFunction
     /// to be used in analysis and intern the function parameters
-    /// Prerequisite: self.add_generics() has already been called with the given
-    /// function's generics, including any generics from the impl, if any.
-    fn extract_meta(&mut self, func: &NoirFunction, func_id: FuncId) -> FuncMeta {
+    /// Prerequisite: any implicit generics, including any generics from the impl,
+    /// have already been added to scope via `self.add_generics`.
+    fn define_function_meta(&mut self, func: &mut NoirFunction, func_id: FuncId) {
+        self.current_function = Some(func_id);
+        self.resolve_where_clause(&mut func.def.where_clause);
+
+        // Without this, impl methods can accidentally be placed in contracts. See #3254
+        if self.self_type.is_some() {
+            self.in_contract = false;
+        }
+
+        self.scopes.start_function();
+        self.current_item = Some(DependencyId::Function(func_id));
+
+        // Check whether the function has globals in the local module and add them to the scope
+        self.resolve_local_globals();
+
         let location = Location::new(func.name_ident().span(), self.file);
         let id = self.interner.function_definition_id(func_id);
         let name_ident = HirIdent::non_trait_method(id, location);
@@ -565,6 +564,8 @@ impl<'context> Elaborator<'context> {
         let has_inline_attribute = has_no_predicates_attribute || should_fold;
         let is_entry_point = self.is_entry_point_function(func);
 
+        self.add_generics(&func.def.generics);
+
         let mut generics = vecmap(&self.generics, |(_, typevar, _)| typevar.clone());
         let mut parameters = vec![];
         let mut parameter_types = vec![];
@@ -593,8 +594,6 @@ impl<'context> Elaborator<'context> {
 
         let return_type = Box::new(self.resolve_type(func.return_type()));
 
-        self.declare_numeric_generics(&parameter_types, &return_type);
-
         if !self.pub_allowed(func) && func.def.return_visibility == Visibility::Public {
             self.push_err(ResolverError::UnnecessaryPub {
                 ident: func.name_ident().clone(),
@@ -647,7 +646,7 @@ impl<'context> Elaborator<'context> {
             .map(|(name, typevar, _span)| (name.clone(), typevar.clone()))
             .collect();
 
-        FuncMeta {
+        let meta = FuncMeta {
             name: name_ident,
             kind: func.kind,
             location,
@@ -661,7 +660,12 @@ impl<'context> Elaborator<'context> {
             trait_constraints: self.resolve_trait_constraints(&func.def.where_clause),
             is_entry_point,
             has_inline_attribute,
-        }
+        };
+
+        self.interner.push_fn_meta(meta, func_id);
+        self.current_function = None;
+        self.scopes.end_function();
+        self.current_item = None;
     }
 
     /// Only sized types are valid to be used as main's parameters or the parameters to a contract
@@ -701,7 +705,7 @@ impl<'context> Elaborator<'context> {
         }
     }
 
-    fn declare_numeric_generics(&mut self, params: &[Type], return_type: &Type) {
+    fn declare_numeric_generics(&mut self, params: &Parameters, return_type: &Type) {
         if self.generics.is_empty() {
             return;
         }
@@ -724,11 +728,11 @@ impl<'context> Elaborator<'context> {
     }
 
     fn find_numeric_generics(
-        parameters: &[Type],
+        parameters: &Parameters,
         return_type: &Type,
     ) -> Vec<(String, TypeVariable)> {
         let mut found = BTreeMap::new();
-        for parameter in parameters {
+        for (_, parameter, _) in &parameters.0 {
             Self::find_numeric_generics_in_type(parameter, &mut found);
         }
         Self::find_numeric_generics_in_type(return_type, &mut found);
@@ -842,10 +846,11 @@ impl<'context> Elaborator<'context> {
         module: LocalModuleId,
         impls: Vec<(Vec<Ident>, Span, UnresolvedFunctions)>,
     ) {
-        self.generics.clear();
+        self.local_module = module;
 
         for (generics, _, functions) in impls {
             self.file = functions.file_id;
+            let old_generics_length = self.generics.len();
             self.add_generics(&generics);
             let self_type = self.resolve_type(typ.clone());
             self.self_type = Some(self_type.clone());
@@ -869,6 +874,8 @@ impl<'context> Elaborator<'context> {
                     }
                 }
             }
+
+            self.generics.truncate(old_generics_length);
         }
     }
 
@@ -878,18 +885,20 @@ impl<'context> Elaborator<'context> {
 
         let unresolved_type = trait_impl.object_type;
         let self_type_span = unresolved_type.span;
+        let old_generics_length = self.generics.len();
         self.add_generics(&trait_impl.generics);
 
         let trait_generics =
             vecmap(&trait_impl.trait_generics, |generic| self.resolve_type(generic.clone()));
 
-        let self_type = self.resolve_type(unresolved_type.clone());
-        let impl_id = self.interner.next_trait_impl_id();
+        let self_type = trait_impl.resolved_object_type.unwrap_or(Type::Error);
+        let impl_id =
+            trait_impl.impl_id.expect("An impls' id should be set during define_function_metas");
 
         self.self_type = Some(self_type.clone());
-        self.current_trait_impl = Some(impl_id);
+        self.current_trait_impl = trait_impl.impl_id;
 
-        let mut methods = trait_impl.methods.function_ids();
+        let methods = trait_impl.methods.function_ids();
 
         self.elaborate_functions(trait_impl.methods);
 
@@ -944,7 +953,7 @@ impl<'context> Elaborator<'context> {
 
         self.self_type = None;
         self.current_trait_impl = None;
-        self.generics.clear();
+        self.generics.truncate(old_generics_length);
     }
 
     fn collect_impls(
@@ -1236,4 +1245,55 @@ impl<'context> Elaborator<'context> {
         self.interner.get_global_definition_mut(global_id).kind = definition_kind;
         self.interner.replace_statement(statement_id, let_statement);
     }
+
+    fn define_function_metas(
+        &mut self,
+        functions: &mut [UnresolvedFunctions],
+        impls: &mut ImplMap,
+        trait_impls: &mut [UnresolvedTraitImpl],
+    ) {
+        for function_set in functions {
+            self.define_function_metas_for_functions(function_set);
+        }
+
+        for ((_typ, local_module), function_sets) in impls {
+            self.local_module = *local_module;
+
+            for (_generics, _, function_set) in function_sets {
+                self.define_function_metas_for_functions(function_set);
+            }
+        }
+
+        for trait_impl in trait_impls {
+            self.file = trait_impl.file_id;
+            self.local_module = trait_impl.module_id;
+
+            let unresolved_type = &trait_impl.object_type;
+            let old_generics_length = self.generics.len();
+            self.add_generics(&trait_impl.generics);
+
+            let self_type = self.resolve_type(unresolved_type.clone());
+            self.self_type = Some(self_type.clone());
+
+            let impl_id = self.interner.next_trait_impl_id();
+            self.current_trait_impl = Some(impl_id);
+
+            self.define_function_metas_for_functions(&mut trait_impl.methods);
+
+            trait_impl.resolved_object_type = self.self_type.take();
+            trait_impl.impl_id = self.current_trait_impl.take();
+            self.generics.truncate(old_generics_length);
+        }
+    }
+
+    fn define_function_metas_for_functions(&mut self, function_set: &mut UnresolvedFunctions) {
+        self.file = function_set.file_id;
+
+        for (local_module, id, func) in &mut function_set.functions {
+            self.local_module = *local_module;
+            let old_generics_length = self.generics.len();
+            self.define_function_meta(func, *id);
+            self.generics.truncate(old_generics_length);
+        }
+    }
 }
```

### compiler/noirc_frontend/src/elaborator/scope.rs
```diff
@@ -1,8 +1,6 @@
 use noirc_errors::Spanned;
-use rustc_hash::FxHashMap as HashMap;
 
 use crate::ast::ERROR_IDENT;
-use crate::hir::comptime::Value;
 use crate::hir::def_map::{LocalModuleId, ModuleId};
 use crate::hir::resolution::path_resolver::{PathResolver, StandardPathResolver};
 use crate::hir::resolution::resolver::SELF_TYPE_NAME;
@@ -18,7 +16,7 @@ use crate::{
         traits::Trait,
     },
     macros_api::{Path, StructId},
-    node_interner::{DefinitionId, TraitId, TypeAliasId},
+    node_interner::{DefinitionId, TraitId},
     Shared, StructType,
 };
 use crate::{Type, TypeAlias};
```

### compiler/noirc_frontend/src/elaborator/traits.rs
```diff
@@ -5,14 +5,8 @@ use noirc_errors::Location;
 
 use crate::{
     ast::{FunctionKind, TraitItem, UnresolvedGenerics, UnresolvedTraitConstraint},
-    hir::{
-        def_collector::dc_crate::UnresolvedTrait, def_map::ModuleId,
-        resolution::path_resolver::StandardPathResolver,
-    },
-    hir_def::{
-        function::{FuncMeta, HirFunction},
-        traits::{TraitConstant, TraitFunction, TraitType},
-    },
+    hir::def_collector::dc_crate::UnresolvedTrait,
+    hir_def::traits::{TraitConstant, TraitFunction, TraitType},
     macros_api::{
         BlockExpression, FunctionDefinition, FunctionReturnType, Ident, ItemVisibility,
         NoirFunction, Param, Pattern, UnresolvedType, Visibility,
@@ -26,10 +20,6 @@ use super::Elaborator;
 
 impl<'context> Elaborator<'context> {
     pub fn collect_traits(&mut self, traits: BTreeMap<TraitId, UnresolvedTrait>) {
-        for (trait_id, unresolved_trait) in &traits {
-            self.interner.push_empty_trait(*trait_id, unresolved_trait);
-        }
-
         for (trait_id, unresolved_trait) in traits {
             let generics = vecmap(&unresolved_trait.trait_def.generics, |_| {
                 TypeVariable::unbound(self.interner.next_type_variable_id())
@@ -187,7 +177,9 @@ impl<'context> Elaborator<'context> {
             return_visibility: Visibility::Private,
         };
 
-        self.elaborate_function(NoirFunction { kind, def }, func_id);
+        let mut function = NoirFunction { kind, def };
+        self.define_function_meta(&mut function, func_id);
+        self.elaborate_function(function, func_id);
         let _ = self.scopes.end_function();
         // Don't check the scope tree for unused variables, they can't be used in a declaration anyway.
         self.trait_bounds.clear();
```

### compiler/noirc_frontend/src/elaborator/types.rs
```diff
@@ -1,19 +1,18 @@
 use std::rc::Rc;
 
-use acvm::{acir::AcirField, FieldElement};
+use acvm::acir::AcirField;
 use iter_extended::vecmap;
 use noirc_errors::{Location, Span};
 
 use crate::{
     ast::{
-        BinaryOpKind, IntegerBitSize, NoirTypeAlias, UnresolvedGenerics, UnresolvedTraitConstraint,
+        BinaryOpKind, IntegerBitSize, UnresolvedGenerics, UnresolvedTraitConstraint,
         UnresolvedTypeExpression,
     },
     hir::{
         def_map::ModuleDefId,
         resolution::{
             errors::ResolverError,
-            import::PathResolution,
             resolver::{verify_mutable_reference, SELF_TYPE_NAME},
         },
         type_check::{Source, TypeCheckError},
@@ -24,17 +23,14 @@ use crate::{
             HirPrefixExpression,
         },
         function::FuncMeta,
-        traits::{Trait, TraitConstraint},
+        traits::TraitConstraint,
     },
     macros_api::{
         HirExpression, HirLiteral, HirStatement, Path, PathKind, SecondaryAttribute, Signedness,
         UnaryOp, UnresolvedType, UnresolvedTypeData,
     },
-    node_interner::{
-        DefinitionKind, DependencyId, ExprId, GlobalId, TraitId, TraitImplKind, TraitMethodId,
-        TypeAliasId,
-    },
-    Generics, Shared, StructType, Type, TypeAlias, TypeBinding, TypeVariable, TypeVariableKind,
+    node_interner::{DefinitionKind, ExprId, GlobalId, TraitId, TraitImplKind, TraitMethodId},
+    Generics, Type, TypeBinding, TypeVariable, TypeVariableKind,
 };
 
 use super::Elaborator;
@@ -636,7 +632,7 @@ impl<'context> Elaborator<'context> {
         rhs_type: &Type,
         span: Span,
     ) -> Type {
-        let mut unify = |this: &mut Self, expected| {
+        let unify = |this: &mut Self, expected| {
             this.unify(rhs_type, &expected, || TypeCheckError::TypeMismatch {
                 expr_typ: rhs_type.to_string(),
                 expected_typ: expected.to_string(),
```

### compiler/noirc_frontend/src/hir/def_collector/dc_crate.rs
```diff
@@ -5,6 +5,7 @@ use crate::graph::CrateId;
 use crate::hir::comptime::{Interpreter, InterpreterError};
 use crate::hir::def_map::{CrateDefMap, LocalModuleId, ModuleId};
 use crate::hir::resolution::errors::ResolverError;
+use crate::Type;
 
 use crate::hir::resolution::import::{resolve_import, ImportDirective, PathResolution};
 use crate::hir::resolution::{
@@ -18,7 +19,9 @@ use crate::hir::type_check::{
 use crate::hir::Context;
 
 use crate::macros_api::{MacroError, MacroProcessor};
-use crate::node_interner::{FuncId, GlobalId, NodeInterner, StructId, TraitId, TypeAliasId};
+use crate::node_interner::{
+    FuncId, GlobalId, NodeInterner, StructId, TraitId, TraitImplId, TypeAliasId,
+};
 
 use crate::ast::{
     ExpressionKind, Ident, LetStatement, Literal, NoirFunction, NoirStruct, NoirTrait,
@@ -107,13 +110,17 @@ pub struct UnresolvedTrait {
 pub struct UnresolvedTraitImpl {
     pub file_id: FileId,
     pub module_id: LocalModuleId,
-    pub trait_id: Option<TraitId>,
     pub trait_generics: Vec<UnresolvedType>,
     pub trait_path: Path,
     pub object_type: UnresolvedType,
     pub methods: UnresolvedFunctions,
     pub generics: UnresolvedGenerics,
     pub where_clause: Vec<UnresolvedTraitConstraint>,
+
+    // These fields are filled in later during elaboration
+    pub trait_id: Option<TraitId>,
+    pub impl_id: Option<TraitImplId>,
+    pub resolved_object_type: Option<Type>,
 }
 
 #[derive(Clone)]
@@ -337,7 +344,7 @@ impl DefCollector {
 
         if use_elaborator {
             let mut more_errors = Elaborator::elaborate(context, crate_id, def_collector.items);
-            more_errors.append(&mut errors);
+            errors.append(&mut more_errors);
             return errors;
         }
 
```

### compiler/noirc_frontend/src/hir/def_collector/dc_mod.rs
```diff
@@ -189,8 +189,12 @@ impl<'a> ModCollector<'a> {
                 object_type: trait_impl.object_type,
                 generics: trait_impl.impl_generics,
                 where_clause: trait_impl.where_clause,
-                trait_id: None, // will be filled later
                 trait_generics: trait_impl.trait_generics,
+
+                // These last fields are filled later on
+                trait_id: None,
+                impl_id: None,
+                resolved_object_type: None,
             };
 
             self.def_collector.items.trait_impls.push(unresolved_trait_impl);
@@ -509,6 +513,7 @@ impl<'a> ModCollector<'a> {
                 method_ids,
                 fns_with_default_impl: unresolved_functions,
             };
+            context.def_interner.push_empty_trait(trait_id, &unresolved);
             self.def_collector.items.traits.insert(trait_id, unresolved);
         }
         errors
```

### compiler/noirc_frontend/src/node_interner.rs
```diff
@@ -111,7 +111,9 @@ pub struct NodeInterner {
     // The purpose for this hashmap is to detect duplication of trait implementations ( if any )
     //
     // Indexed by TraitImplIds
-    pub(crate) trait_implementations: Vec<Shared<TraitImpl>>,
+    pub(crate) trait_implementations: HashMap<TraitImplId, Shared<TraitImpl>>,
+
+    next_trait_implementation_id: usize,
 
     /// Trait implementations on each type. This is expected to always have the same length as
     /// `self.trait_implementations`.
@@ -485,7 +487,8 @@ impl Default for NodeInterner {
             struct_attributes: HashMap::new(),
             type_aliases: Vec::new(),
             traits: HashMap::new(),
-            trait_implementations: Vec::new(),
+            trait_implementations: HashMap::new(),
+            next_trait_implementation_id: 0,
             trait_implementation_map: HashMap::new(),
             selected_trait_implementations: HashMap::new(),
             operator_traits: HashMap::new(),
@@ -1143,7 +1146,7 @@ impl NodeInterner {
     }
 
     pub fn get_trait_implementation(&self, id: TraitImplId) -> Shared<TraitImpl> {
-        self.trait_implementations[id.0].clone()
+        self.trait_implementations[&id].clone()
     }
 
     /// Given a `ObjectType: TraitId` pair, try to find an existing impl that satisfies the
@@ -1378,9 +1381,7 @@ impl NodeInterner {
         impl_generics: Generics,
         trait_impl: Shared<TraitImpl>,
     ) -> Result<(), (Span, FileId)> {
-        assert_eq!(impl_id.0, self.trait_implementations.len(), "trait impl defined out of order");
-
-        self.trait_implementations.push(trait_impl.clone());
+        self.trait_implementations.insert(impl_id, trait_impl.clone());
 
         // Replace each generic with a fresh type variable
         let substitutions = impl_generics
@@ -1483,10 +1484,10 @@ impl NodeInterner {
     }
 
     /// Returns what the next trait impl id is expected to be.
-    /// Note that this does not actually reserve the slot so care should
-    /// be taken that the next trait impl added matches this ID.
-    pub fn next_trait_impl_id(&self) -> TraitImplId {
-        TraitImplId(self.trait_implementations.len())
+    pub fn next_trait_impl_id(&mut self) -> TraitImplId {
+        let next_id = self.next_trait_implementation_id;
+        self.next_trait_implementation_id += 1;
+        TraitImplId(next_id)
     }
 
     /// Removes all TraitImplKind::Assumed from the list of known impls for the given trait
```

### compiler/noirc_frontend/src/resolve_locations.rs
```diff
@@ -157,11 +157,11 @@ impl NodeInterner {
         self.trait_implementations
             .iter()
             .find(|shared_trait_impl| {
-                let trait_impl = shared_trait_impl.borrow();
+                let trait_impl = shared_trait_impl.1.borrow();
                 trait_impl.file == location.file && trait_impl.ident.span().contains(&location.span)
             })
             .and_then(|shared_trait_impl| {
-                let trait_impl = shared_trait_impl.borrow();
+                let trait_impl = shared_trait_impl.1.borrow();
                 self.traits.get(&trait_impl.trait_id).map(|trait_| trait_.location)
             })
     }
```
