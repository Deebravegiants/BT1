# [?] fix(parser): don't panic on $(...) without operator in macro calls (#9993) (#10005)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-05-31
Source: https://github.com/starkware-libs/cairo/commit/ef0410ad1d5e59c3a4f201a7a089d439df70aa63
Type: security-commit

## Details
fix(parser): don't panic on $(...) without operator in macro calls (#9993) (#10005)

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### crates/cairo-lang-parser/src/parser.rs
```diff
@@ -1775,43 +1775,14 @@ impl<'a, 'mt> Parser<'a, 'mt> {
     }
 
     /// Either parses a leaf of the tree (i.e. any non-parenthesis token) or an inner node (i.e. a
-    /// parenthesized stream of tokens).
+    /// parenthesized stream of tokens). Call-site token trees are unstructured: `$`, `?`, `+`, `*`
+    /// have no special meaning here and are just leaves. The semantic layer decides whether the
+    /// shape matches any rule of the target macro.
     fn parse_token_tree(&mut self) -> TokenTreeGreen<'a> {
         match self.peek().kind {
             SyntaxKind::TerminalLBrace
             | SyntaxKind::TerminalLParen
             | SyntaxKind::TerminalLBrack => self.parse_token_tree_node().into(),
-            SyntaxKind::TerminalDollar => {
-                let dollar: TerminalDollarGreen<'_> = self.take::<TerminalDollar<'_>>();
-                match self.peek().kind {
-                    SyntaxKind::TerminalLParen => {
-                        let lparen = self.take::<TerminalLParen<'_>>();
-                        let elements = TokenList::new_green(self.db, &self.parse_token_list());
-                        let rparen = self.parse_token::<TerminalRParen<'_>>();
-                        let separator: OptionTerminalCommaGreen<'_> = match self.peek().kind {
-                            SyntaxKind::TerminalComma => self.take::<TerminalComma<'_>>().into(),
-                            _ => OptionTerminalCommaEmpty::new_green(self.db).into(),
-                        };
-                        let operator = match self.peek().kind {
-                            SyntaxKind::TerminalQuestionMark => {
-                                self.take::<TerminalQuestionMark<'_>>().into()
-                            }
-                            SyntaxKind::TerminalPlus => self.take::<TerminalPlus<'_>>().into(),
-                            SyntaxKind::TerminalMul => self.take::<TerminalMul<'_>>().into(),
-                            _ => unreachable!(),
-                        };
-                        TokenTreeRepetition::new_green(
-                            self.db, dollar, lparen, elements, rparen, separator, operator,
-                        )
-                        .into()
-                    }
-                    SyntaxKind::TerminalIdentifier => {
-                        let identifier = self.take::<TerminalIdentifier<'_>>();
-                        TokenTreeParam::new_green(self.db, dollar, identifier).into()
-                    }
-                    _ => self.parse_token_tree_leaf().into(),
-                }
-            }
             _ => self.parse_token_tree_leaf().into(),
         }
     }
```

### crates/cairo-lang-parser/src/parser_test_data/partial_trees/inline_macro
```diff
@@ -442,3 +442,45 @@ error[E1001]: Missing token ';'.
     │       │       └── semicolon: Missing
     │       └── rbrace (kind: TokenRBrace): '}'
     └── eof (kind: TokenEndOfFile).
+
+//! > ==========================================================================
+
+//! > Test inline macro call with `$(...)` — `$` is just a leaf token at the call site.
+
+//! > test_runner_name
+test_partial_parser_tree(expect_diagnostics: false)
+
+//! > cairo_code
+fn main() -> u32 {
+    foo!($(x))
+}
+
+//! > top_level_kind
+ExprInlineMacro
+
+//! > ignored_kinds
+
+//! > expected_diagnostics
+
+//! > expected_tree
+└── Top level kind: ExprInlineMacro
+    ├── path (kind: ExprPath)
+    │   ├── dollar (kind: OptionTerminalDollarEmpty) []
+    │   └── segments (kind: ExprPathInner)
+    │       └── item #0 (kind: PathSegmentSimple)
+    │           └── ident (kind: TokenIdentifier): 'foo'
+    ├── bang (kind: TokenNot): '!'
+    └── arguments (kind: TokenTreeNode)
+        └── subtree (kind: ParenthesizedTokenTree)
+            ├── lparen (kind: TokenLParen): '('
+            ├── tokens (kind: TokenList)
+            │   ├── child #0 (kind: TokenTreeLeaf)
+            │   │   └── leaf (kind: TokenDollar): '$'
+            │   └── child #1 (kind: TokenTreeNode)
+            │       └── subtree (kind: ParenthesizedTokenTree)
+            │           ├── lparen (kind: TokenLParen): '('
+            │           ├── tokens (kind: TokenList)
+            │           │   └── child #0 (kind: TokenTreeLeaf)
+            │           │       └── leaf (kind: TokenIdentifier): 'x'
+            │           └── rparen (kind: TokenRParen): ')'
+            └── rparen (kind: TokenRParen): ')'
```

