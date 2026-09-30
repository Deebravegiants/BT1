# [?] Fix panic_destruct argument order. (#5908)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-06-27
Source: https://github.com/starkware-libs/cairo/commit/7b8c7b8b6f57096bbb034fea8c22a9896a551147
Type: security-commit

## Details
Fix panic_destruct argument order. (#5908)

## Patch
### corelib/src/test/language_features/panics_test.cairo
```diff
@@ -144,3 +144,16 @@ fn test_panic_macro_basic_string() {
 fn test_panic_macro_with_input() {
     panic!("some_format({})", 1)
 }
+
+
+#[test]
+#[should_panic(expected: 'PanicDestruct')]
+fn test_panic_destruct() {
+    panic_destruct_helper(1);
+}
+
+
+#[inline]
+fn panic_destruct_helper<T, +PanicDestruct<T>>(n: T) {
+    panic_with_felt252('PanicDestruct')
+}
```

### crates/cairo-lang-lowering/src/destructs.rs
```diff
@@ -375,8 +375,8 @@ pub fn add_destructs(
                     stmts.push(StatementCall {
                         function: semantic_function.lowered(db),
                         inputs: vec![
-                            VarUsage { var_id: last_panic_var, location },
                             VarUsage { var_id: panic_destruct.var_id, location },
+                            VarUsage { var_id: last_panic_var, location },
                         ],
                         with_coupon: false,
                         outputs: vec![new_panic_var, output_var],
```

### crates/cairo-lang-lowering/src/inline/test_data/inline
```diff
@@ -1875,9 +1875,10 @@ Statements:
   (v10: core::array::Array::<core::felt252>) <- core::array::array_new::<core::felt252>()
   (v11: core::felt252) <- 482670963043
   (v12: core::array::Array::<core::felt252>) <- core::array::array_append::<core::felt252>(v10, v11)
-  (v13: (core::panics::Panic, core::array::Array::<core::felt252>)) <- struct_construct(v0, v12)
-  (v14: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v13)
+  (v13: core::panics::Panic) <- struct_construct()
+  (v14: (core::panics::Panic, core::array::Array::<core::felt252>)) <- struct_construct(v13, v12)
+  (v15: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v14)
 End:
-  Goto(blk4, {v14 -> v3})
+  Goto(blk4, {v15 -> v3})
 
 //! > lowering_diagnostics
```

### crates/cairo-lang-lowering/src/test_data/destruct
```diff
@@ -162,8 +162,8 @@ Statements:
   (v9: core::felt252) <- 3224115
   (v10: core::array::Array::<core::felt252>) <- core::array::array_append::<core::felt252>(v8, v9)
   (v11: core::panics::Panic) <- struct_construct()
-  (v12: core::panics::Panic) <- test::BPanicDestruct::panic_destruct(v11, v1)
-  (v13: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v12, v0)
+  (v12: core::panics::Panic) <- test::BPanicDestruct::panic_destruct(v1, v11)
+  (v13: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v0, v12)
   (v14: (core::panics::Panic, core::array::Array::<core::felt252>)) <- struct_construct(v13, v10)
   (v15: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v14)
 End:
@@ -172,8 +172,8 @@ End:
 blk3:
 Statements:
   (v16: core::panics::Panic, v17: core::array::Array::<core::felt252>) <- struct_destructure(v7)
-  (v18: core::panics::Panic) <- test::BPanicDestruct::panic_destruct(v16, v1)
-  (v19: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v18, v0)
+  (v18: core::panics::Panic) <- test::BPanicDestruct::panic_destruct(v1, v16)
+  (v19: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v0, v18)
   (v20: (core::panics::Panic, core::array::Array::<core::felt252>)) <- struct_construct(v19, v17)
   (v21: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v20)
 End:
@@ -182,8 +182,8 @@ End:
 blk4:
 Statements:
   (v22: core::panics::Panic, v23: core::array::Array::<core::felt252>) <- struct_destructure(v4)
-  (v24: core::panics::Panic) <- test::BPanicDestruct::panic_destruct(v22, v1)
-  (v25: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v24, v0)
+  (v24: core::panics::Panic) <- test::BPanicDestruct::panic_destruct(v1, v22)
+  (v25: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v0, v24)
   (v26: (core::panics::Panic, core::array::Array::<core::felt252>)) <- struct_construct(v25, v23)
   (v27: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v26)
 End:
@@ -264,7 +264,7 @@ End:
 blk5:
 Statements:
   (v9: core::panics::Panic, v10: core::array::Array::<core::felt252>) <- struct_destructure(v6)
-  (v11: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v9, v1)
+  (v11: core::panics::Panic) <- test::APanicDestruct::panic_destruct(v1, v9)
   (v12: (core::panics::Panic, core::array::Array::<core::felt252>)) <- struct_construct(v11, v10)
   (v13: core::panics::PanicResult::<(test::A,)>) <- PanicResult::Err(v12)
 End:
```
