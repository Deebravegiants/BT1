# [?] Fix forc-fmt panic when lexing fails (#5011)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-08-25
Source: https://github.com/FuelLabs/sway/commit/985e05585410bd95a99515d357263fa524528da6
Type: security-commit

## Details
Fix forc-fmt panic when lexing fails (#5011)

## Description

Closes https://github.com/FuelLabs/sway/issues/5010

Now instead of a panic, the user sees this: 

<img width="836" alt="image"
src="https://github.com/FuelLabs/sway/assets/47993817/2da2e075-8a10-4ed4-8892-1c95cc42af63">

With debug logging they can see the compiler error, or they can simply
run the compiler.

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

## Patch
### forc-plugins/forc-doc/src/doc/descriptor.rs
```diff
@@ -66,7 +66,7 @@ impl Descriptor {
                             item_name,
                             code_str: parse::parse_format::<sway_ast::ItemStruct>(
                                 struct_decl.span.as_str(),
-                            ),
+                            )?,
                             attrs_opt: attrs_opt.clone(),
                             item_context: ItemContext {
                                 context_opt: context,
@@ -103,7 +103,7 @@ impl Descriptor {
                             item_name,
                             code_str: parse::parse_format::<sway_ast::ItemEnum>(
                                 enum_decl.span.as_str(),
-                            ),
+                            )?,
                             attrs_opt: attrs_opt.clone(),
                             item_context: ItemContext {
                                 context_opt: context,
@@ -151,7 +151,7 @@ impl Descriptor {
                             item_name,
                             code_str: parse::parse_format::<sway_ast::ItemTrait>(
                                 trait_decl.span.as_str(),
-                            ),
+                            )?,
                             attrs_opt: attrs_opt.clone(),
                             item_context: ItemContext {
                                 context_opt: context,
@@ -193,7 +193,7 @@ impl Descriptor {
                         module_info,
                         ty_decl: ty_decl.clone(),
                         item_name,
-                        code_str: parse::parse_format::<sway_ast::ItemAbi>(abi_decl.span.as_str()),
+                        code_str: parse::parse_format::<sway_ast::ItemAbi>(abi_decl.span.as_str())?,
                         attrs_opt: attrs_opt.clone(),
                         item_context: ItemContext {
                             context_opt: context,
@@ -228,7 +228,7 @@ impl Descriptor {
                         item_name,
                         code_str: parse::parse_format::<sway_ast::ItemStorage>(
                             storage_decl.span.as_str(),
-                        ),
+                        )?,
                         attrs_opt: attrs_opt.clone(),
                         item_context: ItemContext {
                             context_opt: context,
@@ -288,7 +288,7 @@ impl Descriptor {
                             item_name,
                             code_str: trim_fn_body(parse::parse_format::<sway_ast::ItemFn>(
                                 fn_decl.span.as_str(),
-                            )),
+                            )?),
                             attrs_opt: attrs_opt.clone(),
                             item_context: ItemContext {
                                 context_opt: None,
@@ -321,7 +321,7 @@ impl Descriptor {
                             item_name,
                             code_str: parse::parse_format::<sway_ast::ItemConst>(
                                 const_decl.span.as_str(),
-                            ),
+                            )?,
                             attrs_opt: attrs_opt.clone(),
                             item_context: ItemContext {
                                 context_opt: None,
```

### forc-plugins/forc-fmt/src/main.rs
```diff
@@ -11,9 +11,9 @@ use std::{
     sync::Arc,
 };
 use taplo::formatter as taplo_fmt;
-use tracing::{error, info};
+use tracing::{debug, error, info};
 
-use forc_tracing::{init_tracing_subscriber, println_green, println_red};
+use forc_tracing::{init_tracing_subscriber, println_error, println_green, println_red};
 use forc_util::{find_parent_manifest_dir, is_sway_file};
 use sway_core::{BuildConfig, BuildTarget};
 use sway_utils::{constants, get_sway_files};
@@ -43,7 +43,8 @@ pub struct App {
 fn main() {
     init_tracing_subscriber(Default::default());
     if let Err(err) = run() {
-        error!("Error: {:?}", err);
+        println_error("Formatting skipped due to error.");
+        println_error(&format!("{}", err));
         std::process::exit(1);
     }
 }
@@ -150,11 +151,10 @@ fn format_file(
                 return Ok(edited);
             }
             Err(err) => {
-                // there could still be Sway files that are not part of the build
-                error!(
-                    "\nThis file: {:?} is not part of the build\n{}\n",
-                    file, err
-                );
+                // TODO: Support formatting for incomplete/invalid sway code.
+                // https://github.com/FuelLabs/sway/issues/5012
+                debug!("{}", err);
+                bail!("Failed to compile: {:?}", file);
             }
         }
     }
```

### swayfmt/src/formatter/mod.rs
```diff
@@ -58,13 +58,11 @@ impl Formatter {
     }
 
     /// Collect a mapping of Span -> Comment from unformatted input.
-    pub fn with_comments_context(&mut self, src: &str) -> &mut Self {
-        let comments_context = CommentsContext::new(
-            CommentMap::from_src(Arc::from(src)).unwrap(),
-            src.to_string(),
-        );
+    pub fn with_comments_context(&mut self, src: &str) -> Result<&mut Self, FormatterError> {
+        let comments_context =
+            CommentsContext::new(CommentMap::from_src(Arc::from(src))?, src.to_string());
         self.comments_context = comments_context;
-        self
+        Ok(self)
     }
 
     pub fn format(
@@ -88,7 +86,7 @@ impl Formatter {
         // which will reduce the number of reallocations
         let mut raw_formatted_code = String::with_capacity(src.len());
 
-        self.with_comments_context(src);
+        self.with_comments_context(src)?;
 
         let module = parse_file(&self.source_engine, Arc::from(src), path.clone())?.value;
         module.format(&mut raw_formatted_code, self)?;
```

### swayfmt/src/parse.rs
```diff
@@ -1,4 +1,4 @@
-use crate::{error::ParseFileError, Formatter};
+use crate::{error::ParseFileError, Formatter, FormatterError};
 use std::path::PathBuf;
 use std::sync::Arc;
 use sway_ast::{attribute::Annotated, token::CommentedTokenStream, Module};
@@ -29,7 +29,9 @@ pub fn lex(input: &Arc<str>) -> Result<CommentedTokenStream, ParseFileError> {
     with_handler(|h| sway_parse::lex_commented(h, input, 0, input.len(), &None))
 }
 
-pub fn parse_format<P: sway_parse::Parse + crate::Format>(input: &str) -> String {
+pub fn parse_format<P: sway_parse::Parse + crate::Format>(
+    input: &str,
+) -> Result<String, FormatterError> {
     let parsed = with_handler(|handler| {
         let token_stream = sway_parse::lex(handler, &input.into(), 0, input.len(), None)?;
         sway_parse::Parser::new(handler, &token_stream).parse::<P>()
@@ -38,11 +40,11 @@ pub fn parse_format<P: sway_parse::Parse + crate::Format>(input: &str) -> String
 
     // Allow test cases that include comments.
     let mut formatter = Formatter::default();
-    formatter.with_comments_context(input);
+    formatter.with_comments_context(input)?;
 
     let mut buf = <_>::default();
     parsed.format(&mut buf, &mut formatter).unwrap();
-    buf
+    Ok(buf)
 }
 
 /// Partially parses an AST node that implements sway_parse::Parse.
```

### swayfmt/test_macros/src/lib.rs
```diff
@@ -75,7 +75,7 @@ macro_rules! fmt_test_inner {
         paste! {
             #[test]
             fn [<$scope _ $name>] () {
-                let formatted_code = crate::parse::parse_format::<$ty>($y);
+                let formatted_code = crate::parse::parse_format::<$ty>($y).unwrap();
                 let changeset = diff_lines(&formatted_code, $desired_output);
                 let count_of_updates = changeset.diff().len();
                 if count_of_updates != 0 {
```
