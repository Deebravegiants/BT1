# [?] LS: fix panics in `lsp_helper` (#6168)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-08-08
Source: https://github.com/starkware-libs/cairo/commit/28f78f6f1d4522194f52eb2487a0ae0b6a2a8020
Type: security-commit

## Details
LS: fix panics in `lsp_helper` (#6168)

## Patch
### crates/cairo-lang-language-server/src/ide/code_actions/add_missing_trait.rs
```diff
@@ -78,7 +78,7 @@ fn missing_traits_actions(
         module_start_offset.position_in_file(db.upcast(), file_id).unwrap().to_lsp();
     let relevant_methods = find_methods_for_type(db, resolver, ty, stable_ptr);
     let current_module = db.find_module_containing_node(node)?;
-    let module_visible_traits = db.visible_traits_from_module(current_module);
+    let module_visible_traits = db.visible_traits_from_module(current_module)?;
     let mut code_actions = vec![];
     for method in relevant_methods {
         let method_name = method.name(db.upcast());
```

### crates/cairo-lang-language-server/src/ide/completion/completions.rs
```diff
@@ -274,7 +274,7 @@ pub fn completion_for_method(
 
     // If the trait is not in scope, add a use statement.
     if !module_has_trait(db, module_id, trait_id)? {
-        if let Some(trait_path) = db.visible_traits_from_module(module_id).get(&trait_id) {
+        if let Some(trait_path) = db.visible_traits_from_module(module_id)?.get(&trait_id) {
             additional_text_edits.push(TextEdit {
                 range: Range::new(position, position),
                 new_text: format!("use {};\n", trait_path),
```

### crates/cairo-lang-semantic/src/db.rs
```diff
@@ -1514,7 +1514,7 @@ pub trait SemanticGroup:
     fn visible_traits_from_module(
         &self,
         module_id: ModuleId,
-    ) -> Arc<OrderedHashMap<TraitId, String>>;
+    ) -> Option<Arc<OrderedHashMap<TraitId, String>>>;
     /// Returns all visible traits in a module, alongside a visible use path to the trait.
     /// `user_module_id` is the module from which the traits are should be visible. If
     /// `include_parent` is true, the parent module of `module_id` is also considered.
```

### crates/cairo-lang-semantic/src/lsp_helpers.rs
```diff
@@ -116,11 +116,11 @@ fn visible_traits_in_module_ex(
     visited_modules.insert(module_id);
     let mut modules_to_visit = vec![];
     // Add traits and traverse modules imported into the current module.
-    for use_id in db.module_uses_ids(module_id).unwrap().iter().copied() {
+    for use_id in db.module_uses_ids(module_id).ok()?.iter().copied() {
         if !is_visible(use_id.name(db.upcast()))? {
             continue;
         }
-        let resolved_item = db.use_resolved_item(use_id).unwrap();
+        let resolved_item = db.use_resolved_item(use_id).ok()?;
         match resolved_item {
             ResolvedGenericItem::Module(inner_module_id) => {
                 modules_to_visit.push(inner_module_id);
@@ -132,14 +132,14 @@ fn visible_traits_in_module_ex(
         }
     }
     // Traverse the submodules of the current module.
-    for submodule_id in db.module_submodules_ids(module_id).unwrap().iter().copied() {
+    for submodule_id in db.module_submodules_ids(module_id).ok()?.iter().copied() {
         if !is_visible(submodule_id.name(db.upcast()))? {
             continue;
         }
         modules_to_visit.push(ModuleId::Submodule(submodule_id));
     }
     // Add the traits of the current module.
-    for trait_id in db.module_traits_ids(module_id).unwrap().iter().copied() {
+    for trait_id in db.module_traits_ids(module_id).ok()?.iter().copied() {
         if !is_visible(trait_id.name(db.upcast()))? {
             continue;
         }
@@ -202,7 +202,7 @@ pub fn visible_traits_in_crate(
 pub fn visible_traits_from_module(
     db: &dyn SemanticGroup,
     module_id: ModuleId,
-) -> Arc<OrderedHashMap<TraitId, String>> {
+) -> Option<Arc<OrderedHashMap<TraitId, String>>> {
     let mut current_top_module = module_id;
     while let ModuleId::Submodule(submodule_id) = current_top_module {
         current_top_module = submodule_id.parent_module(db.upcast());
@@ -211,11 +211,10 @@ pub fn visible_traits_from_module(
         ModuleId::CrateRoot(crate_id) => crate_id,
         ModuleId::Submodule(_) => unreachable!("current module is not a top-level module"),
     };
-    let edition = db.crate_config(current_crate_id).unwrap().settings.edition;
+    let edition = db.crate_config(current_crate_id)?.settings.edition;
     let prelude_submodule_name = edition.prelude_submodule_name();
     let core_prelude_submodule = core_submodule(db, "prelude");
-    let prelude_submodule =
-        get_submodule(db, core_prelude_submodule, prelude_submodule_name).unwrap();
+    let prelude_submodule = get_submodule(db, core_prelude_submodule, prelude_submodule_name)?;
 
     let mut module_visible_traits = Vec::new();
     module_visible_traits.extend_from_slice(
@@ -243,5 +242,5 @@ pub fn visible_traits_from_module(
             }
         }
     }
-    result.into()
+    Some(result.into())
 }
```
