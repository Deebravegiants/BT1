# [?] Avoid panics in `print!` and `format!` macros when missing parens (#5470)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-04-24
Source: https://github.com/starkware-libs/cairo/commit/d37d3c1e7546410aadf725c975d767d97f05a2dd
Type: security-commit

## Details
Avoid panics in `print!` and `format!` macros when missing parens (#5470)

## Patch
### crates/cairo-lang-semantic/src/expr/test_data/inline_macros
```diff
@@ -535,6 +535,9 @@ fn foo() {
 
     // Unused arguments.
     format!("{2}{0}", ba, 2, 1);
+
+    // No parens.
+    format!;
 }
 
 //! > function_name
@@ -543,6 +546,11 @@ foo
 //! > module_code
 
 //! > expected_diagnostics
+error: Missing tokens. Expected an argument list wrapped in either parentheses, brackets, or braces.
+ --> lib.cairo:32:12
+    format!;
+           ^
+
 error: Plugin diagnostic: Macro `write` does not support this bracket type.
  --> lib.cairo:5:12
     format!["{}", ba];
@@ -588,6 +596,16 @@ error: Plugin diagnostic: Unused argument.
     format!("{2}{0}", ba, 2, 1);
                           ^
 
+error: Plugin diagnostic: Macro `write` does not support this bracket type.
+ --> lib.cairo:32:12
+    format!;
+           ^
+
+error: Wrong number of arguments. Expected 1, found: 2
+ --> lib.cairo[format_macro]:3:5
+    core::result::ResultTrait::<(), core::fmt::Error>::unwrap(
+    ^********************************************************^
+
 warning[E0001]: Unused variable. Consider ignoring by prefixing with `_`.
  --> lib.cairo:2:9
     let ba: ByteArray = "hello";
@@ -635,6 +653,9 @@ fn foo() {
 
     // Unused arguments.
     print!("{2}{0}", ba, 2, 1);
+
+    // Missing parens.
+    print!;
 }
 
 //! > function_name
@@ -643,6 +664,11 @@ foo
 //! > module_code
 
 //! > expected_diagnostics
+error: Missing tokens. Expected an argument list wrapped in either parentheses, brackets, or braces.
+ --> lib.cairo:32:11
+    print!;
+          ^
+
 error: Plugin diagnostic: Macro `write` does not support this bracket type.
  --> lib.cairo:5:11
     print!["{}", ba];
@@ -688,6 +714,16 @@ error: Plugin diagnostic: Unused argument.
     print!("{2}{0}", ba, 2, 1);
                          ^
 
+error: Plugin diagnostic: Macro `write` does not support this bracket type.
+ --> lib.cairo:32:11
+    print!;
+          ^
+
+error: Wrong number of arguments. Expected 1, found: 2
+ --> lib.cairo[print_macro]:3:5
+    core::result::ResultTrait::<(), core::fmt::Error>::unwrap(
+    ^********************************************************^
+
 warning[E0001]: Unused variable. Consider ignoring by prefixing with `_`.
  --> lib.cairo:2:9
     let ba: ByteArray = "hello";
@@ -735,6 +771,9 @@ fn foo() {
 
     // Unused arguments.
     println!("{2}{0}", ba, 2, 1);
+    
+    // Missing parens.
+    println!;
 }
 
 //! > function_name
@@ -743,6 +782,11 @@ foo
 //! > module_code
 
 //! > expected_diagnostics
+error: Missing tokens. Expected an argument list wrapped in either parentheses, brackets, or braces.
+ --> lib.cairo:32:13
+    println!;
+            ^
+
 error: Plugin diagnostic: Macro `writeln` does not support this bracket type.
  --> lib.cairo:5:13
     println!["{}", ba];
@@ -788,6 +832,16 @@ error: Plugin diagnostic: Unused argument.
     println!("{2}{0}", ba, 2, 1);
                            ^
 
+error: Plugin diagnostic: Macro `writeln` does not support this bracket type.
+ --> lib.cairo:32:13
+    println!;
+            ^
+
+error: Wrong number of arguments. Expected 1, found: 2
+ --> lib.cairo[println_macro]:3:5
+    core::result::ResultTrait::<(), core::fmt::Error>::unwrap(
+    ^********************************************************^
+
 warning[E0001]: Unused variable. Consider ignoring by prefixing with `_`.
  --> lib.cairo:2:9
     let ba: ByteArray = "hello";
```

### crates/cairo-lang-semantic/src/inline_macros/format.rs
```diff
@@ -45,7 +45,9 @@ impl InlineMacroExprPlugin for FormatMacro {
                 ),
                 (
                     "args".to_string(),
-                    RewriteNode::new_trimmed(arguments.arg_list(db).unwrap().as_syntax_node()),
+                    arguments.arg_list(db).map_or_else(RewriteNode::empty, |n| {
+                        RewriteNode::new_trimmed(n.as_syntax_node())
+                    }),
                 ),
             ]
             .into(),
```

### crates/cairo-lang-semantic/src/inline_macros/print.rs
```diff
@@ -73,7 +73,9 @@ fn generate_code_inner(
             ),
             (
                 "args".to_string(),
-                RewriteNode::new_trimmed(arguments.arg_list(db).unwrap().as_syntax_node()),
+                arguments.arg_list(db).map_or_else(RewriteNode::empty, |n| {
+                    RewriteNode::new_trimmed(n.as_syntax_node())
+                }),
             ),
         ]
         .into(),
```