### crates/cairo-lang-parser/src/parser_test_data/partial_trees/macro_declaration
```diff
@@ -325,3 +325,74 @@ error[E1031]: Missing macro repetition operator. Expected `?`, `+`, or `*` after
     │       │       └── semicolon (kind: TokenSemicolon): ';'
     │       └── rbrace (kind: TokenRBrace): '}'
     └── eof (kind: TokenEndOfFile).
+
+//! > ==========================================================================
+
+//! > Test macro definition with body repetition missing operator.
+
+//! > test_runner_name
+test_partial_parser_tree(expect_diagnostics: true)
+
+//! > cairo_code
+macro macro_name {
+    ($($x:expr),*) => { $($x) };
+}
+
+//! > top_level_kind
+
+//! > ignored_kinds
+
+//! > expected_diagnostics
+error[E1031]: Missing macro repetition operator. Expected `?`, `+`, or `*` after `$(...)`.
+ --> dummy_file.cairo:2:30
+    ($($x:expr),*) => { $($x) };
+                             ^
+
+//! > expected_tree
+└── root (kind: SyntaxFile)
+    ├── items (kind: ModuleItemList)
+    │   └── child #0 (kind: ItemMacroDeclaration)
+    │       ├── attributes (kind: AttributeList) []
+    │       ├── visibility (kind: VisibilityDefault) []
+    │       ├── macro_kw (kind: TokenMacro): 'macro'
+    │       ├── name (kind: TokenIdentifier): 'macro_name'
+    │       ├── lbrace (kind: TokenLBrace): '{'
+    │       ├── rules (kind: MacroRulesList)
+    │       │   └── child #0 (kind: MacroRule)
+    │       │       ├── lhs (kind: ParenthesizedMacro)
+    │       │       │   ├── lparen (kind: TokenLParen): '('
+    │       │       │   ├── elements (kind: MacroElements)
+    │       │       │   │   └── child #0 (kind: MacroRepetition)
+    │       │       │   │       ├── dollar (kind: TokenDollar): '$'
+    │       │       │   │       ├── lparen (kind: TokenLParen): '('
+    │       │       │   │       ├── elements (kind: MacroElements)
+    │       │       │   │       │   └── child #0 (kind: MacroParam)
+    │       │       │   │       │       ├── dollar (kind: TokenDollar): '$'
+    │       │       │   │       │       ├── name (kind: TokenIdentifier): 'x'
+    │       │       │   │       │       └── kind (kind: ParamKind)
+    │       │       │   │       │           ├── colon (kind: TokenColon): ':'
+    │       │       │   │       │           └── kind (kind: ParamExpr)
+    │       │       │   │       │               └── expr (kind: TokenIdentifier): 'expr'
+    │       │       │   │       ├── rparen (kind: TokenRParen): ')'
+    │       │       │   │       ├── separator (kind: TokenComma): ','
+    │       │       │   │       └── operator (kind: TokenMul): '*'
+    │       │       │   └── rparen (kind: TokenRParen): ')'
+    │       │       ├── fat_arrow (kind: TokenMatchArrow): '=>'
+    │       │       ├── rhs (kind: BracedMacro)
+    │       │       │   ├── lbrace (kind: TokenLBrace): '{'
+    │       │       │   ├── elements (kind: MacroElements)
+    │       │       │   │   └── child #0 (kind: MacroRepetition)
+    │       │       │   │       ├── dollar (kind: TokenDollar): '$'
+    │       │       │   │       ├── lparen (kind: TokenLParen): '('
+    │       │       │   │       ├── elements (kind: MacroElements)
+    │       │       │   │       │   └── child #0 (kind: MacroParam)
+    │       │       │   │       │       ├── dollar (kind: TokenDollar): '$'
+    │       │       │   │       │       ├── name (kind: TokenIdentifier): 'x'
+    │       │       │   │       │       └── kind (kind: OptionParamKindEmpty) []
+    │       │       │   │       ├── rparen (kind: TokenRParen): ')'
+    │       │       │   │       ├── separator (kind: OptionTerminalCommaEmpty) []
+    │       │       │   │       └── operator: Missing []
+    │       │       │   └── rbrace (kind: TokenRBrace): '}'
+    │       │       └── semicolon (kind: TokenSemicolon): ';'
+    │       └── rbrace (kind: TokenRBrace): '}'
+    └── eof (kind: TokenEndOfFile).
```

