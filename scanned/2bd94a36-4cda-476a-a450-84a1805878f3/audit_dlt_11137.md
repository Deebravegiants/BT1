# [?] Fixes unreachable macro crashing compiler. (#6362)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-08-07
Source: https://github.com/FuelLabs/sway/commit/23320256612b85ad433ef315e789c40869af7897
Type: security-commit

## Details
Fixes unreachable macro crashing compiler. (#6362)

## Description

In case of a bad input given to the lexer, it is possible to generate an
AST with invalid ImplItem tuples.

This fix replaces the unreachable macro with an CompileError::Internal.
This allows the user to see the lexer errors and fix them which will
also address the new errors.

Fixes #6339.

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

Co-authored-by: IGI-111 <igi-111@protonmail.com>
Co-authored-by: João Matos <joao@tritao.eu>

## Patch
### sway-core/src/semantic_analysis/ast_node/declaration/impl_trait.rs
```diff
@@ -489,7 +489,12 @@ impl TyImplSelfOrTrait {
                             (ImplItem::Type(_type_decl), TyTraitItem::Type(_decl_ref)) => {
                                 // Already processed.
                             }
-                            _ => unreachable!(),
+                            _ => {
+                                handler.emit_err(CompileError::Internal(
+                                    "Unexpected ImplItem tuple.",
+                                    Span::dummy(),
+                                ));
+                            }
                         }
                     }
 
@@ -542,7 +547,12 @@ impl TyImplSelfOrTrait {
                             (ImplItem::Type(_type_decl), TyTraitItem::Type(_decl_ref)) => {
                                 // Already processed.
                             }
-                            _ => unreachable!(),
+                            _ => {
+                                handler.emit_err(CompileError::Internal(
+                                    "Unexpected ImplItem tuple.",
+                                    Span::dummy(),
+                                ));
+                            }
                         }
                     }
 
```

### test/src/e2e_vm_tests/test_programs/should_fail/lexer_errors/.gitignore
```diff
@@ -0,0 +1,2 @@
+out
+target
```

### test/src/e2e_vm_tests/test_programs/should_fail/lexer_errors/Forc.lock
```diff
@@ -0,0 +1,8 @@
+[[package]]
+name = "core"
+source = "path+from-root-082ED3C1A64D1BB4"
+
+[[package]]
+name = "lexer_errors"
+source = "member"
+dependencies = ["core"]
```

### test/src/e2e_vm_tests/test_programs/should_fail/lexer_errors/Forc.toml
```diff
@@ -0,0 +1,9 @@
+[project]
+authors = ["Fuel Labs <contact@fuel.sh>"]
+entry = "main.sw"
+license = "Apache-2.0"
+name = "lexer_errors"
+implicit-std = false
+
+[dependencies]
+core = { path = "../../../../../../sway-lib-core" }
```

### test/src/e2e_vm_tests/test_programs/should_fail/lexer_errors/src/main.sw
```diff
@@ -0,0 +1,15 @@
+library;
+
+pub struct R {
+    a: u32,
+}
+
+impl R {
+    pub fn from_str(new: i32) {
+p() {
+  :Script => {
+   c = ZERO_B256;
+    ), }
+}
+
+const OFFSET = 0;
\ No newline at end of file
```

### test/src/e2e_vm_tests/test_programs/should_fail/lexer_errors/test.toml
```diff
@@ -0,0 +1,8 @@
+category = "fail"
+
+# check: $()error
+# check: $()mismatched delimiters
+
+# check: $()error
+# check: $()impl R {
+# nextln: $()unclosed delimiter
\ No newline at end of file
```
