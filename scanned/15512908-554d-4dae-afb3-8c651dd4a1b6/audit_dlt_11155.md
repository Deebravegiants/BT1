# [?] Fix non-deterministic tuple names (#1542)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-05-13
Source: https://github.com/FuelLabs/sway/commit/afcc5211d3e6bbcebecdb1b977ae4a44dc7e9c2b
Type: security-commit

## Details
Fix non-deterministic tuple names (#1542)

## Patch
### sway-core/src/constants.rs
```diff
@@ -20,3 +20,6 @@ pub const CONTRACT_CALL_ASSET_ID_PARAMETER_DEFAULT_VALUE: [u8; 32] = [0; 32];
 
 /// The default entry point for scripts and predicates.
 pub const DEFAULT_ENTRY_POINT_FN_NAME: &str = "main";
+
+/// The default prefix for the compiler generated names of tuples
+pub const TUPLE_NAME_PREFIX: &str = "__tuple_";
```

### sway-core/src/convert_parse_tree.rs
```diff
@@ -1,3 +1,4 @@
+use std::sync::atomic::{AtomicUsize, Ordering};
 use {
     crate::{
         error::{err, ok, CompileError, CompileResult, CompileWarning},
@@ -13,7 +14,6 @@ use {
         SwayParseTree, TraitDeclaration, TraitFn, TreeType, TypeArgument, TypeInfo, TypeParameter,
         UseStatement, VariableDeclaration, Visibility, WhileLoop,
     },
-    nanoid::nanoid,
     std::{convert::TryFrom, iter, mem::MaybeUninit, ops::ControlFlow},
     sway_parse::{
         AbiCastArgs, AngleBrackets, AsmBlock, Assignable, Braces, CodeBlockContents, Dependency,
@@ -2228,11 +2228,19 @@ fn statement_let_to_ast_nodes(
             }
             Pattern::Tuple(pat_tuple) => {
                 let mut ast_nodes = Vec::new();
-                let name = {
-                    // FIXME: This is so, so dodgy.
-                    let name_str: &'static str = Box::leak(nanoid!(32).into_boxed_str());
-                    Ident::new_with_override(name_str, span.clone())
-                };
+
+                // Generate a deterministic name for the tuple. Because the parser is single
+                // threaded, the name generated below will be stable.
+                static COUNTER: AtomicUsize = AtomicUsize::new(0);
+                let tuple_name = format!(
+                    "{}{}",
+                    crate::constants::TUPLE_NAME_PREFIX,
+                    COUNTER.load(Ordering::SeqCst)
+                );
+                COUNTER.fetch_add(1, Ordering::SeqCst);
+                let name =
+                    Ident::new_with_override(Box::leak(tuple_name.into_boxed_str()), span.clone());
+
                 let (type_ascription, type_ascription_span) = match &ty_opt {
                     Some(ty) => {
                         let type_ascription_span = ty.span();
```
