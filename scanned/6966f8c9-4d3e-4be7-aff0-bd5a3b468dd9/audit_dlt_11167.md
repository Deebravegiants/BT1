# [?] assembly-syntax: harden duplicate conflicts without resolver panics

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-03-16
Source: https://github.com/0xMiden/miden-vm/commit/47bbb4f9fcd68c11e3ccb0fe7c38591df27fa9c0
Type: security-commit

## Details
assembly-syntax: harden duplicate conflicts without resolver panics

## Patch
### crates/assembly-syntax/src/ast/item/resolver/error.rs
```diff
@@ -87,18 +87,6 @@ impl SymbolResolutionError {
         }
     }
 
-    pub fn duplicate_symbol(
-        span: SourceSpan,
-        symbol: Arc<str>,
-        source_manager: &dyn SourceManager,
-    ) -> Self {
-        Self::DuplicateSymbol {
-            span,
-            source_file: source_manager.get(span.source_id()).ok(),
-            symbol,
-        }
-    }
-
     pub fn invalid_alias_target(
         span: SourceSpan,
         referrer: SourceSpan,
```

### crates/assembly-syntax/src/ast/item/resolver/symbol_table.rs
```diff
@@ -149,10 +149,13 @@ impl LocalSymbolTable {
                 LocalSymbol::Import { name, .. } => name.clone().into_inner(),
             };
 
-            if let Some(prev) = symbols.insert(name.clone(), id) {
-                panic!(
+            if let Some(prev) = symbols.get(&name).copied() {
+                debug_assert!(
+                    false,
                     "duplicate symbol '{name}' reached local resolver construction (previous={prev:?}, current={id:?})"
                 );
+            } else {
+                symbols.insert(name.clone(), id);
             }
             items.push(symbol);
         }
@@ -503,10 +506,37 @@ mod tests {
         }
     }
 
+    #[cfg(debug_assertions)]
     #[test]
     #[should_panic(expected = "duplicate symbol 'dup' reached local resolver construction")]
     fn local_symbol_table_rejects_duplicate_symbols() {
         let source_manager: Arc<dyn SourceManager> = Arc::new(DefaultSourceManager::default());
         let _table = LocalSymbolTable::new(DuplicateSymbolsForInvariantTest, source_manager);
     }
+
+    #[test]
+    fn local_symbol_table_duplicate_symbols_have_explicit_behavior() {
+        use std::panic::{AssertUnwindSafe, catch_unwind};
+
+        let source_manager: Arc<dyn SourceManager> = Arc::new(DefaultSourceManager::default());
+        let result = catch_unwind(AssertUnwindSafe(|| {
+            LocalSymbolTable::new(DuplicateSymbolsForInvariantTest, source_manager)
+        }));
+
+        if cfg!(debug_assertions) {
+            assert!(
+                result.is_err(),
+                "debug builds should panic when duplicates reach local resolver construction"
+            );
+        } else {
+            let table = result.expect("release builds should not panic on duplicate symbols");
+            let resolved = table
+                .get(Span::unknown("dup"))
+                .expect("release behavior should keep a deterministic symbol mapping");
+            match resolved {
+                SymbolResolution::Local(id) => assert_eq!(id.into_inner(), ItemIndex::new(0)),
+                other => panic!("expected local symbol resolution, got {other:?}"),
+            }
+        }
+    }
 }
```

### crates/assembly-syntax/src/ast/module.rs
```diff
@@ -293,38 +293,42 @@ impl Module {
     pub fn define_procedure(
         &mut self,
         procedure: Procedure,
-        source_manager: Arc<dyn SourceManager>,
+        _source_manager: Arc<dyn SourceManager>,
     ) -> Result<(), SemanticAnalysisError> {
-        let name = procedure.name();
-        let name = Span::new(name.span(), name.as_str());
-        if let Ok(prev) = self.resolve(name, source_manager) {
-            let prev_span = prev.span();
-            Err(SemanticAnalysisError::SymbolConflict { span: procedure.span(), prev_span })
-        } else {
-            self.items.push(Export::Procedure(procedure));
-            Ok(())
+        if let Some(prev) =
+            self.items.iter().find(|item| item.name().as_str() == procedure.name().as_str())
+        {
+            return Err(SemanticAnalysisError::SymbolConflict {
+                span: procedure.span(),
+                prev_span: prev.name().span(),
+            });
         }
+        self.items.push(Export::Procedure(procedure));
+        Ok(())
     }
 
     /// Defines an item alias, raising an error if the alias is invalid, or conflicts with a
     /// previous definition
     pub fn define_alias(
         &mut self,
         item: Alias,
-        source_manager: Arc<dyn SourceManager>,
+        _source_manager: Arc<dyn SourceManager>,
     ) -> Result<(), SemanticAnalysisError> {
         if self.is_kernel() && item.visibility().is_public() {
             return Err(SemanticAnalysisError::ReexportFromKernel { span: item.span() });
         }
-        let name = item.name();
-        let name = Span::new(name.span(), name.as_str());
-        if let Ok(prev) = self.resolve(name, source_manager) {
-            let prev_span = prev.span();
-            Err(SemanticAnalysisError::SymbolConflict { span: item.span(), prev_span })
-        } else {
-            self.items.push(Export::Alias(item));
-            Ok(())
+        if let Some(prev) = self
+            .items
+            .iter()
+            .find(|existing| existing.name().as_str() == item.name().as_str())
+        {
+            return Err(SemanticAnalysisError::SymbolConflict {
+                span: item.name().span(),
+                prev_span: prev.name().span(),
+            });
         }
+        self.items.push(Export::Alias(item));
+        Ok(())
     }
 }
 
```

