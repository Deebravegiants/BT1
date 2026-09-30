# [?] Fix MockProver `assert_verify` panic errors (#118)

## Summary
Severity: Unknown
Chain: ZK
Component: privacy-scaling-explorations/halo2
Published: 2023-01-09
Source: https://github.com/privacy-ethereum/halo2/commit/be10b68d4b704de8a6639fb201fcf20a7f3e3c62
Type: security-commit

## Details
Fix MockProver `assert_verify` panic errors (#118)

* fix: Support dynamic lookups in `MockProver::assert_verify`

Since lookups can only be `Fixed` in Halo2-upstream, we need to add
custom suport for the error rendering of dynamic lookups which doesn't
come by default when we rebase to upstream.

This means that now we have to print not only `AdviceQuery` results to
render the `Expression` that is being looked up. But also support
`Instance`, `Advice`, `Challenge` or any other expression types that are
avaliable.

This addresses the rendering issue, renaming also the `table_columns`
variable for `lookup_columns` as the columns do not have the type
`TableColumn` by default as opposite to what happens upstream.

* fix: Don't error and emit empty String for Empty queries

* feat: Add `assert_sarisfied_par` fn to `MockProver`

* fix: Address clippy errors

* chore: Address review comments

* chore: Fix clippy lints

Resolves: #116

## Patch
### halo2_proofs/src/dev.rs
```diff
@@ -1315,6 +1315,27 @@ impl<F: FieldExt> MockProver<F> {
             panic!("circuit was not satisfied");
         }
     }
+
+    /// Panics if the circuit being checked by this `MockProver` is not satisfied.
+    ///
+    /// Any verification failures will be pretty-printed to stderr before the function
+    /// panics.
+    ///
+    /// Internally, this function uses a parallel aproach in order to verify the `MockProver` contents.
+    ///
+    /// Apart from the stderr output, this method is equivalent to:
+    /// ```ignore
+    /// assert_eq!(prover.verify_par(), Ok(()));
+    /// ```
+    pub fn assert_satisfied_par(&self) {
+        if let Err(errs) = self.verify_par() {
+            for err in errs {
+                err.emit(self);
+                eprintln!();
+            }
+            panic!("circuit was not satisfied");
+        }
+    }
 }
 
 #[cfg(test)]
```

### halo2_proofs/src/dev/failure.rs
```diff
@@ -398,18 +398,18 @@ fn render_lookup<F: FieldExt>(
 
     // Recover the fixed columns from the table expressions. We don't allow composite
     // expressions for the table side of lookups.
-    let table_columns = lookup.table_expressions.iter().map(|expr| {
+    let lookup_columns = lookup.table_expressions.iter().map(|expr| {
         expr.evaluate(
             &|_| panic!("no constants in table expressions"),
             &|_| panic!("no selectors in table expressions"),
             &|query| format!("F{}", query.column_index),
-            &|_| panic!("no advice columns in table expressions"),
-            &|_| panic!("no instance columns in table expressions"),
-            &|_| panic!("no challenges in table expressions"),
-            &|_| panic!("no negations in table expressions"),
-            &|_, _| panic!("no sums in table expressions"),
-            &|_, _| panic!("no products in table expressions"),
-            &|_, _| panic!("no scaling in table expressions"),
+            &|query| format! {"A{}", query.column_index},
+            &|query| format! {"I{}", query.column_index},
+            &|challenge| format! {"C{}", challenge.index()},
+            &|query| format! {"-{}", query},
+            &|a, b| format! {"{} + {}", a,b},
+            &|a, b| format! {"{} * {}", a,b},
+            &|a, b| format! {"{} * {:?}", a, b},
         )
     });
 
@@ -441,7 +441,7 @@ fn render_lookup<F: FieldExt>(
         eprint!("{}L{}", if i == 0 { "" } else { ", " }, i);
     }
     eprint!(") ∉ (");
-    for (i, column) in table_columns.enumerate() {
+    for (i, column) in lookup_columns.enumerate() {
         eprint!("{}{}", if i == 0 { "" } else { ", " }, column);
     }
     eprintln!(")");
```

### halo2_proofs/src/dev/failure/emitter.rs
```diff
@@ -120,16 +120,17 @@ pub(super) fn expression_to_string<F: Field>(
         &|query| {
             layout
                 .get(&query.rotation.0)
-                .unwrap()
-                .get(
-                    &(
-                        Any::Advice(Advice { phase: query.phase }),
-                        query.column_index,
+                .and_then(|map| {
+                    map.get(
+                        &(
+                            Any::Advice(Advice { phase: query.phase }),
+                            query.column_index,
+                        )
+                            .into(),
                     )
-                        .into(),
-                )
-                .unwrap()
-                .clone()
+                })
+                .cloned()
+                .unwrap_or_default()
         },
         &|query| {
             layout
```
