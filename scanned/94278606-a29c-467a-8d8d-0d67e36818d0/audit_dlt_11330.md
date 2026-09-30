# [?] fix: don't crash on AsTraitPath with empty path (#6454)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-11-05
Source: https://github.com/noir-lang/noir/commit/fc72dcdf3e8eeff73f72756e7ab87dddf2920657
Type: security-commit

## Details
fix: don't crash on AsTraitPath with empty path (#6454)

## Patch
### compiler/noirc_frontend/src/ast/statement.rs
```diff
@@ -454,9 +454,8 @@ impl Path {
         self.last_segment().ident
     }
 
-    pub fn first_name(&self) -> &str {
-        assert!(!self.segments.is_empty());
-        &self.segments.first().unwrap().ident.0.contents
+    pub fn first_name(&self) -> Option<&str> {
+        self.segments.first().map(|segment| segment.ident.0.contents.as_str())
     }
 
     pub fn last_name(&self) -> &str {
```

### compiler/noirc_frontend/src/elaborator/path_resolution.rs
```diff
@@ -107,7 +107,7 @@ impl<'context> Elaborator<'context> {
     pub(super) fn resolve_path(&mut self, mut path: Path) -> PathResolutionResult {
         let mut module_id = self.module_id();
 
-        if path.kind == PathKind::Plain && path.first_name() == SELF_TYPE_NAME {
+        if path.kind == PathKind::Plain && path.first_name() == Some(SELF_TYPE_NAME) {
             if let Some(Type::Struct(struct_type, _)) = &self.self_type {
                 let struct_type = struct_type.borrow();
                 if path.segments.len() == 1 {
```

### compiler/noirc_frontend/src/elaborator/types.rs
```diff
@@ -192,7 +192,7 @@ impl<'context> Elaborator<'context> {
 
     // Resolve Self::Foo to an associated type on the current trait or trait impl
     fn lookup_associated_type_on_self(&self, path: &Path) -> Option<Type> {
-        if path.segments.len() == 2 && path.first_name() == SELF_TYPE_NAME {
+        if path.segments.len() == 2 && path.first_name() == Some(SELF_TYPE_NAME) {
             if let Some(trait_id) = self.current_trait {
                 let the_trait = self.interner.get_trait(trait_id);
                 if let Some(typ) = the_trait.get_associated_type(path.last_name()) {
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -61,6 +61,15 @@ pub(crate) fn remove_experimental_warnings(errors: &mut Vec<(CompilationError, F
 }
 
 pub(crate) fn get_program(src: &str) -> (ParsedModule, Context, Vec<(CompilationError, FileId)>) {
+    get_program_with_maybe_parser_errors(
+        src, false, // allow parser errors
+    )
+}
+
+pub(crate) fn get_program_with_maybe_parser_errors(
+    src: &str,
+    allow_parser_errors: bool,
+) -> (ParsedModule, Context, Vec<(CompilationError, FileId)>) {
     let root = std::path::Path::new("/");
     let fm = FileManager::new(root);
 
@@ -73,7 +82,7 @@ pub(crate) fn get_program(src: &str) -> (ParsedModule, Context, Vec<(Compilation
     let mut errors = vecmap(parser_errors, |e| (e.into(), root_file_id));
     remove_experimental_warnings(&mut errors);
 
-    if !has_parser_error(&errors) {
+    if allow_parser_errors || !has_parser_error(&errors) {
         let inner_attributes: Vec<SecondaryAttribute> = program
             .items
             .iter()
```

### compiler/noirc_frontend/src/tests/traits.rs
```diff
@@ -1,6 +1,6 @@
 use crate::hir::def_collector::dc_crate::CompilationError;
 use crate::hir::resolution::errors::ResolverError;
-use crate::tests::get_program_errors;
+use crate::tests::{get_program_errors, get_program_with_maybe_parser_errors};
 
 use super::assert_no_errors;
 
@@ -390,3 +390,19 @@ fn trait_bounds_which_are_dependent_on_generic_types_are_resolved_correctly() {
     "#;
     assert_no_errors(src);
 }
+
+#[test]
+fn does_not_crash_on_as_trait_path_with_empty_path() {
+    let src = r#"
+        struct Foo {
+            x: <N>,
+        }
+
+        fn main() {}
+    "#;
+
+    let (_, _, errors) = get_program_with_maybe_parser_errors(
+        src, true, // allow parser errors
+    );
+    assert!(!errors.is_empty());
+}
```
