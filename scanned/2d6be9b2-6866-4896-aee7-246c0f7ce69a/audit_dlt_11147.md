# [?] Fix fmt panic for const inside trait (#5009)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2023-08-24
Source: https://github.com/FuelLabs/sway/commit/a7da1f2c94ae66f99220810c042af56bd5504cad
Type: security-commit

## Details
Fix fmt panic for const inside trait (#5009)

## Description

Closes https://github.com/FuelLabs/sway/issues/5008

The panic happened because the formatter was adding two `;`s after a
constant declaration inside of a trait.

I'm working toward the goal of making it so the formatter never panics,
even for sway files that do not compile.

I made it so, when a sway file does not compile, it does not cause the
formatter to panic. Now it prints an error message and returns that it
did not format anything with exit code 0.

I'm checking in this simple bash script that runs the formatter against
every sway project in the repo. Fixing this bug brought the # of panics
from ~35 down to 23.

I verified that the CI step that checks the formatting of sway docs is
still working.

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
### scripts/formatter/forc-fmt-all.sh
```diff
@@ -0,0 +1,22 @@
+#!/bin/bash
+
+# This script will format all sway projects in the current directory and all subdirectories.
+# This is useful for testing the formatter itself to make sure it's not panicking on any valid
+# sway projects and for checking that it's formatted output is correct.
+forc_manifests=`find . -name Forc.toml`
+let count=0
+let failed=0
+for f in $forc_manifests
+do
+    dir="${f%/*}"
+    forc fmt -p $dir
+    if [ $? -ne 0 ]
+    then
+        echo "Formatting failed: $dir"
+        let failed=failed+1
+    fi
+    let count=count+1
+done
+echo ""
+echo "Failed count: $failed"
+echo "Total count: $count"
```

### swayfmt/src/items/item_abi/mod.rs
```diff
@@ -11,6 +11,9 @@ use std::fmt::Write;
 use sway_ast::{keywords::Token, ItemAbi};
 use sway_types::{ast::Delimiter, Spanned};
 
+#[cfg(test)]
+mod tests;
+
 impl Format for ItemAbi {
     fn format(
         &self,
```

### swayfmt/src/items/item_abi/tests.rs
```diff
@@ -0,0 +1,41 @@
+use forc_tracing::{println_green, println_red};
+use paste::paste;
+use prettydiff::{basic::DiffOp, diff_lines};
+use test_macros::fmt_test_item;
+
+fmt_test_item!(abi_contains_constant
+"abi A {
+    const ID: u32;
+}",
+intermediate_whitespace
+"abi A {
+const ID: u32;
+}");
+
+fmt_test_item!(abi_contains_functions
+"abi A {
+    fn hi() -> bool;
+    fn hi2(hello: bool);
+    fn hi3(hello: bool) -> u64;
+}",
+intermediate_whitespace
+"abi A {
+fn hi() -> bool;
+    fn hi2(hello: bool);
+        fn hi3(hello: bool)-> u64;
+}");
+
+fmt_test_item!(abi_contains_comments
+"abi A {
+    fn hi() -> bool;
+    /// Function 2
+    fn hi2(hello: bool);
+    fn hi3(hello: bool) -> u64; // here too
+}",
+intermediate_whitespace
+"abi A {
+fn hi() -> bool;
+/// Function 2
+    fn hi2(hello: bool);
+        fn hi3(hello: bool)-> u64;// here too
+}");
```

### swayfmt/src/items/item_impl/tests.rs
```diff
@@ -104,3 +104,13 @@ fn foo(  ) {
 }
 }"
 );
+
+fmt_test_item!(impl_contains_const
+"impl ConstantId for Struct {
+    const ID: u32 = 5;
+}",
+intermediate_whitespace
+"impl ConstantId for Struct {
+    const ID: u32=5;
+}"
+);
```

### swayfmt/src/items/item_trait/mod.rs
```diff
@@ -83,13 +83,16 @@ impl Format for ItemTrait {
                     sway_ast::ItemTraitItem::Const(const_decl, _) => {
                         write!(formatted_code, "{}", formatter.indent_str()?,)?;
                         const_decl.format(formatted_code, formatter)?;
-                        writeln!(formatted_code, ";")?;
                     }
                     ItemTraitItem::Error(_, _) => {}
                 }
             }
         }
-        formatted_code.pop(); // pop last ending newline
+
+        if formatted_code.ends_with('\n') {
+            formatted_code.pop(); // pop last ending newline
+        }
+
         Self::close_curly_brace(formatted_code, formatter)?;
         if let Some(trait_defs) = &self.trait_defs_opt {
             write!(formatted_code, " ")?;
@@ -128,7 +131,7 @@ impl Format for ItemTraitItem {
             }
             ItemTraitItem::Const(const_decl, _) => {
                 const_decl.format(formatted_code, formatter)?;
-                writeln!(formatted_code, ";")?;
+                writeln!(formatted_code)?;
                 Ok(())
             }
             ItemTraitItem::Error(_, _) => Ok(()),
```

### swayfmt/src/items/item_trait/tests.rs
```diff
@@ -67,6 +67,15 @@ intermediate_whitespace
 }   "
 );
 
+fmt_test_item!(trait_contains_const
+"trait ConstantId {
+    const ID: u32 = 1;
+}",
+intermediate_whitespace
+"trait ConstantId {
+    const    ID: u32 = 1;
+}");
+
 fmt_test_item!(
 trait_normal_comment_two_fns
 "pub trait MyTrait {
@@ -75,7 +84,6 @@ trait_normal_comment_two_fns
     // Before b
     fn b(self);
 }",
-
 intermediate_whitespace
 "  pub   trait   MyTrait {
     // Before A
```
