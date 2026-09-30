# [?] fix(fuzz): Use an inline block to circumvent negation with overflow (#8911)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-13
Source: https://github.com/noir-lang/noir/commit/753ad6fb530beb01f94ebf75946050627ede2c11
Type: security-commit

## Details
fix(fuzz): Use an inline block to circumvent negation with overflow (#8911)

## Patch
### compiler/noirc_frontend/src/monomorphization/printer.rs
```diff
@@ -249,7 +249,9 @@ impl AstPrinter {
             }
             super::ast::Literal::Integer(x, typ, _) => {
                 if self.show_type_of_int_literal {
-                    write!(f, "{x} as {typ}")
+                    // Unfortunately this doesn't work: `-128 as i8` panics with `attempt to negate with overflow` because it first treats `128` as `u8`.
+                    //write!(f, "{x} as {typ}")
+                    write!(f, "{{ let x: {typ} = {x}; x }}")
                 } else {
                     x.fmt(f)
                 }
```