### crates/cairo-lang-semantic/src/expr/expansion_test_data/inline_macros
```diff
@@ -199,3 +199,75 @@ error[E2200]: Plugin diagnostic: Macro cannot be parsed as legacy macro. Expecte
  --> lib.cairo:2:1
 array![format!]
 ^^^^^^^^^^^^^^^
+
+//! > ==========================================================================
+
+//! > Test call-site `+` matched as a literal token and expanded.
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: false)
+
+//! > module_code
+#[feature("user_defined_inline_macros")]
+macro plus_lit {
+    (+) => { 7 };
+}
+
+//! > expr_code
+plus_lit!(+)
+
+//! > expanded_code
+7
+
+//! > diagnostics
+
+//! > ==========================================================================
+
+//! > Test call-site `+` matched as a literal token between two captures.
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: false)
+
+//! > module_code
+#[feature("user_defined_inline_macros")]
+macro keep_plus {
+    ($a:ident + $b:ident) => { $a + $b };
+}
+
+//! > function_body
+let x = 1_felt252;
+let y = 2_felt252;
+
+//! > expr_code
+keep_plus!(x + y)
+
+//! > expanded_code
+x+ y
+
+//! > diagnostics
+
+//! > ==========================================================================
+
+//! > Test call-site bare `$` is an opaque token that matches no ident rule.
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: true)
+
+//! > module_code
+#[feature("user_defined_inline_macros")]
+macro take_ident {
+    ($x:ident) => { 0 };
+}
+
+//! > expr_code
+take_ident!($)
+
+//! > expanded_code
+take_ident!($)
+
+//! > diagnostics
+error[E2158]: No matching rule found in inline macro `take_ident`.
+ --> lib.cairo:6:1
+take_ident!($)
+^^^^^^^^^^^^^^
+
```

### crates/cairo-lang-semantic/src/expr/test_data/inline_macros
```diff
@@ -2766,3 +2766,30 @@ error[E2158]: No matching rule found in inline macro `m`.
  --> lib.cairo:5:1
 m!
 ^^
+
+//! > ==========================================================================
+
+//! > Regression for #9993: macro call with `$(...)` without an operator does not ICE.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo() {
+    mymac!($(x));
+}
+
+//! > function_name
+foo
+
+//! > module_code
+#[feature("user_defined_inline_macros")]
+macro mymac {
+    ($x:ident) => { 1 };
+}
+
+//! > expected_diagnostics
+error[E2158]: No matching rule found in inline macro `mymac`.
+ --> lib.cairo:6:5
+    mymac!($(x));
+    ^^^^^^^^^^^^
```