### crates/assembly-syntax/src/sema/tests.rs
```diff
@@ -1,7 +1,17 @@
+use alloc::{
+    string::{String, ToString},
+    sync::Arc,
+};
+
+use miden_debug_types::{Span, Spanned};
+
 use crate::{
-    MAX_REPEAT_COUNT,
-    ast::{Constant, Export, Module},
+    MAX_REPEAT_COUNT, Path,
+    ast::{
+        Constant, ConstantExpr, Export, Module, ModuleKind, TypeAlias, TypeExpr, Visibility, types,
+    },
     diagnostics::reporting::PrintDiagnostic,
+    sema::SemanticAnalysisError,
     testing::SyntaxTestContext,
 };
 
@@ -59,6 +69,119 @@ fn assert_symbol_conflict(error: &miden_utils_diagnostics::Report, symbol: &str)
     );
 }
 
+#[derive(Clone, Copy, Debug, PartialEq, Eq)]
+enum DefinitionKind {
+    Alias,
+    Procedure,
+    Constant,
+    Type,
+}
+
+impl DefinitionKind {
+    fn declaration(self, symbol: &str) -> String {
+        match self {
+            Self::Alias => format!("use ::dep::{}", quote_ident_if_needed(symbol)),
+            Self::Procedure => {
+                format!("proc {}\n    nop\nend", quote_ident_if_needed(symbol))
+            },
+            Self::Constant => format!("const {symbol} = 1"),
+            Self::Type => format!("type {} = felt", quote_ident_if_needed(symbol)),
+        }
+    }
+}
+
+fn quote_ident_if_needed(symbol: &str) -> String {
+    let is_bare_ident = symbol
+        .bytes()
+        .all(|b| b == b'_' || b.is_ascii_lowercase() || b.is_ascii_digit());
+    if is_bare_ident {
+        symbol.to_string()
+    } else {
+        format!("\"{symbol}\"")
+    }
+}
+
+fn assert_cross_kind_conflict(first: DefinitionKind, second: DefinitionKind) {
+    if is_constant_type_pair(first, second) {
+        assert_constant_type_conflict_via_module_api(first, second);
+        return;
+    }
+
+    let symbol = if matches!(first, DefinitionKind::Constant)
+        || matches!(second, DefinitionKind::Constant)
+    {
+        "THING"
+    } else {
+        "thing"
+    };
+    let context = SyntaxTestContext::default();
+    let source = format!("{}\n{}\n", first.declaration(symbol), second.declaration(symbol));
+    let message = format!("expected symbol conflict during analysis ({first:?} then {second:?})");
+    let error = context.parse_module(source).expect_err(&message);
+    let rendered = format!("{}", PrintDiagnostic::new_without_color(&error));
+    if error.downcast_ref::<crate::sema::SyntaxError>().is_none() {
+        panic!("expected SyntaxError ({first:?} then {second:?}), got: {rendered}");
+    }
+    assert_symbol_conflict(&error, symbol);
+    assert!(rendered.contains("symbol conflict"));
+    assert!(rendered.contains(symbol));
+}
+
+fn is_constant_type_pair(first: DefinitionKind, second: DefinitionKind) -> bool {
+    matches!(
+        (first, second),
+        (DefinitionKind::Constant, DefinitionKind::Type)
+            | (DefinitionKind::Type, DefinitionKind::Constant)
+    )
+}
+
+fn assert_constant_type_conflict_via_module_api(first: DefinitionKind, second: DefinitionKind) {
+    let symbol = "dup";
+    let mut module = Module::new(ModuleKind::Library, Path::new("mod"));
+
+    match first {
+        DefinitionKind::Constant => module
+            .define_constant(constant_with_name(symbol))
+            .expect("expected initial constant definition to succeed"),
+        DefinitionKind::Type => module
+            .define_type(type_alias_with_name(symbol))
+            .expect("expected initial type definition to succeed"),
+        _ => unreachable!("only constant/type pairs should use this helper"),
+    }
+
+    let result = match second {
+        DefinitionKind::Constant => module.define_constant(constant_with_name(symbol)),
+        DefinitionKind::Type => module.define_type(type_alias_with_name(symbol)),
+        _ => unreachable!("only constant/type pairs should use this helper"),
+    };
+    assert!(
+        matches!(result, Err(SemanticAnalysisError::SymbolConflict { .. })),
+        "expected SymbolConflict when defining {second:?} after {first:?}, got {result:?}"
+    );
+}
+
+fn ident_with_name(name: &str) -> crate::ast::Ident {
+    crate::ast::Ident::from_raw_parts(Span::unknown(Arc::<str>::from(name)))
+}
+
+fn constant_with_name(name: &str) -> Constant {
+    let ident = ident_with_name(name);
+    Constant::new(
+        ident.span(),
+        Visibility::Private,
+        ident,
+        ConstantExpr::String(ident_with_name("value")),
+    )
+}
+
+fn type_alias_with_name(name: &str) -> TypeAlias {
+    TypeAlias::new(
+        Visibility::Private,
+        ident_with_name(name),
+        TypeExpr::Primitive(Span::unknown(types::Type::Felt)),
+    )
+}
+
 #[test]
 fn repeat_count_zero_rejected_in_analysis() {
     let context = SyntaxTestContext::default();
@@ -145,73 +268,19 @@ pub const ACCOUNT_ID_SUFFIX_OFFSET = ACCOUNT_ID_AND_NONCE_OFFSET + 2
 }
 
 #[test]
-fn define_alias_detects_cross_kind_duplicate_with_type() {
-    let context = SyntaxTestContext::default();
-    let error = context
-        .parse_module(
-            r#"
-type thing = felt
-use ::dep::thing
-"#,
-        )
-        .expect_err("expected conflicting type/alias names to be rejected during analysis");
-    assert_symbol_conflict(&error, "thing");
-    let rendered = format!("{}", PrintDiagnostic::new_without_color(&error));
-    assert!(rendered.contains("symbol conflict"));
-    assert!(rendered.contains("thing"));
-}
-
-#[test]
-fn define_procedure_detects_cross_kind_duplicate_with_type() {
-    let context = SyntaxTestContext::default();
-    let error = context
-        .parse_module(
-            r#"
-type thing = felt
-proc thing
-    nop
-end
-"#,
-        )
-        .expect_err("expected conflicting type/procedure names to be rejected during analysis");
-    assert_symbol_conflict(&error, "thing");
-    let rendered = format!("{}", PrintDiagnostic::new_without_color(&error));
-    assert!(rendered.contains("symbol conflict"));
-    assert!(rendered.contains("thing"));
-}
-
-#[test]
-fn define_constant_detects_cross_kind_duplicate_with_alias() {
-    let context = SyntaxTestContext::default();
-    let error = context
-        .parse_module(
-            r#"
-use ::dep::"THING"
-const THING = 1
-"#,
-        )
-        .expect_err("expected conflicting alias/constant names to be rejected during analysis");
-    assert_symbol_conflict(&error, "THING");
-    let rendered = format!("{}", PrintDiagnostic::new_without_color(&error));
-    assert!(rendered.contains("symbol conflict"));
-    assert!(rendered.contains("THING"));
-}
-
-#[test]
-fn define_type_detects_cross_kind_duplicate_with_procedure() {
-    let context = SyntaxTestContext::default();
-    let error = context
-        .parse_module(
-            r#"
-proc thing
-    nop
-end
-type thing = felt
-"#,
-        )
-        .expect_err("expected conflicting procedure/type names to be rejected during analysis");
-    assert_symbol_conflict(&error, "thing");
-    let rendered = format!("{}", PrintDiagnostic::new_without_color(&error));
-    assert!(rendered.contains("symbol conflict"));
-    assert!(rendered.contains("thing"));
+fn define_items_detect_cross_kind_duplicates_for_all_pairs_and_orders() {
+    let kinds = [
+        DefinitionKind::Alias,
+        DefinitionKind::Procedure,
+        DefinitionKind::Constant,
+        DefinitionKind::Type,
+    ];
+    for first in kinds {
+        for second in kinds {
+            if first == second {
+                continue;
+            }
+            assert_cross_kind_conflict(first, second);
+        }
+    }
 }
```
