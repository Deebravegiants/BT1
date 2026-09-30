# [?] Fix panic in forc-fmt with special chars (#5014)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-08-28
Source: https://github.com/FuelLabs/sway/commit/0c045be3295008adfdf1c1162161153011ad212e
Type: security-commit

## Details
Fix panic in forc-fmt with special chars (#5014)

## Description

Closes https://github.com/FuelLabs/sway/issues/5013

## Checklist

- [x] I have linked to any relevant issues.
- [ ] I have commented my code, particularly in hard-to-understand
areas.
- [ ] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] I have added tests that prove my fix is effective or that my
feature works.
- [ ] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [ ] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [ ] I have requested a review from the relevant team or maintainers.

---------

Co-authored-by: Joshua Batty <joshpbatty@gmail.com>

## Patch
### swayfmt/src/comments.rs
```diff
@@ -1,8 +1,3 @@
-use ropey::Rope;
-use std::{fmt::Write, ops::Range};
-use sway_ast::token::{Comment, CommentKind};
-use sway_types::{Span, Spanned};
-
 use crate::{
     formatter::FormattedCode,
     parse::parse_snippet,
@@ -12,6 +7,10 @@ use crate::{
     },
     Format, Formatter, FormatterError,
 };
+use ropey::Rope;
+use std::{fmt::Write, ops::Range};
+use sway_ast::token::{Comment, CommentKind};
+use sway_types::{Span, Spanned};
 
 pub type UnformattedCode = String;
 
@@ -151,9 +150,7 @@ pub fn rewrite_with_comments<T: sway_parse::Parse + Format + LeafSpans>(
     let mut offset = 0;
     let mut to_rewrite = formatted_code[last_formatted..].to_string();
 
-    let formatted_leaf_spans = parse_snippet::<T>(&formatted_code[last_formatted..])
-        .unwrap()
-        .leaf_spans();
+    let formatted_leaf_spans = parse_snippet::<T>(&formatted_code[last_formatted..])?.leaf_spans();
 
     let mut previous_unformatted_leaf_span = unformatted_leaf_spans
         .first()
@@ -352,13 +349,17 @@ fn insert_after_span(
         };
 
         // Insert the actual comment(s).
-        src_rope.insert(from.end + offset, &comment_str);
+        src_rope
+            .try_insert(from.end + offset, &comment_str)
+            .map_err(|_| FormatterError::CommentError)?;
 
         formatted_code.clear();
         formatted_code.push_str(&src_rope.to_string());
     }
 
-    Ok(comment_str.len())
+    // In order to handle special characters, we return the number of characters rather than
+    // the size of the string.
+    Ok(comment_str.chars().count())
 }
 
 #[cfg(test)]
```

### swayfmt/src/items/item_fn/tests.rs
```diff
@@ -120,3 +120,15 @@ intermediate_whitespace
     }
 }"
 );
+
+fmt_test_item!(fn_comments_special_chars
+"fn comments_special_chars() {
+    // this ↓↓↓↓↓   
+    let val = 1; // this is a normal comment
+}",
+intermediate_whitespace
+"fn comments_special_chars() {
+    // this ↓↓↓↓↓   
+    let val = 1;      // this is a normal comment
+}"
+);
```

### swayfmt/src/parse.rs
```diff
@@ -35,15 +35,14 @@ pub fn parse_format<P: sway_parse::Parse + crate::Format>(
     let parsed = with_handler(|handler| {
         let token_stream = sway_parse::lex(handler, &input.into(), 0, input.len(), None)?;
         sway_parse::Parser::new(handler, &token_stream).parse::<P>()
-    })
-    .unwrap();
+    })?;
 
     // Allow test cases that include comments.
     let mut formatter = Formatter::default();
     formatter.with_comments_context(input)?;
 
     let mut buf = <_>::default();
-    parsed.format(&mut buf, &mut formatter).unwrap();
+    parsed.format(&mut buf, &mut formatter)?;
     Ok(buf)
 }
 
```

### swayfmt/src/utils/map/newline.rs
```diff
@@ -278,7 +278,11 @@ fn insert_after_span(
         format_newline_sequence(&newline_sequence, threshold)
     )?;
     let mut src_rope = Rope::from_str(formatted_code);
-    src_rope.insert(at, &sequence_string);
+
+    src_rope
+        .try_insert(at, &sequence_string)
+        .map_err(|_| FormatterError::NewlineSequenceError)?;
+
     formatted_code.clear();
     formatted_code.push_str(&src_rope.to_string());
     Ok(sequence_string.len())
```
