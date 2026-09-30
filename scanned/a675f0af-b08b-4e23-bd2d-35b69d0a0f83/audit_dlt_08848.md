# [?] fix: emit diagnostic for unsupported items in statement position instead of panicking (#9806)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-05
Source: https://github.com/starkware-libs/cairo/commit/0b3d35db60e76a4e872924e8d8dc5ca68c18b7f9
Type: security-commit

## Details
fix: emit diagnostic for unsupported items in statement position instead of panicking (#9806)

## Patch
### crates/cairo-lang-semantic/src/diagnostic.rs
```diff
@@ -1199,6 +1199,9 @@ impl<'db> DiagnosticEntry<'db> for SemanticDiagnostic<'db> {
             SemanticDiagnosticKind::OnlyTypeOrConstParamsInNegImpl => {
                 "Negative impls may only use type or const generic parameters.".into()
             }
+            SemanticDiagnosticKind::UnsupportedItemInStatement => {
+                "Item not supported as a statement.".into()
+            }
         }
     }
     fn location(&self, db: &'db dyn Database) -> SpanInFile<'db> {
@@ -1462,6 +1465,7 @@ impl<'db> DiagnosticEntry<'db> for SemanticDiagnostic<'db> {
             SemanticDiagnosticKind::UserDefinedInlineMacrosDisabled => error_code!(E2194),
             SemanticDiagnosticKind::NonNeverLetElseType => error_code!(E2195),
             SemanticDiagnosticKind::OnlyTypeOrConstParamsInNegImpl => error_code!(E2196),
+            SemanticDiagnosticKind::UnsupportedItemInStatement => error_code!(E2197),
             SemanticDiagnosticKind::PluginDiagnostic(diag) => {
                 diag.error_code.unwrap_or(error_code!(E2200))
             }
@@ -1881,6 +1885,7 @@ pub enum SemanticDiagnosticKind<'db> {
     UserDefinedInlineMacrosDisabled,
     NonNeverLetElseType,
     OnlyTypeOrConstParamsInNegImpl,
+    UnsupportedItemInStatement,
 }
 
 /// The kind of an expression with multiple possible return types.
```

### crates/cairo-lang-semantic/src/expr/compute.rs
```diff
@@ -4758,28 +4758,25 @@ pub fn compute_and_append_statement_semantic<'db>(
                         }
                     }
                 }
-                ast::ModuleItem::Module(_) => {
-                    unreachable!("Modules are not supported inside a function.")
-                }
-                ast::ModuleItem::FreeFunction(_) => {
-                    unreachable!("FreeFunction type not supported.")
-                }
-                ast::ModuleItem::ExternFunction(_) => {
-                    unreachable!("ExternFunction type not supported.")
-                }
-                ast::ModuleItem::ExternType(_) => unreachable!("ExternType type not supported."),
-                ast::ModuleItem::Trait(_) => unreachable!("Trait type not supported."),
-                ast::ModuleItem::Impl(_) => unreachable!("Impl type not supported."),
-                ast::ModuleItem::ImplAlias(_) => unreachable!("ImplAlias type not supported."),
-                ast::ModuleItem::Struct(_) => unreachable!("Struct type not supported."),
-                ast::ModuleItem::Enum(_) => unreachable!("Enum type not supported."),
-                ast::ModuleItem::TypeAlias(_) => unreachable!("TypeAlias type not supported."),
-                ast::ModuleItem::InlineMacro(_) => unreachable!("InlineMacro type not supported."),
-                ast::ModuleItem::HeaderDoc(_) => unreachable!("HeaderDoc type not supported."),
-                ast::ModuleItem::MacroDeclaration(_) => {
-                    unreachable!("MacroDeclaration type not supported.")
+                ast::ModuleItem::Module(_)
+                | ast::ModuleItem::FreeFunction(_)
+                | ast::ModuleItem::ExternFunction(_)
+                | ast::ModuleItem::ExternType(_)
+                | ast::ModuleItem::Trait(_)
+                | ast::ModuleItem::Impl(_)
+                | ast::ModuleItem::ImplAlias(_)
+                | ast::ModuleItem::Struct(_)
+                | ast::ModuleItem::Enum(_)
+                | ast::ModuleItem::TypeAlias(_)
+                | ast::ModuleItem::InlineMacro(_)
+                | ast::ModuleItem::HeaderDoc(_)
+                | ast::ModuleItem::MacroDeclaration(_) => {
+                    return Err(ctx
+                        .diagnostics
+                        .report(stmt_item_syntax.stable_ptr(db), UnsupportedItemInStatement));
                 }
-                ast::ModuleItem::Missing(_) => unreachable!("Missing type not supported."),
+                // Diagnostics reported on syntax level already.
+                ast::ModuleItem::Missing(_) => return Err(skip_diagnostic()),
             }
             statements.push(ctx.arenas.statements.alloc(semantic::Statement::Item(
                 semantic::StatementItem { stable_ptr: syntax.stable_ptr(db) },
```

### crates/cairo-lang-semantic/src/expr/test_data/statements
```diff
@@ -219,6 +219,29 @@ fn unstable_function_with_note() -> felt252 {
 
 //! > ==========================================================================
 
+//! > Type alias as statement inside a function body.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo() {
+    type MyAlias = felt252;
+}
+
+//! > function_name
+foo
+
+//! > module_code
+
+//! > expected_diagnostics
+error[E2197]: Item not supported as a statement.
+ --> lib.cairo:2:5
+    type MyAlias = felt252;
+    ^^^^^^^^^^^^^^^^^^^^^^^
+
+//! > ==========================================================================
+
 //! > Declarative macro with parameter missing kind specifier.
 
 //! > test_runner_name
@@ -247,4 +270,3 @@ error[E2158]: No matching rule found in inline macro `m`.
  --> lib.cairo:5:5
     m!(1);
     ^^^^^
-
```
