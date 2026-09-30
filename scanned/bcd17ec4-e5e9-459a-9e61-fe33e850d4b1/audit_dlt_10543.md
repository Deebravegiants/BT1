# [?] LS: fix missing module panic (#6172)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-08-08
Source: https://github.com/starkware-libs/cairo/commit/8ee7f426619b3d7b3355a950a16dc07964a86524
Type: security-commit

## Details
LS: fix missing module panic (#6172)

## Patch
### crates/cairo-lang-language-server/src/lib.rs
```diff
@@ -944,7 +944,7 @@ fn find_definition(
             let item = ResolvedGenericItem::Module(ModuleId::Submodule(submodule_id));
             return Some((
                 ResolvedItem::Generic(item.clone()),
-                resolved_generic_item_def(db, item),
+                resolved_generic_item_def(db, item)?,
             ));
         }
     }
@@ -959,7 +959,7 @@ fn find_definition(
         {
             return Some((
                 ResolvedItem::Generic(item.clone()),
-                resolved_generic_item_def(db, item),
+                resolved_generic_item_def(db, item)?,
             ));
         }
 
@@ -1001,9 +1001,9 @@ fn resolved_concrete_item_def(
 fn resolved_generic_item_def(
     db: &AnalysisDatabase,
     item: ResolvedGenericItem,
-) -> SyntaxStablePtrId {
+) -> Option<SyntaxStablePtrId> {
     let defs_db = db.upcast();
-    match item {
+    Some(match item {
         ResolvedGenericItem::GenericConstant(item) => item.untyped_stable_ptr(defs_db),
         ResolvedGenericItem::Module(module_id) => {
             // Check if the module is an inline submodule.
@@ -1012,11 +1012,11 @@ fn resolved_generic_item_def(
                     submodule_id.stable_ptr(defs_db).lookup(db.upcast()).body(db.upcast())
                 {
                     // Inline module.
-                    return submodule_id.stable_ptr().untyped();
+                    return Some(submodule_id.stable_ptr().untyped());
                 }
             }
-            let module_file = db.module_main_file(module_id).unwrap();
-            let file_syntax = db.file_module_syntax(module_file).unwrap();
+            let module_file = db.module_main_file(module_id).ok()?;
+            let file_syntax = db.file_module_syntax(module_file).ok()?;
             file_syntax.as_syntax_node().stable_ptr()
         }
         ResolvedGenericItem::GenericFunction(item) => {
@@ -1041,7 +1041,7 @@ fn resolved_generic_item_def(
             trait_function.stable_ptr(defs_db).untyped()
         }
         ResolvedGenericItem::Variable(var) => var.untyped_stable_ptr(defs_db),
-    }
+    })
 }
 
 fn is_cairo_file_path(file_path: &Url) -> bool {
```

### crates/cairo-lang-language-server/tests/e2e/hover.rs
```diff
@@ -13,6 +13,7 @@ cairo_lang_test_utils::test_file_test!(
     "tests/test_data/hover",
     {
         basic: "basic.txt",
+        missing_module: "missing_module.txt",
         partial: "partial.txt",
         starknet: "starknet.txt",
     },
```

### crates/cairo-lang-language-server/tests/test_data/hover/missing_module.txt
```diff
@@ -0,0 +1,38 @@
+//! > Hover
+
+//! > test_runner_name
+test_hover
+
+//! > cairo_project.toml
+[crate_roots]
+hello = "src"
+
+[config.global]
+edition = "2023_11"
+
+//! > cairo_code
+m<caret>od<caret> mis<caret>sing;
+
+//! > hover #0
+// = source context
+m<caret>od missing;
+// = highlight
+No highlight information.
+// = popover
+No hover information.
+
+//! > hover #1
+// = source context
+mod<caret> missing;
+// = highlight
+No highlight information.
+// = popover
+No hover information.
+
+//! > hover #2
+// = source context
+mod mis<caret>sing;
+// = highlight
+No highlight information.
+// = popover
+No hover information.
```
