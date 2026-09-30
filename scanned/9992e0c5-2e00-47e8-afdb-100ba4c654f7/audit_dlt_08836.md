# [?] fix(lowering): dedup panic_destruct calls for a var at a shared panic location (#10205)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-07-18
Source: https://github.com/starkware-libs/cairo/commit/d83ad6f2dee14d233bb33dae9ad39d9e232704fc
Type: security-commit

## Details
fix(lowering): dedup panic_destruct calls for a var at a shared panic location (#10205)

## Patch
### crates/cairo-lang-lowering/src/destructs.rs
```diff
@@ -367,7 +367,10 @@ pub fn add_destructs<'db>(
         let first_panic_var = variables.new_var(VarRequest { ty: panic_ty, location });
         let mut last_panic_var = first_panic_var;
 
-        for destruction in destructions {
+        for destruction in destructions.into_iter().unique_by(|entry| match entry {
+            DestructionEntry::Plain(d) => d.var_id,
+            DestructionEntry::Panic(d) => d.var_id,
+        }) {
             let output_var = variables.new_var(VarRequest { ty: unit_ty(db), location });
 
             match destruction {
```

### crates/cairo-lang-lowering/src/test_data/destruct
```diff
@@ -369,3 +369,72 @@ error[E3005]: Cannot inline a function that might call itself.
 
 //! > lowering_flat
 Parameters:
+
+//! > ==========================================================================
+
+//! > Panic destruct is not duplicated when arms converge on a shared panic.
+
+//! > test_runner_name
+test_function_lowering(expect_diagnostics: false)
+
+//! > function_code
+fn foo(flag: bool) {
+    let d: Felt252Dict<u64> = Default::default();
+    let _w = Wrap { d };
+    if flag {
+        let _a = 1_u8;
+    } else {
+        let _b = 2_u8;
+    }
+    core::panic_with_felt252('x');
+}
+
+//! > function_name
+foo
+
+//! > module_code
+struct Wrap {
+    d: Felt252Dict<u64>,
+}
+
+impl WrapPanicDestruct of core::traits::PanicDestruct<Wrap> {
+    fn panic_destruct(self: Wrap, ref panic: core::panics::Panic) nopanic {
+        let Wrap { d } = self;
+        d.squash();
+    }
+}
+
+//! > semantic_diagnostics
+
+//! > lowering_diagnostics
+
+//! > lowering_flat
+Parameters: v0: core::RangeCheck, v1: core::SegmentArena, v2: core::gas::GasBuiltin, v3: core::bool
+blk0 (root):
+Statements:
+  (v4: core::SegmentArena, v5: core::dict::Felt252Dict::<core::integer::u64>) <- core::dict::felt252_dict_new::<core::integer::u64>(v1)
+End:
+  Match(match_enum(v3) {
+    bool::False(v6) => blk1,
+    bool::True(v7) => blk2,
+  })
+
+blk1:
+Statements:
+  (v8: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v2)
+End:
+  Goto(blk3, {v8 -> v9})
+
+blk2:
+Statements:
+  (v10: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v2)
+End:
+  Goto(blk3, {v10 -> v9})
+
+blk3:
+Statements:
+  (v11: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<120>()
+  (v12: core::RangeCheck, v13: core::SegmentArena, v14: core::gas::GasBuiltin, v15: core::dict::SquashedFelt252Dict::<core::integer::u64>) <- core::dict::Felt252DictImpl::<core::integer::u64, core::integer::U64Felt252DictValue>::squash(v0, v4, v9, v5)
+  (v16: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v11)
+End:
+  Return(v12, v13, v14, v16)
```
