# [?] fix(LSP): don't crash on broken function definition (#9441)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-08-11
Source: https://github.com/noir-lang/noir/commit/e54057dc34c7b675e329f23425ff25855e049358
Type: security-commit

## Details
fix(LSP): don't crash on broken function definition (#9441)

## Patch
### compiler/noirc_frontend/src/parser/parser.rs
```diff
@@ -220,7 +220,12 @@ impl<'a> Parser<'a> {
                     }
                 },
                 Some(Err(lexer_error)) => self.errors.push(lexer_error.into()),
-                None => return (eof_located_token(), last_comments),
+                None => {
+                    let end_span = Span::single_char(self.current_token_location.span.end());
+                    let end_location = Location::new(end_span, self.current_token_location.file);
+                    let end_token = LocatedToken::new(Token::EOF, end_location);
+                    return (end_token, last_comments);
+                }
             }
         }
     }
```

### tooling/lsp/src/requests/document_symbol.rs
```diff
@@ -509,14 +509,49 @@ impl Visitor for DocumentSymbolCollector<'_> {
 
 #[cfg(test)]
 mod document_symbol_tests {
-    use crate::test_utils;
+    use crate::{notifications::on_did_open_text_document, test_utils};
 
     use super::*;
     use async_lsp::lsp_types::{
-        PartialResultParams, Range, SymbolKind, TextDocumentIdentifier, WorkDoneProgressParams,
+        DidOpenTextDocumentParams, PartialResultParams, Range, SymbolKind, TextDocumentIdentifier,
+        TextDocumentItem, WorkDoneProgressParams,
     };
     use tokio::test;
 
+    async fn get_document_symbols(src: &str) -> Vec<DocumentSymbol> {
+        let (mut state, noir_text_document) = test_utils::init_lsp_server("document_symbol").await;
+
+        let _ = on_did_open_text_document(
+            &mut state,
+            DidOpenTextDocumentParams {
+                text_document: TextDocumentItem {
+                    uri: noir_text_document.clone(),
+                    language_id: "noir".to_string(),
+                    version: 0,
+                    text: src.to_string(),
+                },
+            },
+        );
+
+        let response = on_document_symbol_request(
+            &mut state,
+            DocumentSymbolParams {
+                text_document: TextDocumentIdentifier { uri: noir_text_document },
+                work_done_progress_params: WorkDoneProgressParams { work_done_token: None },
+                partial_result_params: PartialResultParams { partial_result_token: None },
+            },
+        )
+        .await
+        .expect("Could not execute on_document_symbol_request")
+        .unwrap();
+
+        let DocumentSymbolResponse::Nested(symbols) = response else {
+            panic!("Expected response to be nested");
+        };
+
+        symbols
+    }
+
     #[test]
     async fn test_document_symbol() {
         let (mut state, noir_text_document) = test_utils::init_lsp_server("document_symbol").await;
@@ -752,4 +787,26 @@ mod document_symbol_tests {
             ]
         );
     }
+
+    #[test]
+    async fn test_function_with_just_open_parentheses() {
+        let src = "fn main(\n";
+        let mut symbols = get_document_symbols(src).await;
+        assert_eq!(symbols.len(), 1);
+        let symbol = symbols.remove(0);
+        assert_eq!(
+            symbol.range,
+            Range {
+                start: Position { line: 0, character: 0 },
+                end: Position { line: 1, character: 0 },
+            }
+        );
+        assert_eq!(
+            symbol.selection_range,
+            Range {
+                start: Position { line: 0, character: 3 },
+                end: Position { line: 0, character: 7 },
+            }
+        );
+    }
 }
```
