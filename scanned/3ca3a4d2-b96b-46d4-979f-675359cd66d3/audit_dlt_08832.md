# [?] fix(semantic): report macro expansion failures instead of panicking (#10297)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-08-25
Source: https://github.com/starkware-libs/cairo/commit/48fcf0f15938060c6076b7a20673c374597ae1fd
Type: security-commit

## Details
fix(semantic): report macro expansion failures instead of panicking (#10297)

## Patch
### crates/cairo-lang-semantic/src/diagnostic.rs
```diff
@@ -27,6 +27,7 @@ use syntax::node::ids::SyntaxStablePtrId;
 use crate::corelib::LiteralError;
 use crate::expr::inference::InferenceError;
 use crate::items::feature_kind::FeatureMarkerDiagnostic;
+use crate::items::macro_declaration::MacroExpansionFailure;
 use crate::items::trt::ConcreteTraitTypeId;
 use crate::path::ContextualizePath;
 use crate::resolve::{ResolvedConcreteItem, ResolvedGenericItem};
@@ -1228,6 +1229,17 @@ impl<'db> DiagnosticEntry<'db> for SemanticDiagnostic<'db> {
                     name.long(db)
                 )
             }
+            SemanticDiagnosticKind::MacroExpansionFailed(failure) => match failure {
+                MacroExpansionFailure::RepetitionWithoutPlaceholder => {
+                    "Repetition in the macro expansion holds no placeholder, so the number of \
+                     repetitions cannot be determined."
+                        .into()
+                }
+                MacroExpansionFailure::MissingCapture(name) => format!(
+                    "Macro placeholder '{}' has no captured value in this repetition.",
+                    name.long(db)
+                ),
+            },
             SemanticDiagnosticKind::UserDefinedInlineMacrosDisabled => {
                 "User defined inline macros are disabled in the current crate.".into()
             }
@@ -1507,6 +1519,7 @@ impl<'db> DiagnosticEntry<'db> for SemanticDiagnostic<'db> {
             SemanticDiagnosticKind::OnlyTypeOrConstParamsInNegImpl => error_code!(E2196),
             SemanticDiagnosticKind::UnsupportedItemInStatement => error_code!(E2197),
             SemanticDiagnosticKind::ExternItemOutsideCorelib => error_code!(E2201),
+            SemanticDiagnosticKind::MacroExpansionFailed(_) => error_code!(E2202),
             SemanticDiagnosticKind::PluginDiagnostic(diag) => {
                 diag.error_code.unwrap_or(error_code!(E2200))
             }
@@ -1928,6 +1941,7 @@ pub enum SemanticDiagnosticKind<'db> {
         actual: usize,
     },
     MacroPlaceholderRepDriverMismatch(SmolStrId<'db>),
+    MacroExpansionFailed(MacroExpansionFailure<'db>),
     UserDefinedInlineMacrosDisabled,
     NonNeverLetElseType,
     OnlyTypeOrConstParamsInNegImpl,
```

### crates/cairo-lang-semantic/src/expr/compute.rs
```diff
@@ -835,7 +835,8 @@ fn expand_inline_macro<'db>(
         rule.err?;
         let mut matcher_ctx =
             MatcherContext { captures, placeholder_to_rep_id, ..Default::default() };
-        let expanded_code = expand_macro_rule(ctx.db, rule, &mut matcher_ctx)?;
+        let expanded_code = expand_macro_rule(ctx.db, rule, &mut matcher_ctx)
+            .map_err(|err| err.report(ctx.diagnostics))?;
 
         let macro_defsite_resolver_data =
             ctx.db.macro_declaration_resolver_data(macro_declaration_id)?;
```

### crates/cairo-lang-semantic/src/expr/test_data/inline_macros
```diff
@@ -2552,11 +2552,6 @@ error[E1001]: Missing token ';'.
 m!
   ^
 
-error[E2158]: No matching rule found in inline macro `m`.
- --> lib.cairo:5:1
-m!
-^^
-
 //! > ==========================================================================
 
 //! > Regression for #9993: macro call with `$(...)` without an operator does not ICE.
@@ -2704,3 +2699,106 @@ error[E2199]: Macro placeholder 'b' is from a different repetition than the one
  --> lib.cairo:2:49
     ($($a:ident),* ; $($b:ident),*) => { $($a + $b + )* 0 };
                                                 ^^
+
+//! > ==========================================================================
+
+//! > Test item-position macro call whose expansion repeats a placeholder-free block.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > cairo_code
+macro m {
+    () => { $(foo)* };
+}
+
+m!();
+fn foo() {}
+
+//! > expected_diagnostics
+error[E2202]: Repetition in the macro expansion holds no placeholder, so the number of repetitions cannot be determined.
+ --> lib.cairo:2:13
+    () => { $(foo)* };
+            ^^^^^^^
+
+//! > ==========================================================================
+
+//! > Test expression-position macro call whose expansion repeats a placeholder-free block.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > cairo_code
+macro m {
+    () => { $(foo)* 0 };
+}
+fn foo() -> felt252 {
+    m!()
+}
+
+//! > expected_diagnostics
+error[E2202]: Repetition in the macro expansion holds no placeholder, so the number of repetitions cannot be determined.
+ --> lib.cairo:2:13
+    () => { $(foo)* 0 };
+            ^^^^^^^
+
+//! > ==========================================================================
+
+//! > Test item-position macro call whose expansion repeats its own placeholder (valid).
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: false)
+
+//! > cairo_code
+macro make_fns {
+    ($($name:ident),*) => { $(fn $name() {})* };
+}
+
+make_fns!(first, second);
+fn foo() {}
+
+//! > expected_diagnostics
+
+//! > ==========================================================================
+
+//! > Test item-position macro call with a parse error in its arguments reports only that error.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > cairo_code
+macro m {
+    ($x:ident) => { fn $x() {} };
+}
+
+m!([1);
+fn foo() {}
+
+//! > expected_diagnostics
+error[E1001]: Missing token ']'.
+ --> lib.cairo:5:6
+m!([1);
+     ^
+
+//! > ==========================================================================
+
+//! > Test placeholder-free repetition in a macro declared in another module.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > cairo_code
+mod helpers {
+    pub macro m {
+        () => { $(foo)* };
+    }
+}
+
+helpers::m!();
+fn foo() {}
+
+//! > expected_diagnostics
+error[E2202]: Repetition in the macro expansion holds no placeholder, so the number of repetitions cannot be determined.
+ --> lib.cairo:3:17
+        () => { $(foo)* };
+                ^^^^^^^
```

### crates/cairo-lang-semantic/src/items/macro_call.rs
```diff
@@ -76,6 +76,18 @@ fn priv_macro_call_data<'db>(
         });
     }
     let mut diagnostics = SemanticDiagnostics::new(callsite_module_id);
+    // Skipping the expansion of a macro call that had a parser error, as the reported parser errors
+    // already describe the problem.
+    if macro_call_syntax.as_syntax_node().contains_missing(db) {
+        return Ok(MacroCallData {
+            macro_call_module: Err(skip_diagnostic()),
+            diagnostics: diagnostics.build(),
+            defsite_module_id: callsite_module_id,
+            callsite_module_id,
+            expansion_mappings: Arc::new([]),
+            parent_macro_call_data: resolver.macro_call_data,
+        });
+    }
     let macro_declaration_id = match resolver.resolve_generic_path(
         &mut diagnostics,
         &macro_call_path,
@@ -151,7 +163,20 @@ fn priv_macro_call_data<'db>(
         });
     }
     let mut matcher_ctx = MatcherContext { captures, placeholder_to_rep_id, ..Default::default() };
-    let expanded_code = expand_macro_rule(db, rule, &mut matcher_ctx).unwrap();
+    let expanded_code = match expand_macro_rule(db, rule, &mut matcher_ctx) {
+        Ok(expanded_code) => expanded_code,
+        Err(err) => {
+            let diag_added = err.report(&mut diagnostics);
+            return Ok(MacroCallData {
+                macro_call_module: Err(diag_added),
+                diagnostics: diagnostics.build(),
+                defsite_module_id,
+                callsite_module_id,
+                expansion_mappings: Arc::new([]),
+                parent_macro_call_data,
+            });
+        }
+    };
     let generated_file_id = FileLongId::Virtual(VirtualFile {
         parent: Some(macro_call_syntax.stable_ptr(db).untyped().span_in_file(db)),
         name: macro_name,
```

### crates/cairo-lang-semantic/src/items/macro_declaration.rs
```diff
@@ -4,7 +4,7 @@ use cairo_lang_defs::db::DefsGroup;
 use cairo_lang_defs::ids::{
     LanguageElementId, LookupItemId, MacroDeclarationId, ModuleId, ModuleItemId,
 };
-use cairo_lang_diagnostics::{Diagnostics, Maybe, skip_diagnostic};
+use cairo_lang_diagnostics::{DiagnosticAdded, Diagnostics, Maybe};
 use cairo_lang_filesystem::db::FilesGroup;
 use cairo_lang_filesystem::ids::{CodeMapping, CodeOrigin, SmolStrId};
 use cairo_lang_filesystem::span::{TextSpan, TextWidth};
@@ -555,16 +555,42 @@ pub struct MacroExpansionResult {
     pub code_mappings: Arc<[CodeMapping]>,
 }
 
+/// The reason the expansion of a macro rule could not be performed.
+#[derive(Clone, Debug, Eq, Hash, PartialEq, salsa::SalsaValue)]
+pub enum MacroExpansionFailure<'db> {
+    /// A `$( ... )` block in the expansion holds no placeholder, so there is nothing to determine
+    /// how many times it should be repeated.
+    RepetitionWithoutPlaceholder,
+    /// A placeholder in the expansion has no captured value at the current repetition indices.
+    MissingCapture(SmolStrId<'db>),
+}
+
+/// An error preventing the expansion of a macro rule, to be reported by the caller performing the
+/// expansion.
+#[derive(Clone, Debug, Eq, PartialEq)]
+pub struct MacroExpansionError<'db> {
+    /// The node in the rule's expansion that could not be expanded.
+    stable_ptr: SyntaxStablePtrId<'db>,
+    /// The reason the expansion failed.
+    failure: MacroExpansionFailure<'db>,
+}
+impl<'db> MacroExpansionError<'db> {
+    /// Reports the error as a semantic diagnostic on the node that could not be expanded.
+    pub fn report(self, diagnostics: &mut SemanticDiagnostics<'db>) -> DiagnosticAdded {
+        diagnostics
+            .report(self.stable_ptr, SemanticDiagnosticKind::MacroExpansionFailed(self.failure))
+    }
+}
+
 /// Traverse the macro expansion and replace the placeholders with the provided values, creates a
 /// string representation of the expanded macro.
 ///
-/// Returns an error if any used placeholder in the expansion is not found in the captures.
-/// When an error is returned, appropriate diagnostics will already have been reported.
-pub fn expand_macro_rule(
-    db: &dyn Database,
-    rule: &MacroRuleData<'_>,
-    matcher_ctx: &mut MatcherContext<'_>,
-) -> Maybe<MacroExpansionResult> {
+/// Returns an error if the expansion cannot be performed, for the caller to report.
+pub fn expand_macro_rule<'db>(
+    db: &'db dyn Database,
+    rule: &MacroRuleData<'db>,
+    matcher_ctx: &mut MatcherContext<'db>,
+) -> Result<MacroExpansionResult, MacroExpansionError<'db>> {
     let node = rule.expansion.as_syntax_node();
     let mut res_buffer = String::new();
     let mut code_mappings = Vec::new();
@@ -574,16 +600,13 @@ pub fn expand_macro_rule(
 
 /// Helper function for [expand_macro_rule]. Traverses the macro expansion and replaces the
 /// placeholders with the provided values while collecting the result in res_buffer.
-///
-/// Returns an error if a placeholder is not found in captures.
-/// When an error is returned, appropriate diagnostics will already have been reported.
-fn expand_macro_rule_ex(
-    db: &dyn Database,
-    node: SyntaxNode<'_>,
-    matcher_ctx: &mut MatcherContext<'_>,
+fn expand_macro_rule_ex<'db>(
+    db: &'db dyn Database,
+    node: SyntaxNode<'db>,
+    matcher_ctx: &mut MatcherContext<'db>,
     res_buffer: &mut String,
     code_mappings: &mut Vec<CodeMapping>,
-) -> Maybe<()> {
+) -> Result<(), MacroExpansionError<'db>> {
     match node.kind(db) {
         SyntaxKind::MacroParam => {
             let path_node = MacroParam::from_syntax_node(db, node);
@@ -597,7 +620,10 @@ fn expand_macro_rule_ex(
                     .captures
                     .get(&name)
                     .and_then(|v| rep_index.map_or_else(|| v.first(), |i| v.get(i)))
-                    .ok_or_else(skip_diagnostic)?;
+                    .ok_or(MacroExpansionError {
+                        stable_ptr: path_node.stable_ptr(db).untyped(),
+                        failure: MacroExpansionFailure::MissingCapture(name),
+                    })?;
                 let start = TextWidth::from_str(res_buffer).as_offset();
                 let span = TextSpan::new_with_width(start, TextWidth::from_str(&value.text));
                 res_buffer.push_str(&value.text);
@@ -611,8 +637,12 @@ fn expand_macro_rule_ex(
         SyntaxKind::MacroRepetition => {
             let repetition = ast::MacroRepetition::from_syntax_node(db, node);
             let elements = repetition.elements(db);
-            let first_param = find_first_repetition_param(db, elements.elements(db))
-                .ok_or_else(skip_diagnostic)?;
+            let first_param = find_first_repetition_param(db, elements.elements(db)).ok_or(
+                MacroExpansionError {
+                    stable_ptr: repetition.stable_ptr(db).untyped(),
+                    failure: MacroExpansionFailure::RepetitionWithoutPlaceholder,
+                },
+            )?;
             let placeholder_name = first_param.name(db).text(db);
             // If the placeholder isn't mapped to any repetition, it means it doesn't belong to any
             // consumed repetition.
```

### crates/cairo-lang-semantic/src/items/tests/enum
```diff
@@ -178,11 +178,6 @@ error[E0006]: Type not found.
     A: P,
        ^
 
-error[E2156]: Inline macro `MyEnum::A` not found.
- --> lib.cairo:4:1
-MyEnum::A(());
-^^^^^^^^^^^^^^
-
 //! > ==========================================================================
 
 //! > Test no ICE when an item-level macro call names an enum variant whose type is a generic enum with a trait bound.
```
