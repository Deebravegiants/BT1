# [?] fix(fuzz): Handle `Div` overflow message equivalence (#13036)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-16
Source: https://github.com/noir-lang/noir/commit/a724dd4b5cba469a425dfa5b67191859040ac644
Type: security-commit

## Details
fix(fuzz): Handle `Div` overflow message equivalence (#13036)

## Patch
### tooling/ast_fuzzer/src/compare/interpreted.rs
```diff
@@ -182,6 +182,9 @@ impl Comparable for ssa::interpreter::errors::InterpreterError {
                         || msg == "attempt to shift right with overflow"
                         || msg == "attempt to shift left with overflow"
                 }
+                // Signed division of `i_N::MIN / -1` overflows. The `expand_signed_math` pass and
+                // the constant-folding of binary ops produce the message with different casing.
+                BinaryOp::Div => msg.to_lowercase() == "attempt to divide with overflow",
                 _ => false,
             },
             (
```
