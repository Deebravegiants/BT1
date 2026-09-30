# [?] fix: never panic in LSP inlay hints (#5534)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-07-18
Source: https://github.com/noir-lang/noir/commit/6b11445d9913e2953a96d09f86826aa652a233c4
Type: security-commit

## Details
fix: never panic in LSP inlay hints (#5534)

# Description

## Problem

I noticed that the inlay hint request would sometimes panic. This
happens if the request happens when a source file is being edited but
its cached version (in a FileMap) is not yet updated. Then, the editor
might pass a line range that's bigger than what's cached... producing a
panic.

In reality, the panic comes from the `codespan_lsp` crate: a function we
call returns `Result`, but there's an `unwrap()` inside it making it
panic instead of returning a Result.

## Summary

Here we don't depend on `codespan_lsp` for doing that, and instead copy
the logic but never panic.

## Additional Context

None.

## Documentation

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### Cargo.lock
```diff
@@ -2724,7 +2724,6 @@ dependencies = [
  "codespan-lsp",
  "fm",
  "fxhash",
- "lsp-types 0.88.0",
  "lsp-types 0.94.1",
  "nargo",
  "nargo_fmt",
```

### tooling/lsp/Cargo.toml
```diff
@@ -13,7 +13,6 @@ license.workspace = true
 acvm.workspace = true
 codespan-lsp.workspace = true
 lsp-types.workspace = true
-lsp_types_0_88_0 = { package = "lsp-types", version = "0.88.0" }
 nargo.workspace = true
 nargo_fmt.workspace = true
 nargo_toml.workspace = true
```

### tooling/lsp/src/requests/inlay_hint.rs
```diff
@@ -1,3 +1,4 @@
+use fm::codespan_files::Files;
 use std::future::{self, Future};
 
 use async_lsp::ResponseError;
@@ -39,23 +40,7 @@ pub(crate) fn on_inlay_hint_request(
             let source = file.source();
             let (parsed_moduled, _errors) = noirc_frontend::parse_program(source);
 
-            // The version of codespan_lsp is pretty old and relies on an old version of lsp-types.
-            // We can't downgrade because we need some types from the latest version, and there's
-            // no newer version of codespan_lsp... but we just need this type here, so we create
-            // a copy of a Range to get an older type.
-            let range = lsp_types_0_88_0::Range {
-                start: lsp_types_0_88_0::Position {
-                    line: params.range.start.line,
-                    character: params.range.start.character,
-                },
-                end: lsp_types_0_88_0::Position {
-                    line: params.range.end.line,
-                    character: params.range.end.character,
-                },
-            };
-
-            let span = codespan_lsp::range_to_byte_span(args.files, file_id, &range)
-                .ok()
+            let span = range_to_byte_span(args.files, file_id, &params.range)
                 .map(|range| Span::from(range.start as u32..range.end as u32));
 
             let mut collector = InlayHintCollector::new(args.files, file_id, args.interner, span);
@@ -596,4 +581,67 @@ mod inlay_hints_tests {
             panic!("Expected InlayHintLabel::LabelParts, got {:?}", inlay_hint.label);
         }
     }
+
+    #[test]
+    async fn test_do_not_panic_when_given_line_is_too_big() {
+        let inlay_hints = get_inlay_hints(0, 100000).await;
+        assert!(!inlay_hints.is_empty());
+    }
+}
+
+// These functions are copied from the codespan_lsp crate, except that they never panic
+// (the library will sometimes panic, so functions returning Result are not always accurate)
+
+fn range_to_byte_span(
+    files: &FileMap,
+    file_id: FileId,
+    range: &lsp_types::Range,
+) -> Option<std::ops::Range<usize>> {
+    Some(
+        position_to_byte_index(files, file_id, &range.start)?
+            ..position_to_byte_index(files, file_id, &range.end)?,
+    )
+}
+
+fn position_to_byte_index(
+    files: &FileMap,
+    file_id: FileId,
+    position: &lsp_types::Position,
+) -> Option<usize> {
+    let Ok(source) = files.source(file_id) else {
+        return None;
+    };
+
+    let Ok(line_span) = files.line_range(file_id, position.line as usize) else {
+        return None;
+    };
+    let line_str = source.get(line_span.clone())?;
+
+    let byte_offset = character_to_line_offset(line_str, position.character)?;
+
+    Some(line_span.start + byte_offset)
+}
+
+fn character_to_line_offset(line: &str, character: u32) -> Option<usize> {
+    let line_len = line.len();
+    let mut character_offset = 0;
+
+    let mut chars = line.chars();
+    while let Some(ch) = chars.next() {
+        if character_offset == character {
+            let chars_off = chars.as_str().len();
+            let ch_off = ch.len_utf8();
+
+            return Some(line_len - chars_off - ch_off);
+        }
+
+        character_offset += ch.len_utf16() as u32;
+    }
+
+    // Handle positions after the last character on the line
+    if character_offset == character {
+        Some(line_len)
+    } else {
+        None
+    }
 }
```
