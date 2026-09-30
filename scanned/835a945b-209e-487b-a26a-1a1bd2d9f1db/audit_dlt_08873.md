# [?] Fixed scc panic checks to be consistently post inlining. (#4315)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2023-10-30
Source: https://github.com/starkware-libs/cairo/commit/84104f45f7f1a634fa7e28e07f5ff20f966f73cb
Type: security-commit

## Details
Fixed scc panic checks to be consistently post inlining. (#4315)

## Patch
### crates/cairo-lang-lowering/src/panic/mod.rs
```diff
@@ -345,7 +345,7 @@ pub fn scc_may_panic(db: &dyn LoweringGroup, scc: ConcreteSCCRepresentative) ->
             return Ok(true);
         }
         // For each direct callee, find if it may panic.
-        let direct_callees = db.concrete_function_with_body_direct_callees(function)?;
+        let direct_callees = db.concrete_function_with_body_postinline_direct_callees(function)?;
         for direct_callee in direct_callees {
             if let Some(callee_body) = direct_callee.body(db.upcast())? {
                 let callee_scc = db.concrete_function_with_body_scc_representative(callee_body);
@@ -365,7 +365,7 @@ pub fn has_direct_panic(
     db: &dyn LoweringGroup,
     function_id: ConcreteFunctionWithBodyId,
 ) -> Maybe<bool> {
-    let lowered_function = db.priv_concrete_function_with_body_lowered_flat(function_id)?;
+    let lowered_function = db.priv_concrete_function_with_body_postinline_lowered(function_id)?;
     Ok(itertools::any(&lowered_function.blocks, |(_, block)| {
         matches!(&block.end, FlatBlockEnd::Panic(..))
     }))
```

### tests/bug_samples/issue4314.cairo
```diff
@@ -0,0 +1,21 @@
+#[inline]
+fn one() {
+    two();
+}
+
+#[inline(never)]
+fn two() {
+    three();
+}
+
+#[inline(never)]
+fn three() {
+    one();
+}
+
+#[test]
+#[should_panic]
+#[available_gas(10000)]
+fn calls_inline_panic() {
+    one();
+}
```

### tests/bug_samples/lib.cairo
```diff
@@ -32,6 +32,7 @@ mod issue4038;
 mod issue4075;
 mod issue4092;
 mod issue4109;
+mod issue4314;
 mod issue4318;
 mod loop_only_change;
 mod inconsistent_gas;
```
