# [?] fix: Prevent panic in semantic highlighting for unknown token types (#7189)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2025-05-22
Source: https://github.com/FuelLabs/sway/commit/a70254b279893a9871170988a4c308a7373d8dc5
Type: security-commit

## Details
fix: Prevent panic in semantic highlighting for unknown token types (#7189)

## Description
Previously, the language server would panic if it encountered a
`SymbolKind` that mapped to a `SemanticTokenType` not present in the
`SUPPORTED_TYPES` array. This was due to an `unwrap()` call in the
`type_index` function.

This PR addresses the issue by:
Adding `SemanticTokenType::new("traitType")` to the `SUPPORTED_TYPES`
array, which was the specific missing type causing a crash when opening
`sway-lib-std/src/iterator.sw`.

Modifying `type_index` to return `Option<u32>` instead of `u32`,
removing the `unwrap()`.

closes #7188

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

## Patch
### sway-lsp/src/capabilities/semantic_tokens.rs
```diff
@@ -47,10 +47,13 @@ pub fn semantic_tokens(tokens_sorted: &[&RefMulti<TokenIdent, Token>]) -> Semant
     for entry in tokens_sorted {
         let (ident, token) = entry.pair();
         let ty = semantic_token_type(&token.kind);
-        let token_index = type_index(&ty);
-        // TODO - improve with modifiers
-        let modifier_bitset = 0;
-        builder.push(ident.range, token_index, modifier_bitset);
+        if let Some(token_index) = type_index(&ty) {
+            // TODO - improve with modifiers
+            let modifier_bitset = 0;
+            builder.push(ident.range, token_index, modifier_bitset);
+        } else {
+            tracing::error!("Unsupported token type: {:?} for token: {:#?}", ty, token);
+        }
     }
     builder.build()
 }
@@ -151,6 +154,7 @@ pub(crate) const SUPPORTED_TYPES: &[SemanticTokenType] = &[
     SemanticTokenType::new("selfKeyword"),
     SemanticTokenType::new("selfTypeKeyword"),
     SemanticTokenType::new("typeAlias"),
+    SemanticTokenType::new("traitType"),
 ];
 
 pub(crate) const SUPPORTED_MODIFIERS: &[SemanticTokenModifier] = &[
@@ -194,6 +198,9 @@ fn semantic_token_type(kind: &SymbolKind) -> SemanticTokenType {
     }
 }
 
-fn type_index(ty: &SemanticTokenType) -> u32 {
-    SUPPORTED_TYPES.iter().position(|it| it == ty).unwrap() as u32
+fn type_index(ty: &SemanticTokenType) -> Option<u32> {
+    SUPPORTED_TYPES
+        .iter()
+        .position(|it| it == ty)
+        .map(|x| x as u32)
 }
```

### sway-lsp/tests/lib.rs
```diff
@@ -156,6 +156,30 @@ fn did_open() {
     });
 }
 
+#[test]
+fn did_open_all_std_lib_files() {
+    run_async!({
+        let (mut service, _) = LspService::new(ServerState::new);
+        let files = sway_utils::helpers::get_sway_files(std_lib_dir().join("src"));
+        for file in files {
+            eprintln!("opening file: {:?}", file.as_path());
+
+            // If the workspace is not initialized, we need to initialize it
+            // Otherwise, we can just open the file
+            let uri = if service.inner().sync_workspace.get().is_none() {
+                init_and_open(&mut service, file.to_path_buf()).await
+            } else {
+                open(service.inner(), file.to_path_buf()).await
+            };
+
+            // Make sure that semantic tokens are successfully returned for the file
+            let semantic_tokens = lsp::get_semantic_tokens_full(service.inner(), &uri).await;
+            assert!(!semantic_tokens.data.is_empty());
+        }
+        shutdown_and_exit(&mut service).await;
+    });
+}
+
 // Opens all members in the examples workspace and assert that we are able to return semantic tokens for each workspace member.
 // This test is expected to run for a while although should be much faster once https://github.com/FuelLabs/sway/pull/7139 is merged.
 #[test]
```

### sway-lsp/tests/utils/src/lib.rs
```diff
@@ -58,6 +58,10 @@ pub fn e2e_test_dir() -> PathBuf {
         .join("struct_field_access")
 }
 
+pub fn std_lib_dir() -> PathBuf {
+    sway_workspace_dir().join("sway-lib-std")
+}
+
 pub fn runnables_test_dir() -> PathBuf {
     test_fixtures_dir().join("runnables")
 }
```
