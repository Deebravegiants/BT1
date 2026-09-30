# [?] Fix parser panics in edge cases (#5155)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-10-02
Source: https://github.com/FuelLabs/sway/commit/91046ebebd8288a91ac074b7654fbcbffbf23fee
Type: security-commit

## Details
Fix parser panics in edge cases (#5155)

## Description

Will partially address #5049

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

## Patch
### sway-parse/src/lib.rs
```diff
@@ -63,3 +63,48 @@ pub fn parse_module_kind(
     }
     parser.parse()
 }
+
+#[cfg(test)]
+mod tests {
+    use crate::*;
+
+    #[test]
+    fn parse_invalid() {
+        // just make sure these do not panic
+        let _res = parse_file(&Handler::default(), Arc::from("script; fn main(256߄"), None);
+        let _res = parse_file(
+            &Handler::default(),
+            Arc::from(
+                "script;
+            fn karr() {
+                let c: f828 =  0x00000000000000000000000vncifxp;
+            abi Zezybt {
+                #[mfzbezc, storage(r#
+            true }
+            }
+            cug",
+            ),
+            None,
+        );
+        let _res = parse_file(
+            &Handler::default(),
+            Arc::from(
+                "script;
+
+            corefn main() {
+                let a: b256 =  0x000>0000000scri s = \"flibrary I24;
+
+            use core::primitives::*;
+            use std::assert::assert;
+
+            ///\u{7eb}",
+            ),
+            None,
+        );
+        let _res = parse_file(
+            &Handler::default(),
+            Arc::from("script; \"\u{7eb}\u{7eb}"),
+            None,
+        );
+    }
+}
```

### sway-parse/src/parser.rs
```diff
@@ -49,8 +49,8 @@ impl<'a, 'e> Parser<'a, 'e> {
                     (self.full_span.end() + 1).saturating_sub(trim_offset),
                     self.full_span.source_id().cloned(),
                 )
+                .unwrap_or(Span::dummy())
             }
-            .unwrap(),
         };
         self.emit_error_with_span(kind, span)
     }
```

### sway-parse/src/token.rs
```diff
@@ -209,6 +209,15 @@ pub fn lex_commented(
                     character = next_character;
                     index = next_index;
                 }
+                if !(character.is_xid_start() || character == '_') {
+                    let kind = LexErrorKind::InvalidCharacter {
+                        position: index,
+                        character,
+                    };
+                    let span = span_one(&l, index, character);
+                    error(l.handler, LexError { kind, span });
+                    continue;
+                }
             }
 
             // Don't accept just `_` as an identifier.
@@ -466,10 +475,14 @@ fn lex_string(
                 },
             )
         };
-        let (next_index, next_character) = l
-            .stream
-            .next()
-            .ok_or_else(|| unclosed_string_lit(l, l.src.len() - 1))?;
+        let (next_index, next_character) = l.stream.next().ok_or_else(|| {
+            // last character may not be a unicode boundary
+            let mut end = l.src.len() - 1;
+            while !l.src.is_char_boundary(end) {
+                end -= 1;
+            }
+            unclosed_string_lit(l, end)
+        })?;
         parsed.push(match next_character {
             '\\' => parse_escape_code(l)
                 .map_err(|e| e.unwrap_or_else(|| unclosed_string_lit(l, l.src.len())))?,
```
