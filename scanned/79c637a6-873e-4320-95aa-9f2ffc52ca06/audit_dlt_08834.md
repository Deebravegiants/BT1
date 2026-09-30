# [?] fix(parser): stop colored_printer panicking on valid tokens (#10261)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-07-27
Source: https://github.com/starkware-libs/cairo/commit/39ad12d20df6a96126003db361a4cb9ff8153b46
Type: security-commit

## Details
fix(parser): stop colored_printer panicking on valid tokens (#10261)

Co-authored-by: Claude Opus 5 <noreply@anthropic.com>

## Patch
### crates/cairo-lang-parser/src/colored_printer.rs
```diff
@@ -71,14 +71,23 @@ fn set_color(text: &str, kind: SyntaxKind) -> ColoredString {
         | SyntaxKind::TokenEnum
         | SyntaxKind::TokenStruct
         | SyntaxKind::TokenTrait
+        | SyntaxKind::TokenMacro
+        | SyntaxKind::TokenConst
+        | SyntaxKind::TokenPub
         | SyntaxKind::TokenImpl => text.bright_blue(),
         SyntaxKind::TokenOf
         | SyntaxKind::TokenLet
         | SyntaxKind::TokenReturn
         | SyntaxKind::TokenMatch
         | SyntaxKind::TokenIf
         | SyntaxKind::TokenElse
+        | SyntaxKind::TokenWhile
+        | SyntaxKind::TokenFor
+        | SyntaxKind::TokenLoop
+        | SyntaxKind::TokenContinue
+        | SyntaxKind::TokenBreak
         | SyntaxKind::TokenUse
+        | SyntaxKind::TokenAs
         | SyntaxKind::TokenImplicits
         | SyntaxKind::TokenRef
         | SyntaxKind::TokenMut
@@ -98,13 +107,21 @@ fn set_color(text: &str, kind: SyntaxKind) -> ColoredString {
         | SyntaxKind::TokenNot
         | SyntaxKind::TokenQuestionMark
         | SyntaxKind::TokenUnderscore
+        | SyntaxKind::TokenAt
+        | SyntaxKind::TokenBitNot
+        | SyntaxKind::TokenDollar
         | SyntaxKind::TokenHash => text.truecolor(255, 180, 255), // Pink
         SyntaxKind::TokenEq
         | SyntaxKind::TokenEqEq
         | SyntaxKind::TokenGE
         | SyntaxKind::TokenGT
         | SyntaxKind::TokenLE
         | SyntaxKind::TokenLT
+        | SyntaxKind::TokenPlusEq
+        | SyntaxKind::TokenMinusEq
+        | SyntaxKind::TokenMulEq
+        | SyntaxKind::TokenDivEq
+        | SyntaxKind::TokenModEq
         | SyntaxKind::TokenNeq => {
             text.truecolor(255, 165, 0) // Orange
         }
@@ -120,11 +137,13 @@ fn set_color(text: &str, kind: SyntaxKind) -> ColoredString {
         SyntaxKind::TokenMissing => text.clear(),
         SyntaxKind::TokenSkipped => text.on_red(), // red background
         SyntaxKind::TokenSingleLineComment
+        | SyntaxKind::TokenSingleLineDocComment
+        | SyntaxKind::TokenSingleLineInnerComment
         | SyntaxKind::TokenWhitespace
         | SyntaxKind::TokenNewline
         | SyntaxKind::TokenEmpty => text.clear(),
-        // TODO(yuval): Can this be made exhaustive?
-        _ => panic!("Unexpected syntax kind: {kind:?}"),
+        // TODO(orizi): Make exhaustive.
+        _ => text.clear(),
     }
 }
 
```
