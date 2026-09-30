# [?] Prevent an illegal use of a generic from crashing the compiler (#3277)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-11-07
Source: https://github.com/FuelLabs/sway/commit/1b8a7df8cc22ea4240a2b1728853df5a90d42d17
Type: security-commit

## Details
Prevent an illegal use of a generic from crashing the compiler (#3277)

## Patch
### sway-core/src/control_flow_analysis/analyze_return_paths.rs
```diff
@@ -241,7 +241,7 @@ fn connect_declaration(
             connect_impl_trait(&trait_name, graph, &methods, entry_node)?;
             Ok(leaves.to_vec())
         }
-        ErrorRecovery => Ok(leaves.to_vec()),
+        ErrorRecovery(_) => Ok(leaves.to_vec()),
     }
 }
 
```

### sway-core/src/control_flow_analysis/dead_code_analysis.rs
```diff
@@ -369,7 +369,7 @@ fn connect_declaration(
             connect_storage_declaration(&storage, graph, entry_node, tree_type);
             Ok(leaves.to_vec())
         }
-        ErrorRecovery | GenericTypeForFunctionScope { .. } => Ok(leaves.to_vec()),
+        ErrorRecovery(_) | GenericTypeForFunctionScope { .. } => Ok(leaves.to_vec()),
     }
 }
 
```

### sway-core/src/ir_generation/compile.rs
```diff
@@ -183,7 +183,7 @@ fn compile_declarations(
             | ty::TyDeclaration::AbiDeclaration(_)
             | ty::TyDeclaration::GenericTypeForFunctionScope { .. }
             | ty::TyDeclaration::StorageDeclaration(_)
-            | ty::TyDeclaration::ErrorRecovery => (),
+            | ty::TyDeclaration::ErrorRecovery(_) => (),
         }
     }
     Ok(())
```

### sway-core/src/language/ty/declaration/declaration.rs
```diff
@@ -23,7 +23,7 @@ pub enum TyDeclaration {
     // If type parameters are defined for a function, they are put in the namespace just for
     // the body of that function.
     GenericTypeForFunctionScope { name: Ident, type_id: TypeId },
-    ErrorRecovery,
+    ErrorRecovery(Span),
     StorageDeclaration(DeclarationId),
 }
 
@@ -42,7 +42,7 @@ impl CopyTypes for TyDeclaration {
             | ConstantDeclaration(_)
             | StorageDeclaration(..)
             | GenericTypeForFunctionScope { .. }
-            | ErrorRecovery => (),
+            | ErrorRecovery(_) => (),
         }
     }
 }
@@ -62,7 +62,7 @@ impl ReplaceSelfType for TyDeclaration {
             | ConstantDeclaration(_)
             | StorageDeclaration(..)
             | GenericTypeForFunctionScope { .. }
-            | ErrorRecovery => (),
+            | ErrorRecovery(_) => (),
         }
     }
 }
@@ -80,9 +80,8 @@ impl Spanned for TyDeclaration {
             AbiDeclaration(decl_id) => decl_id.span(),
             ImplTrait(decl_id) => decl_id.span(),
             StorageDeclaration(decl) => decl.span(),
-            ErrorRecovery | GenericTypeForFunctionScope { .. } => {
-                unreachable!("No span exists for these ast node types")
-            }
+            GenericTypeForFunctionScope { name, .. } => name.span(),
+            ErrorRecovery(span) => span.clone(),
         }
     }
 }
@@ -230,7 +229,7 @@ impl CollectTypesMetadata for TyDeclaration {
                     }
                 }
             }
-            ErrorRecovery
+            ErrorRecovery(_)
             | StorageDeclaration(_)
             | TraitDeclaration(_)
             | StructDeclaration(_)
@@ -256,6 +255,7 @@ impl TyDeclaration {
             TyDeclaration::EnumDeclaration(decl_id) => {
                 CompileResult::from(de_get_enum(decl_id.clone(), access_span))
             }
+            TyDeclaration::ErrorRecovery(_) => err(vec![], vec![]),
             decl => err(
                 vec![],
                 vec![CompileError::DeclIsNotAnEnum {
@@ -282,6 +282,7 @@ impl TyDeclaration {
                 );
                 ok(decl, warnings, errors)
             }
+            TyDeclaration::ErrorRecovery(_) => err(vec![], vec![]),
             decl => {
                 errors.push(CompileError::DeclIsNotAStruct {
                     actually: decl.friendly_name().to_string(),
@@ -311,6 +312,7 @@ impl TyDeclaration {
                 );
                 ok(decl, warnings, errors)
             }
+            TyDeclaration::ErrorRecovery(_) => err(vec![], vec![]),
             decl => {
                 errors.push(CompileError::DeclIsNotAFunction {
                     actually: decl.friendly_name().to_string(),
@@ -329,6 +331,7 @@ impl TyDeclaration {
         let mut errors = vec![];
         match self {
             TyDeclaration::VariableDeclaration(decl) => ok(decl, warnings, errors),
+            TyDeclaration::ErrorRecovery(_) => err(vec![], vec![]),
             decl => {
                 errors.push(CompileError::DeclIsNotAVariable {
                     actually: decl.friendly_name().to_string(),
@@ -347,6 +350,7 @@ impl TyDeclaration {
             TyDeclaration::AbiDeclaration(decl_id) => {
                 CompileResult::from(de_get_abi(decl_id.clone(), access_span))
             }
+            TyDeclaration::ErrorRecovery(_) => err(vec![], vec![]),
             decl => err(
                 vec![],
                 vec![CompileError::DeclIsNotAnAbi {
@@ -365,6 +369,7 @@ impl TyDeclaration {
             TyDeclaration::ConstantDeclaration(decl) => {
                 CompileResult::from(de_get_constant(decl.clone(), access_span))
             }
+            TyDeclaration::ErrorRecovery(_) => err(vec![], vec![]),
             decl => {
                 let errors = vec![
                     (CompileError::DeclIsNotAConstant {
@@ -390,7 +395,7 @@ impl TyDeclaration {
             ImplTrait { .. } => "impl trait",
             AbiDeclaration(..) => "abi",
             GenericTypeForFunctionScope { .. } => "generic type parameter",
-            ErrorRecovery => "error",
+            ErrorRecovery(_) => "error",
             StorageDeclaration(_) => "contract storage declaration",
         }
     }
@@ -505,7 +510,7 @@ impl TyDeclaration {
             | ImplTrait { .. }
             | StorageDeclaration { .. }
             | AbiDeclaration(..)
-            | ErrorRecovery => Visibility::Public,
+            | ErrorRecovery(_) => Visibility::Public,
             VariableDeclaration(decl) => decl.mutability.visibility(),
         };
         ok(visibility, warnings, errors)
```

### sway-core/src/semantic_analysis/ast_node/declaration/declaration.rs
```diff
@@ -0,0 +1,300 @@
+use sway_error::warning::{CompileWarning, Warning};
+use sway_types::{style::is_screaming_snake_case, Spanned};
+
+use crate::{
+    declaration_engine::*,
+    error::*,
+    language::{parsed, ty},
+    semantic_analysis::TypeCheckContext,
+    type_system::*,
+    CompileResult,
+};
+
+impl ty::TyDeclaration {
+    pub(crate) fn type_check(
+        mut ctx: TypeCheckContext,
+        decl: parsed::Declaration,
+    ) -> CompileResult<ty::TyDeclaration> {
+        let mut warnings = vec![];
+        let mut errors = vec![];
+
+        let decl = match decl {
+            parsed::Declaration::VariableDeclaration(parsed::VariableDeclaration {
+                name,
+                type_ascription,
+                type_ascription_span,
+                body,
+                is_mutable,
+            }) => {
+                let type_ascription = check!(
+                    ctx.resolve_type_with_self(
+                        insert_type(type_ascription),
+                        &type_ascription_span.clone().unwrap_or_else(|| name.span()),
+                        EnforceTypeArguments::Yes,
+                        None
+                    ),
+                    insert_type(TypeInfo::ErrorRecovery),
+                    warnings,
+                    errors
+                );
+                let mut ctx = ctx.with_type_annotation(type_ascription).with_help_text(
+                    "Variable declaration's type annotation does not match up \
+                        with the assigned expression's type.",
+                );
+                let result = ty::TyExpression::type_check(ctx.by_ref(), body);
+                let body = check!(
+                    result,
+                    ty::TyExpression::error(name.span()),
+                    warnings,
+                    errors
+                );
+                let typed_var_decl =
+                    ty::TyDeclaration::VariableDeclaration(Box::new(ty::TyVariableDeclaration {
+                        name: name.clone(),
+                        body,
+                        mutability: ty::VariableMutability::new_from_ref_mut(false, is_mutable),
+                        type_ascription,
+                        type_ascription_span,
+                    }));
+                ctx.namespace.insert_symbol(name, typed_var_decl.clone());
+                typed_var_decl
+            }
+            parsed::Declaration::ConstantDeclaration(parsed::ConstantDeclaration {
+                name,
+                type_ascription,
+                value,
+                visibility,
+                attributes,
+                span,
+                ..
+            }) => {
+                let result = {
+                    let type_id = check!(
+                        ctx.resolve_type_with_self(
+                            insert_type(type_ascription),
+                            &span,
+                            EnforceTypeArguments::No,
+                            None
+                        ),
+                        insert_type(TypeInfo::ErrorRecovery),
+                        warnings,
+                        errors,
+                    );
+                    let ctx = ctx.by_ref().with_type_annotation(type_id).with_help_text(
+                        "This declaration's type annotation does not match up with the assigned \
+                            expression's type.",
+                    );
+                    ty::TyExpression::type_check(ctx, value)
+                };
+
+                if !is_screaming_snake_case(name.as_str()) {
+                    warnings.push(CompileWarning {
+                        span: name.span(),
+                        warning_content: Warning::NonScreamingSnakeCaseConstName {
+                            name: name.clone(),
+                        },
+                    })
+                }
+
+                let value = check!(
+                    result,
+                    ty::TyExpression::error(name.span()),
+                    warnings,
+                    errors
+                );
+                let decl = ty::TyConstantDeclaration {
+                    name: name.clone(),
+                    value,
+                    visibility,
+                    attributes,
+                    span,
+                };
+                let typed_const_decl =
+                    ty::TyDeclaration::ConstantDeclaration(de_insert_constant(decl));
+                ctx.namespace.insert_symbol(name, typed_const_decl.clone());
+                typed_const_decl
+            }
+            parsed::Declaration::EnumDeclaration(decl) => {
+                let span = decl.span.clone();
+                let enum_decl = check!(
+                    ty::TyEnumDeclaration::type_check(ctx.by_ref(), decl),
+                    return ok(ty::TyDeclaration::ErrorRecovery(span), warnings, errors),
+                    warnings,
+                    errors
+                );
+                let name = enum_decl.name.clone();
+                let decl = ty::TyDeclaration::EnumDeclaration(de_insert_enum(enum_decl));
+                check!(
+                    ctx.namespace.insert_symbol(name, decl.clone()),
+                    return err(warnings, errors),
+                    warnings,
+                    errors
+                );
+                decl
+            }
+            parsed::Declaration::FunctionDeclaration(fn_decl) => {
+                let span = fn_decl.span.clone();
+                let mut ctx = ctx.with_type_annotation(insert_type(TypeInfo::Unknown));
+                let fn_decl = check!(
+                    ty::TyFunctionDeclaration::type_check(ctx.by_ref(), fn_decl, false),
+                    return ok(ty::TyDeclaration::ErrorRecovery(span), warnings, errors),
+                    warnings,
+                    errors
+                );
+                let name = fn_decl.name.clone();
+                let decl = ty::TyDeclaration::FunctionDeclaration(de_insert_function(fn_decl));
+                ctx.namespace.insert_symbol(name, decl.clone());
+                decl
+            }
+            parsed::Declaration::TraitDeclaration(trait_decl) => {
+                let span = trait_decl.span.clone();
+                let trait_decl = check!(
+                    ty::TyTraitDeclaration::type_check(ctx.by_ref(), trait_decl),
+                    return ok(ty::TyDeclaration::ErrorRecovery(span), warnings, errors),
+                    warnings,
+                    errors
+                );
+                let name = trait_decl.name.clone();
+                let decl_id = de_insert_trait(trait_decl);
+                let decl = ty::TyDeclaration::TraitDeclaration(decl_id);
+                ctx.namespace.insert_symbol(name, decl.clone());
+                decl
+            }
+            parsed::Declaration::ImplTrait(impl_trait) => {
+                let span = impl_trait.block_span.clone();
+                let impl_trait = check!(
+                    ty::TyImplTrait::type_check_impl_trait(ctx.by_ref(), impl_trait),
+                    return ok(ty::TyDeclaration::ErrorRecovery(span), warnings, errors),
+                    warnings,
+                    errors
+                );
+                check!(
+                    ctx.namespace.insert_trait_implementation(
+                        impl_trait.trait_name.clone(),
+                        impl_trait.trait_type_arguments.clone(),
+                        impl_trait.implementing_for_type_id,
+                        &impl_trait.methods,
+                        &impl_trait.span,
+                        false
+                    ),
+                    return err(warnings, errors),
+                    warnings,
+                    errors
+                );
+                ty::TyDeclaration::ImplTrait(de_insert_impl_trait(impl_trait))
+            }
+            parsed::Declaration::ImplSelf(impl_self) => {
+                let span = impl_self.block_span.clone();
+                let impl_trait = check!(
+                    ty::TyImplTrait::type_check_impl_self(ctx.by_ref(), impl_self),
+                    return ok(ty::TyDeclaration::ErrorRecovery(span), warnings, errors),
+                    warnings,
+                    errors
+                );
+                check!(
+                    ctx.namespace.insert_trait_implementation(
+                        impl_trait.trait_name.clone(),
+                        impl_trait.trait_type_arguments.clone(),
+                        impl_trait.implementing_for_type_id,
+                        &impl_trait.methods,
+                        &impl_trait.span,
+                        true
+                    ),
+                    return err(warnings, errors),
+                    warnings,
+                    errors
+                );
+                ty::TyDeclaration::ImplTrait(de_insert_impl_trait(impl_trait))
+            }
+            parsed::Declaration::StructDeclaration(decl) => {
+                let span = decl.span.clone();
+                let decl = check!(
+                    ty::TyStructDeclaration::type_check(ctx.by_ref(), decl),
+                    return ok(ty::TyDeclaration::ErrorRecovery(span), warnings, errors),
+                    warnings,
+                    errors
+                );
+                let name = decl.name.clone();
+                let decl_id = de_insert_struct(decl);
+                let decl = ty::TyDeclaration::StructDeclaration(decl_id);
+                // insert the struct decl into namespace
+                check!(
+                    ctx.namespace.insert_symbol(name, decl.clone()),
+                    return err(warnings, errors),
+                    warnings,
+                    errors
+                );
+                decl
+            }
+            parsed::Declaration::AbiDeclaration(abi_decl) => {
+                let span = abi_decl.span.clone();
+                let abi_decl = check!(
+                    ty::TyAbiDeclaration::type_check(ctx.by_ref(), abi_decl),
+                    return ok(ty::TyDeclaration::ErrorRecovery(span), warnings, errors),
+                    warnings,
+                    errors
+                );
+                let name = abi_decl.name.clone();
+                let decl = ty::TyDeclaration::AbiDeclaration(de_insert_abi(abi_decl));
+                ctx.namespace.insert_symbol(name, decl.clone());
+                decl
+            }
+            parsed::Declaration::StorageDeclaration(parsed::StorageDeclaration {
+                span,
+                fields,
+                attributes,
+                ..
+            }) => {
+                let mut fields_buf = Vec::with_capacity(fields.len());
+                for parsed::StorageField {
+                    name,
+                    type_info,
+                    initializer,
+                    type_info_span,
+                    attributes,
+                    ..
+                } in fields
+                {
+                    let type_id = check!(
+                        ctx.resolve_type_without_self(insert_type(type_info), &name.span(), None),
+                        return err(warnings, errors),
+                        warnings,
+                        errors
+                    );
+
+                    let mut ctx = ctx.by_ref().with_type_annotation(type_id);
+                    let initializer = check!(
+                        ty::TyExpression::type_check(ctx.by_ref(), initializer),
+                        return err(warnings, errors),
+                        warnings,
+                        errors,
+                    );
+
+                    fields_buf.push(ty::TyStorageField {
+                        name,
+                        type_id,
+                        type_span: type_info_span,
+                        initializer,
+                        span: span.clone(),
+                        attributes,
+                    });
+                }
+                let decl = ty::TyStorageDeclaration::new(fields_buf, span, attributes);
+                let decl_id = de_insert_storage(decl);
+                // insert the storage declaration into the symbols
+                // if there already was one, return an error that duplicate storage
+
+                // declarations are not allowed
+                check!(
+                    ctx.namespace.set_storage_declaration(decl_id.clone()),
+                    return err(warnings, errors),
+                    warnings,
+                    errors
+                );
+                ty::TyDeclaration::StorageDeclaration(decl_id)
+            }
+        };
+
+        ok(decl, warnings, errors)
+    }
+}
```

### sway-core/src/semantic_analysis/ast_node/declaration/function.rs
```diff
@@ -55,15 +55,18 @@ impl ty::TyFunctionDeclaration {
                 errors.push(CompileError::WhereClauseNotYetSupported {
                     span: type_parameter.trait_constraints_span,
                 });
-                return err(warnings, errors);
+                continue;
             }
             new_type_parameters.push(check!(
                 TypeParameter::type_check(fn_ctx.by_ref(), type_parameter),
-                return err(warnings, errors),
+                continue,
                 warnings,
                 errors
             ));
         }
+        if !errors.is_empty() {
+            return err(warnings, errors);
+        }
 
         // type check the function parameters, which will also insert them into the namespace
         let mut new_parameters = vec![];
@@ -75,6 +78,9 @@ impl ty::TyFunctionDeclaration {
                 errors
             ));
         }
+        if !errors.is_empty() {
+            return err(warnings, errors);
+        }
 
         // type check the return type
         let initial_return_type = insert_type(return_type);
```

### sway-core/src/semantic_analysis/ast_node/declaration/impl_trait.rs
```diff
@@ -366,7 +366,7 @@ impl ty::TyImplTrait {
                 | ty::TyDeclaration::ImplTrait(_)
                 | ty::TyDeclaration::AbiDeclaration(_)
                 | ty::TyDeclaration::GenericTypeForFunctionScope { .. }
-                | ty::TyDeclaration::ErrorRecovery
+                | ty::TyDeclaration::ErrorRecovery(_)
                 | ty::TyDeclaration::StorageDeclaration(_) => Ok(false),
             }
         }
@@ -432,15 +432,18 @@ impl ty::TyImplTrait {
                 errors.push(CompileError::WhereClauseNotYetSupported {
                     span: type_parameter.trait_constraints_span,
                 });
-                return err(warnings, errors);
+                continue;
             }
             new_impl_type_parameters.push(check!(
                 TypeParameter::type_check(ctx.by_ref(), type_parameter),
-                return err(warnings, errors),
+                continue,
                 warnings,
                 errors
             ));
         }
+        if !errors.is_empty() {
+            return err(warnings, errors);
+        }
 
         // type check the type that we are implementing for
         let implementing_for_type_id = check!(
@@ -491,6 +494,9 @@ impl ty::TyImplTrait {
                 errors
             ));
         }
+        if !errors.is_empty() {
+            return err(warnings, errors);
+        }
 
         check!(
             CompileResult::from(Self::gather_storage_only_types(
@@ -611,7 +617,7 @@ fn type_check_trait_implementation(
             errors.push(CompileError::MultipleDefinitionsOfFunction {
                 name: impl_method.name.clone(),
             });
-            return err(warnings, errors);
+            continue;
         }
 
         // remove this function from the "checklist"
@@ -623,7 +629,7 @@ fn type_check_trait_implementation(
                     interface_name: interface_name(),
                     span: impl_method.name.span(),
                 });
-                return err(warnings, errors);
+                continue;
             }
         };
 
@@ -820,7 +826,11 @@ fn type_check_trait_implementation(
         });
     }
 
-    ok(new_method_ids, warnings, errors)
+    if errors.is_empty() {
+        ok(new_method_ids, warnings, errors)
+    } else {
+        err(warnings, errors)
+    }
 }
 
 /// Given an array of [TypeParameter] `type_parameters`, checks to see if any of
```

### sway-core/src/semantic_analysis/ast_node/declaration/mod.rs
```diff
@@ -1,4 +1,6 @@
 mod abi;
+#[allow(clippy::module_inception)]
+mod declaration;
 mod r#enum;
 mod function;
 mod impl_trait;
```

### sway-core/src/semantic_analysis/ast_node/mod.rs
```diff
@@ -17,38 +17,14 @@ use crate::{
     Ident,
 };
 
-use sway_error::{
-    error::CompileError,
-    warning::{CompileWarning, Warning},
-};
-use sway_types::{span::Span, state::StateIndex, style::is_screaming_snake_case, Spanned};
+use sway_error::{error::CompileError, warning::Warning};
+use sway_types::{span::Span, state::StateIndex, Spanned};
 
 impl ty::TyAstNode {
-    pub(crate) fn type_check(mut ctx: TypeCheckContext, node: AstNode) -> CompileResult<Self> {
+    pub(crate) fn type_check(ctx: TypeCheckContext, node: AstNode) -> CompileResult<Self> {
         let mut warnings = Vec::new();
         let mut errors = Vec::new();
 
-        // A little utility used to check an ascribed type matches its associated expression.
-        let mut type_check_ascribed_expr =
-            |mut ctx: TypeCheckContext, type_ascription: TypeInfo, expr| {
-                let type_id = check!(
-                    ctx.resolve_type_with_self(
-                        insert_type(type_ascription),
-                        &node.span,
-                        EnforceTypeArguments::No,
-                        None
-                    ),
-                    insert_type(TypeInfo::ErrorRecovery),
-                    warnings,
-                    errors,
-                );
-                let ctx = ctx.with_type_annotation(type_id).with_help_text(
-                    "This declaration's type annotation does not match up with the assigned \
-                        expression's type.",
-                );
-                ty::TyExpression::type_check(ctx, expr)
-            };
-
         let node = ty::TyAstNode {
             content: match node.content.clone() {
                 AstNodeContent::UseStatement(a) => {
@@ -67,270 +43,12 @@ impl ty::TyAstNode {
                     ty::TyAstNodeContent::SideEffect
                 }
                 AstNodeContent::IncludeStatement(_) => ty::TyAstNodeContent::SideEffect,
-                AstNodeContent::Declaration(a) => {
-                    ty::TyAstNodeContent::Declaration(match a {
-                        Declaration::VariableDeclaration(VariableDeclaration {
-                            name,
-                            type_ascription,
-                            type_ascription_span,
-                            body,
-                            is_mutable,
-                        }) => {
-                            let type_ascription = check!(
-                                ctx.resolve_type_with_self(
-                                    insert_type(type_ascription),
-                                    &type_ascription_span.clone().unwrap_or_else(|| name.span()),
-                                    EnforceTypeArguments::Yes,
-                                    None
-                                ),
-                                insert_type(TypeInfo::ErrorRecovery),
-                                warnings,
-                                errors
-                            );
-                            let mut ctx = ctx.with_type_annotation(type_ascription).with_help_text(
-                                "Variable declaration's type annotation does not match up \
-                                    with the assigned expression's type.",
-                            );
-                            let result = ty::TyExpression::type_check(ctx.by_ref(), body);
-                            let body = check!(
-                                result,
-                                ty::TyExpression::error(name.span()),
-                                warnings,
-                                errors
-                            );
-                            let typed_var_decl = ty::TyDeclaration::VariableDeclaration(Box::new(
-                                ty::TyVariableDeclaration {
-                                    name: name.clone(),
-                                    body,
-                                    mutability: ty::VariableMutability::new_from_ref_mut(
-                                        false, is_mutable,
-                                    ),
-                                    type_ascription,
-                                    type_ascription_span,
-                                },
-                            ));
-                            ctx.namespace.insert_symbol(name, typed_var_decl.clone());
-                            typed_var_decl
-                        }
-                        Declaration::ConstantDeclaration(ConstantDeclaration {
-                            name,
-                            type_ascription,
-                            value,
-                            visibility,
-                            attributes,
-                            span,
-                            ..
-                        }) => {
-                            let result =
-                                type_check_ascribed_expr(ctx.by_ref(), type_ascription, value);
-
-                            if !is_screaming_snake_case(name.as_str()) {
-                                warnings.push(CompileWarning {
-                                    span: name.span(),
-                                    warning_content: Warning::NonScreamingSnakeCaseConstName {
-                                        name: name.clone(),
-                                    },
-                                })
-                            }
-
-                            let value = check!(
-                                result,
-                                ty::TyExpression::error(name.span()),
-                                warnings,
-                                errors
-                            );
-                            let decl = ty::TyConstantDeclaration {
-                                name: name.clone(),
-                                value,
-                                visibility,
-                                attributes,
-                                span,
-                            };
-                            let typed_const_decl =
-                                ty::TyDeclaration::ConstantDeclaration(de_insert_constant(decl));
-                            ctx.namespace.insert_symbol(name, typed_const_decl.clone());
-                            typed_const_decl
-                        }
-                        Declaration::EnumDeclaration(decl) => {
-                            let enum_decl = check!(
-                                ty::TyEnumDeclaration::type_check(ctx.by_ref(), decl),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            let name = enum_decl.name.clone();
-                            let decl =
-                                ty::TyDeclaration::EnumDeclaration(de_insert_enum(enum_decl));
-                            check!(
-                                ctx.namespace.insert_symbol(name, decl.clone()),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            decl
-                        }
-                        Declaration::FunctionDeclaration(fn_decl) => {
-                            let mut ctx = ctx.with_type_annotation(insert_type(TypeInfo::Unknown));
-                            let fn_decl = check!(
-                                ty::TyFunctionDeclaration::type_check(ctx.by_ref(), fn_decl, false),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            let name = fn_decl.name.clone();
-                            let decl =
-                                ty::TyDeclaration::FunctionDeclaration(de_insert_function(fn_decl));
-                            ctx.namespace.insert_symbol(name, decl.clone());
-                            decl
-                        }
-                        Declaration::TraitDeclaration(trait_decl) => {
-                            let trait_decl = check!(
-                                ty::TyTraitDeclaration::type_check(ctx.by_ref(), trait_decl),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            let name = trait_decl.name.clone();
-                            let decl_id = de_insert_trait(trait_decl);
-                            let decl = ty::TyDeclaration::TraitDeclaration(decl_id);
-                            ctx.namespace.insert_symbol(name, decl.clone());
-                            decl
-                        }
-                        Declaration::ImplTrait(impl_trait) => {
-                            let impl_trait = check!(
-                                ty::TyImplTrait::type_check_impl_trait(ctx.by_ref(), impl_trait),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            check!(
-                                ctx.namespace.insert_trait_implementation(
-                                    impl_trait.trait_name.clone(),
-                                    impl_trait.trait_type_arguments.clone(),
-                                    impl_trait.implementing_for_type_id,
-                                    &impl_trait.methods,
-                                    &impl_trait.span,
-                                    false
-                                ),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            ty::TyDeclaration::ImplTrait(de_insert_impl_trait(impl_trait))
-                        }
-                        Declaration::ImplSelf(impl_self) => {
-                            let impl_trait = check!(
-                                ty::TyImplTrait::type_check_impl_self(ctx.by_ref(), impl_self),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            check!(
-                                ctx.namespace.insert_trait_implementation(
-                                    impl_trait.trait_name.clone(),
-                                    impl_trait.trait_type_arguments.clone(),
-                                    impl_trait.implementing_for_type_id,
-                                    &impl_trait.methods,
-                                    &impl_trait.span,
-                                    true
-                                ),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            ty::TyDeclaration::ImplTrait(de_insert_impl_trait(impl_trait))
-                        }
-                        Declaration::StructDeclaration(decl) => {
-                            let decl = check!(
-                                ty::TyStructDeclaration::type_check(ctx.by_ref(), decl),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            let name = decl.name.clone();
-                            let decl_id = de_insert_struct(decl);
-                            let decl = ty::TyDeclaration::StructDeclaration(decl_id);
-                            // insert the struct decl into namespace
-                            check!(
-                                ctx.namespace.insert_symbol(name, decl.clone()),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            decl
-                        }
-                        Declaration::AbiDeclaration(abi_decl) => {
-                            let abi_decl = check!(
-                                ty::TyAbiDeclaration::type_check(ctx.by_ref(), abi_decl),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            let name = abi_decl.name.clone();
-                            let decl = ty::TyDeclaration::AbiDeclaration(de_insert_abi(abi_decl));
-                            ctx.namespace.insert_symbol(name, decl.clone());
-                            decl
-                        }
-                        Declaration::StorageDeclaration(StorageDeclaration {
-                            span,
-                            fields,
-                            attributes,
-                            ..
-                        }) => {
-                            let mut fields_buf = Vec::with_capacity(fields.len());
-                            for StorageField {
-                                name,
-                                type_info,
-                                initializer,
-                                type_info_span,
-                                attributes,
-                                ..
-                            } in fields
-                            {
-                                let type_id = check!(
-                                    ctx.resolve_type_without_self(
-                                        insert_type(type_info),
-                                        &name.span(),
-                                        None
-                                    ),
-                                    return err(warnings, errors),
-                                    warnings,
-                                    errors
-                                );
-
-                                let mut ctx = ctx.by_ref().with_type_annotation(type_id);
-                                let initializer = check!(
-                                    ty::TyExpression::type_check(ctx.by_ref(), initializer),
-                                    return err(warnings, errors),
-                                    warnings,
-                                    errors,
-                                );
-
-                                fields_buf.push(ty::TyStorageField {
-                                    name,
-                                    type_id,
-                                    type_span: type_info_span,
-                                    initializer,
-                                    span: span.clone(),
-                                    attributes,
-                                });
-                            }
-                            let decl = ty::TyStorageDeclaration::new(fields_buf, span, attributes);
-                            let decl_id = de_insert_storage(decl);
-                            // insert the storage declaration into the symbols
-                            // if there already was one, return an error that duplicate storage
-
-                            // declarations are not allowed
-                            check!(
-                                ctx.namespace.set_storage_declaration(decl_id.clone()),
-                                return err(warnings, errors),
-                                warnings,
-                                errors
-                            );
-                            ty::TyDeclaration::StorageDeclaration(decl_id)
-                        }
-                    })
-                }
+                AstNodeContent::Declaration(decl) => ty::TyAstNodeContent::Declaration(check!(
+                    ty::TyDeclaration::type_check(ctx, decl),
+                    return err(warnings, errors),
+                    warnings,
+                    errors
+                )),
                 AstNodeContent::Expression(expr) => {
                     let ctx = ctx
                         .with_type_annotation(insert_type(TypeInfo::Unknown))
@@ -355,7 +73,7 @@ impl ty::TyAstNode {
                     ty::TyAstNodeContent::ImplicitReturnExpression(typed_expr)
                 }
             },
-            span: node.span.clone(),
+            span: node.span,
         };
 
         if let ty::TyAstNode {
```

### sway-core/src/semantic_analysis/namespace/namespace.rs
```diff
@@ -221,6 +221,7 @@ impl Namespace {
             errors.push(CompileError::MethodNotFound {
                 method_name: method_name.clone(),
                 type_name: type_id.to_string(),
+                span: method_name.span(),
             });
         }
         err(warnings, errors)
```

### sway-core/src/semantic_analysis/storage_only_types.rs
```diff
@@ -284,7 +284,7 @@ fn decl_validate(decl: &ty::TyDeclaration) -> CompileResult<()> {
             }
         }
         ty::TyDeclaration::GenericTypeForFunctionScope { .. }
-        | ty::TyDeclaration::ErrorRecovery => {}
+        | ty::TyDeclaration::ErrorRecovery(_) => {}
     }
     ok((), warnings, errors)
 }
```

### sway-error/src/error.rs
```diff
@@ -235,6 +235,7 @@ pub enum CompileError {
     MethodNotFound {
         method_name: Ident,
         type_name: String,
+        span: Span,
     },
     #[error("Module \"{name}\" could not be found.")]
     ModuleNotFound { span: Span, name: String },
@@ -726,7 +727,7 @@ impl Spanned for CompileError {
             MethodOnNonValue { span, .. } => span.clone(),
             StructMissingField { span, .. } => span.clone(),
             StructDoesNotHaveField { span, .. } => span.clone(),
-            MethodNotFound { method_name, .. } => method_name.span(),
+            MethodNotFound { span, .. } => span.clone(),
             ModuleNotFound { span, .. } => span.clone(),
             NotATuple { span, .. } => span.clone(),
             NotAStruct { span, .. } => span.clone(),
```
