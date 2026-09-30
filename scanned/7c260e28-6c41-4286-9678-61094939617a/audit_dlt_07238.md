# [?] [move-prover] Fixes a crash when someone tries to include a schema with a type check error.

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-06-04
Source: https://github.com/move-language/move/commit/5ef3738beb3602cc3b26582696b594a0e9dde662
Type: security-commit

## Details
[move-prover] Fixes a crash when someone tries to include a schema with a type check error.

The bug was in the expression rewriter. The rewriter must deal with Invalid expressions because it is used during type checking, where Invalid expression nodes can appear as result of type check errors.

Closes: #8482

## Patch
### language/move-model/src/exp_rewriter.rs
```diff
@@ -324,7 +324,9 @@ pub trait ExpRewriterFunctions {
                     exp
                 }
             }
-            Invalid(..) => unreachable!(),
+            // This can happen since we are calling the rewriter during type checking, and
+            // we may have encountered an error which is represented as an Invalid expression.
+            Invalid(id) => Invalid(*id).into_exp(),
         }
     }
 
```

### language/move-model/tests/sources/use_erroneous_schema.exp
```diff
@@ -0,0 +1,16 @@
+error: undeclared `M::x`
+
+   ┌── tests/sources/use_erroneous_schema.move:5:17 ───
+   │
+ 5 │         ensures x > 0;
+   │                 ^
+   │
+
+error: no matching declaration of `<`
+
+    ┌── tests/sources/use_erroneous_schema.move:13:17 ───
+    │
+ 13 │         ensures 2 < true;
+    │                 ^^^^^^^^
+    │
+    = outruled candidate `<(num, num): bool` (expected `num` but found `bool` for argument 2)
```

### language/move-model/tests/sources/use_erroneous_schema.move
```diff
@@ -0,0 +1,15 @@
+module 0x42::M {
+
+    // This schema creates an error.
+    spec schema ErroneousSchema {
+        ensures x > 0;
+    }
+
+    // This function includes the schema with the error, but also has its own error. We expect the own error
+    // to be reported and no issue with the use of erroneous schema.
+    fun foo(x: u64): u64 { x }
+    spec foo {
+        include ErroneousSchema;
+        ensures 2 < true;
+    }
+}
```
