# [?] Fixes method application unwrap panic. (#6201)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-07-01
Source: https://github.com/FuelLabs/sway/commit/65dbd34e7185a58fc3432397c8a0290fb4d72cc3
Type: security-commit

## Details
Fixes method application unwrap panic. (#6201)

## Description

This commit replaces an unwrap that was, in the previous version of std
lib, throwing out a panic because the base value was None.

Fixes #6060

## Checklist

- [ ] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [ ] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

Co-authored-by: IGI-111 <igi-111@protonmail.com>

## Patch
### sway-core/src/semantic_analysis/ast_node/expression/typed_expression/method_application.rs
```diff
@@ -109,26 +109,24 @@ pub(crate) fn type_check_method_application(
         if let (Some(arg), false) = arg_opt {
             args_buf.push_back(arg);
         } else {
+            // We type check the argument expression again this time throwing out the error.
             let param_index = if method.is_contract_call {
                 index - 1 //contract call methods don't have self parameter.
             } else {
                 index
             };
-            // This arg_opt is None because it failed in the first pass.
-            // We now try to type check it again, this time with the type annotation.
-            let ctx = ctx
-                .by_ref()
-                .with_help_text(
-                    "Function application argument type must match function parameter type.",
-                )
-                .with_type_annotation(
-                    method
-                        .parameters
-                        .get(param_index)
-                        .unwrap()
-                        .type_argument
-                        .type_id,
-                );
+            let ctx = if let Some(param) = method.parameters.get(param_index) {
+                // We now try to type check it again, this time with the type annotation.
+                ctx.by_ref()
+                    .with_help_text(
+                        "Function application argument type must match function parameter type.",
+                    )
+                    .with_type_annotation(param.type_argument.type_id)
+            } else {
+                ctx.by_ref()
+                    .with_help_text("")
+                    .with_type_annotation(type_engine.insert(engines, TypeInfo::Unknown, None))
+            };
             args_buf.push_back(
                 ty::TyExpression::type_check(handler, ctx, arg)
                     .unwrap_or_else(|err| ty::TyExpression::error(err, span.clone(), engines)),
```
