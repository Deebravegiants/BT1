# [?] Fix range OOB bug in the language server (#6314)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-07-31
Source: https://github.com/FuelLabs/sway/commit/0245223413d603cd46db408550192c72968fca39
Type: security-commit

## Details
Fix range OOB bug in the language server (#6314)

## Description
This PR fixes a crash in the language server caused by an out-of-bounds
error when using `rope`. It replaces the `ropey` crate with a custom
implementation using `String` and `Vec<usize>` for line offsets. This
change improves robustness and prevents panics when handling rapid text
changes.

Closes #6313

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [x] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [x] If my change requires substantial documentation changes, I have
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
### Cargo.lock
```diff
@@ -6901,7 +6901,6 @@ dependencies = [
  "rayon",
  "rayon-cond",
  "regex",
- "ropey",
  "serde",
  "serde_json",
  "sway-ast",
```

### sway-lsp/Cargo.toml
```diff
@@ -25,7 +25,6 @@ proc-macro2 = "1.0.5"
 quote = "1.0.9"
 rayon = "1.5.0"
 rayon-cond = "0.3"
-ropey = "1.2"
 serde = { version = "1.0", features = ["derive"] }
 serde_json = "1.0.60"
 sway-ast = { version = "0.62.0", path = "../sway-ast" }
```

### sway-lsp/src/core/document.rs
```diff
@@ -1,4 +1,3 @@
-#![allow(dead_code)]
 use std::sync::Arc;
 
 use crate::{
@@ -8,114 +7,110 @@ use crate::{
 use dashmap::DashMap;
 use forc_util::fs_locking::PidFileLocking;
 use lsp_types::{Position, Range, TextDocumentContentChangeEvent, Url};
-use ropey::Rope;
 use tokio::{fs::File, io::AsyncWriteExt};
 
 #[derive(Debug, Clone)]
 pub struct TextDocument {
-    #[allow(dead_code)]
-    language_id: String,
-    #[allow(dead_code)]
     version: i32,
     uri: String,
-    content: Rope,
+    content: String,
+    line_offsets: Vec<usize>,
 }
 
 impl TextDocument {
     pub async fn build_from_path(path: &str) -> Result<Self, DocumentError> {
         tokio::fs::read_to_string(path)
             .await
-            .map(|content| Self {
-                language_id: "sway".into(),
-                version: 1,
-                uri: path.into(),
-                content: Rope::from_str(&content),
+            .map(|content| {
+                let line_offsets = TextDocument::calculate_line_offsets(&content);
+                Self {
+                    version: 1,
+                    uri: path.into(),
+                    content,
+                    line_offsets,
+                }
+            })
+            .map_err(|e| match e.kind() {
+                std::io::ErrorKind::NotFound => {
+                    DocumentError::DocumentNotFound { path: path.into() }
+                }
+                std::io::ErrorKind::PermissionDenied => {
+                    DocumentError::PermissionDenied { path: path.into() }
+                }
+                _ => DocumentError::IOError {
+                    path: path.into(),
+                    error: e.to_string(),
+                },
             })
-            .map_err(|_| DocumentError::DocumentNotFound { path: path.into() })
     }
 
     pub fn get_uri(&self) -> &str {
         &self.uri
     }
 
-    pub fn get_line(&self, line: usize) -> String {
-        self.content.line(line).to_string()
+    pub fn get_text(&self) -> &str {
+        &self.content
     }
 
-    pub fn apply_change(&mut self, change: &TextDocumentContentChangeEvent) {
-        let edit = self.build_edit(change);
-
-        self.content.remove(edit.start_index..edit.end_index);
-        self.content.insert(edit.start_index, edit.change_text);
-    }
-
-    pub fn get_text(&self) -> String {
-        self.content.to_string()
+    pub fn get_line(&self, line: usize) -> &str {
+        let start = self
+            .line_offsets
+            .get(line)
+            .copied()
+            .unwrap_or(self.content.len());
+        let end = self
+            .line_offsets
+            .get(line + 1)
+            .copied()
+            .unwrap_or(self.content.len());
+        &self.content[start..end]
     }
-}
 
-// private methods
-impl TextDocument {
-    fn build_edit<'change>(
-        &self,
-        change: &'change TextDocumentContentChangeEvent,
-    ) -> EditText<'change> {
-        let change_text = change.text.as_str();
-        let text_bytes = change_text.as_bytes();
-        let text_end_byte_index = text_bytes.len();
-
-        let range = if let Some(range) = change.range {
-            range
+    pub fn apply_change(
+        &mut self,
+        change: &TextDocumentContentChangeEvent,
+    ) -> Result<(), DocumentError> {
+        if let Some(range) = change.range {
+            self.validate_range(range)?;
+            let start_index = self.position_to_index(range.start);
+            let end_index = self.position_to_index(range.end);
+            self.content
+                .replace_range(start_index..end_index, &change.text);
         } else {
-            let start = self.byte_to_position(0);
-            let end = self.byte_to_position(text_end_byte_index);
-            Range { start, end }
-        };
-
-        let start_index = self.position_to_index(range.start);
-        let end_index = self.position_to_index(range.end);
-
-        EditText {
-            start_index,
-            end_index,
-            change_text,
+            self.content.clone_from(&change.text);
         }
+        self.line_offsets = Self::calculate_line_offsets(&self.content);
+        self.version += 1;
+        Ok(())
     }
 
-    fn byte_to_position(&self, byte_index: usize) -> Position {
-        let line_index = self.content.byte_to_line(byte_index);
-
-        let line_utf16_cu_index = {
-            let char_index = self.content.line_to_char(line_index);
-            self.content.char_to_utf16_cu(char_index)
-        };
-
-        let character_utf16_cu_index = {
-            let char_index = self.content.byte_to_char(byte_index);
-            self.content.char_to_utf16_cu(char_index)
-        };
-
-        let character = character_utf16_cu_index - line_utf16_cu_index;
-
-        Position::new(line_index as u32, character as u32)
+    fn validate_range(&self, range: Range) -> Result<(), DocumentError> {
+        let start = self.position_to_index(range.start);
+        let end = self.position_to_index(range.end);
+        if start > end || end > self.content.len() {
+            return Err(DocumentError::InvalidRange { range });
+        }
+        Ok(())
     }
 
     fn position_to_index(&self, position: Position) -> usize {
-        let row_index = position.line as usize;
-        let column_index = position.character as usize;
-
-        let row_char_index = self.content.line_to_char(row_index);
-        let column_char_index = self.content.utf16_cu_to_char(column_index);
-
-        row_char_index + column_char_index
+        let line_offset = self
+            .line_offsets
+            .get(position.line as usize)
+            .copied()
+            .unwrap_or(self.content.len());
+        line_offset + position.character as usize
     }
-}
 
-#[derive(Debug)]
-struct EditText<'text> {
-    start_index: usize,
-    end_index: usize,
-    change_text: &'text str,
+    fn calculate_line_offsets(text: &str) -> Vec<usize> {
+        let mut offsets = vec![0];
+        for (i, c) in text.char_indices() {
+            if c == '\n' {
+                offsets.push(i + 1);
+            }
+        }
+        offsets
+    }
 }
 
 pub struct Documents(DashMap<String, TextDocument>);
@@ -145,11 +140,7 @@ impl Documents {
         uri: &Url,
         changes: &[TextDocumentContentChangeEvent],
     ) -> Result<(), LanguageServerError> {
-        let src = self.update_text_document(uri, changes).ok_or_else(|| {
-            DocumentError::DocumentNotFound {
-                path: uri.path().to_string(),
-            }
-        })?;
+        let src = self.update_text_document(uri, changes)?;
 
         let mut file =
             File::create(uri.path())
@@ -169,30 +160,33 @@ impl Documents {
         Ok(())
     }
 
-    /// Get the document at the given [Url].
-    pub fn get_text_document(&self, url: &Url) -> Result<TextDocument, DocumentError> {
-        self.try_get(url.path())
-            .try_unwrap()
-            .ok_or_else(|| DocumentError::DocumentNotFound {
-                path: url.path().to_string(),
-            })
-            .map(|document| document.clone())
-    }
-
     /// Update the document at the given [Url] with the Vec of changes returned by the client.
     pub fn update_text_document(
         &self,
-        url: &Url,
+        uri: &Url,
         changes: &[TextDocumentContentChangeEvent],
-    ) -> Option<String> {
-        self.try_get_mut(url.path())
+    ) -> Result<String, DocumentError> {
+        self.try_get_mut(uri.path())
             .try_unwrap()
-            .map(|mut document| {
+            .ok_or_else(|| DocumentError::DocumentNotFound {
+                path: uri.path().to_string(),
+            })
+            .and_then(|mut document| {
                 for change in changes {
-                    document.apply_change(change);
+                    document.apply_change(change)?;
                 }
-                document.get_text()
+                Ok(document.get_text().to_string())
+            })
+    }
+
+    /// Get the document at the given [Url].
+    pub fn get_text_document(&self, url: &Url) -> Result<TextDocument, DocumentError> {
+        self.try_get(url.path())
+            .try_unwrap()
+            .ok_or_else(|| DocumentError::DocumentNotFound {
+                path: url.path().to_string(),
             })
+            .map(|document| document.clone())
     }
 
     /// Remove the text document.
@@ -281,6 +275,11 @@ mod tests {
         let path = get_absolute_path("sway-lsp/tests/fixtures/cats.txt");
         let result = TextDocument::build_from_path(&path).await;
         assert!(result.is_ok(), "result = {result:?}");
+        let document = result.unwrap();
+        assert_eq!(document.version, 1);
+        assert_eq!(document.uri, path);
+        assert!(!document.content.is_empty());
+        assert!(!document.line_offsets.is_empty());
     }
 
     #[tokio::test]
@@ -315,4 +314,51 @@ mod tests {
             .expect_err("expected DocumentAlreadyStored");
         assert_eq!(result, DocumentError::DocumentAlreadyStored { path });
     }
+
+    #[test]
+    fn get_line_returns_correct_line() {
+        let content = "line1\nline2\nline3".to_string();
+        let line_offsets = TextDocument::calculate_line_offsets(&content);
+        let document = TextDocument {
+            version: 1,
+            uri: "test.sw".into(),
+            content,
+            line_offsets,
+        };
+        assert_eq!(document.get_line(0), "line1\n");
+        assert_eq!(document.get_line(1), "line2\n");
+        assert_eq!(document.get_line(2), "line3");
+    }
+
+    #[test]
+    fn apply_change_updates_content_correctly() {
+        let content = "Hello, world!".to_string();
+        let line_offsets = TextDocument::calculate_line_offsets(&content);
+        let mut document = TextDocument {
+            version: 1,
+            uri: "test.sw".into(),
+            content,
+            line_offsets,
+        };
+        let change = TextDocumentContentChangeEvent {
+            range: Some(Range::new(Position::new(0, 7), Position::new(0, 12))),
+            range_length: None,
+            text: "Rust".into(),
+        };
+        document.apply_change(&change).unwrap();
+        assert_eq!(document.get_text(), "Hello, Rust!");
+    }
+
+    #[test]
+    fn position_to_index_works_correctly() {
+        let content = "line1\nline2\nline3".to_string();
+        let line_offsets = TextDocument::calculate_line_offsets(&content);
+        let document = TextDocument {
+            version: 1,
+            uri: "test.sw".into(),
+            content,
+            line_offsets,
+        };
+        assert_eq!(document.position_to_index(Position::new(1, 2)), 8);
+    }
 }
```

### sway-lsp/src/error.rs
```diff
@@ -1,3 +1,4 @@
+use lsp_types::Range;
 use swayfmt::FormatterError;
 use thiserror::Error;
 
@@ -46,6 +47,13 @@ pub enum DocumentError {
     UnableToWriteFile { path: String, err: String },
     #[error("File wasn't able to be removed at path {:?} : {:?}", path, err)]
     UnableToRemoveFile { path: String, err: String },
+
+    #[error("Permission denied for path {:?}", path)]
+    PermissionDenied { path: String },
+    #[error("IO error for path {:?} : {:?}", path, error)]
+    IOError { path: String, error: String },
+    #[error("Invalid range {:?}", range)]
+    InvalidRange { range: Range },
 }
 
 #[derive(Debug, Error, PartialEq, Eq)]
```
