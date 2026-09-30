# [?] Avoid adding redeposit_gas before panic flows. (#7687)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2025-04-21
Source: https://github.com/starkware-libs/cairo/commit/73953872a51075f34d0dfdfbbb6218fbdba25328
Type: security-commit

## Details
Avoid adding redeposit_gas before panic flows. (#7687)

## Patch
### crates/cairo-lang-lowering/src/lower/test_data/for
```diff
@@ -87,10 +87,9 @@ End:
 
 blk2:
 Statements:
-  (v29: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v19)
-  (v30: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v22)
+  (v29: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v22)
 End:
-  Return(v18, v29, v30)
+  Return(v18, v19, v29)
 
 
 Generated loop lowering for source location:
@@ -168,11 +167,10 @@ End:
 
 blk4:
 Statements:
-  (v28: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v8)
-  (v29: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v30: core::panics::PanicResult::<(core::array::SpanIter::<core::felt252>, core::felt252, ())>) <- PanicResult::Err(v29)
+  (v28: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v29: core::panics::PanicResult::<(core::array::SpanIter::<core::felt252>, core::felt252, ())>) <- PanicResult::Err(v28)
 End:
-  Return(v7, v28, v30)
+  Return(v7, v8, v29)
 
 //! > ==========================================================================
 
@@ -254,7 +252,6 @@ End:
 
 blk2:
 Statements:
-  (v16: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v7)
-  (v17: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v10)
+  (v16: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v10)
 End:
-  Return(v6, v16, v17)
+  Return(v6, v7, v16)
```

### crates/cairo-lang-lowering/src/lower/test_data/loop
```diff
@@ -61,10 +61,9 @@ End:
 
 blk2:
 Statements:
-  (v13: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v14: core::panics::PanicResult::<(core::bool,)>) <- PanicResult::Err(v7)
+  (v13: core::panics::PanicResult::<(core::bool,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v13, v14)
+  Return(v3, v4, v13)
 
 
 Generated loop lowering for source location:
@@ -149,11 +148,10 @@ End:
 
 blk4:
 Statements:
-  (v21: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v22: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v23: core::panics::PanicResult::<(core::felt252, core::bool)>) <- PanicResult::Err(v22)
+  (v21: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v22: core::panics::PanicResult::<(core::felt252, core::bool)>) <- PanicResult::Err(v21)
 End:
-  Return(v5, v21, v23)
+  Return(v5, v6, v22)
 
 //! > ==========================================================================
 
@@ -219,10 +217,9 @@ End:
 
 blk2:
 Statements:
-  (v13: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v14: core::panics::PanicResult::<(core::bool,)>) <- PanicResult::Err(v7)
+  (v13: core::panics::PanicResult::<(core::bool,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v13, v14)
+  Return(v3, v4, v13)
 
 
 Generated loop lowering for source location:
@@ -307,11 +304,10 @@ End:
 
 blk4:
 Statements:
-  (v21: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v22: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v23: core::panics::PanicResult::<(core::felt252, core::bool)>) <- PanicResult::Err(v22)
+  (v21: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v22: core::panics::PanicResult::<(core::felt252, core::bool)>) <- PanicResult::Err(v21)
 End:
-  Return(v5, v21, v23)
+  Return(v5, v6, v22)
 
 //! > ==========================================================================
 
@@ -397,10 +393,9 @@ End:
 
 blk2:
 Statements:
-  (v19: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v8)
-  (v20: core::panics::PanicResult::<(test::A, ())>) <- PanicResult::Err(v11)
+  (v19: core::panics::PanicResult::<(test::A, ())>) <- PanicResult::Err(v11)
 End:
-  Return(v7, v19, v20)
+  Return(v7, v8, v19)
 
 
 Generated loop lowering for source location:
@@ -472,11 +467,10 @@ End:
 
 blk2:
 Statements:
-  (v17: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v8)
-  (v18: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v19: core::panics::PanicResult::<(core::integer::u32, test::A, test::A)>) <- PanicResult::Err(v18)
+  (v17: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v18: core::panics::PanicResult::<(core::integer::u32, test::A, test::A)>) <- PanicResult::Err(v17)
 End:
-  Return(v7, v17, v19)
+  Return(v7, v8, v18)
 
 //! > ==========================================================================
 
@@ -546,10 +540,9 @@ End:
 
 blk2:
 Statements:
-  (v13: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v14: core::panics::PanicResult::<(core::bool,)>) <- PanicResult::Err(v7)
+  (v13: core::panics::PanicResult::<(core::bool,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v13, v14)
+  Return(v3, v4, v13)
 
 
 Generated loop lowering for source location:
@@ -678,11 +671,10 @@ End:
 
 blk7:
 Statements:
-  (v26: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v27: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v28: core::panics::PanicResult::<(core::felt252, core::bool)>) <- PanicResult::Err(v27)
+  (v26: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v27: core::panics::PanicResult::<(core::felt252, core::bool)>) <- PanicResult::Err(v26)
 End:
-  Return(v5, v26, v28)
+  Return(v5, v6, v27)
 
 //! > ==========================================================================
 
@@ -828,10 +820,9 @@ End:
 
 blk2:
 Statements:
-  (v12: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v13: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v7)
+  (v12: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v12, v13)
+  Return(v3, v4, v12)
 
 
 Generated loop lowering for source location:
@@ -931,11 +922,10 @@ End:
 
 blk4:
 Statements:
-  (v17: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v18: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v19: core::panics::PanicResult::<(core::integer::u8, ())>) <- PanicResult::Err(v18)
+  (v17: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v18: core::panics::PanicResult::<(core::integer::u8, ())>) <- PanicResult::Err(v17)
 End:
-  Return(v5, v17, v19)
+  Return(v5, v6, v18)
 
 //! > ==========================================================================
 
@@ -1440,10 +1430,9 @@ End:
 
 blk2:
 Statements:
-  (v14: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v15: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v9)
+  (v14: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v9)
 End:
-  Return(v5, v14, v15)
+  Return(v5, v6, v14)
 
 
 Generated loop lowering for source location:
@@ -1528,11 +1517,10 @@ End:
 
 blk4:
 Statements:
-  (v24: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v7)
-  (v25: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v26: core::panics::PanicResult::<(test::A, core::felt252, ())>) <- PanicResult::Err(v25)
+  (v24: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v25: core::panics::PanicResult::<(test::A, core::felt252, ())>) <- PanicResult::Err(v24)
 End:
-  Return(v6, v24, v26)
+  Return(v6, v7, v25)
 
 //! > ==========================================================================
 
@@ -1608,10 +1596,9 @@ End:
 
 blk2:
 Statements:
-  (v12: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v13: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v7)
+  (v12: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v12, v13)
+  Return(v3, v4, v12)
 
 //! > lowering_diagnostics
 
@@ -1722,10 +1709,9 @@ End:
 
 blk4:
 Statements:
-  (v19: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v20: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v7)
+  (v19: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v19, v20)
+  Return(v3, v4, v19)
 
 
 Generated loop lowering for source location:
@@ -1900,11 +1886,10 @@ End:
 
 blk9:
 Statements:
-  (v35: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v36: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v37: core::panics::PanicResult::<(core::felt252, core::internal::LoopResult::<core::bool, core::integer::u32>)>) <- PanicResult::Err(v36)
+  (v35: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v36: core::panics::PanicResult::<(core::felt252, core::internal::LoopResult::<core::bool, core::integer::u32>)>) <- PanicResult::Err(v35)
 End:
-  Return(v5, v35, v37)
+  Return(v5, v6, v36)
 
 //! > lowering_diagnostics
 
@@ -2158,10 +2143,9 @@ End:
 
 blk4:
 Statements:
-  (v19: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v20: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v7)
+  (v19: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v19, v20)
+  Return(v3, v4, v19)
 
 
 Generated loop lowering for source location:
@@ -2385,11 +2369,10 @@ End:
 
 blk8:
 Statements:
-  (v32: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v33: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v34: core::panics::PanicResult::<(core::array::Array::<core::integer::u32>, core::internal::LoopResult::<(), core::integer::u32>)>) <- PanicResult::Err(v33)
+  (v32: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v33: core::panics::PanicResult::<(core::array::Array::<core::integer::u32>, core::internal::LoopResult::<(), core::integer::u32>)>) <- PanicResult::Err(v32)
 End:
-  Return(v5, v32, v34)
+  Return(v5, v6, v33)
 
 //! > lowering_diagnostics
 
@@ -2497,10 +2480,9 @@ End:
 
 blk4:
 Statements:
-  (v19: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v20: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v7)
+  (v19: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v19, v20)
+  Return(v3, v4, v19)
 
 
 Generated loop lowering for source location:
@@ -2724,11 +2706,10 @@ End:
 
 blk8:
 Statements:
-  (v32: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v33: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v34: core::panics::PanicResult::<(core::array::Array::<core::integer::u32>, core::internal::LoopResult::<(), core::integer::u32>)>) <- PanicResult::Err(v33)
+  (v32: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v33: core::panics::PanicResult::<(core::array::Array::<core::integer::u32>, core::internal::LoopResult::<(), core::integer::u32>)>) <- PanicResult::Err(v32)
 End:
-  Return(v5, v32, v34)
+  Return(v5, v6, v33)
 
 //! > lowering_diagnostics
 
@@ -2834,10 +2815,9 @@ End:
 
 blk4:
 Statements:
-  (v22: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v23: core::panics::PanicResult::<(core::result::Result::<(), core::integer::u32>,)>) <- PanicResult::Err(v9)
+  (v22: core::panics::PanicResult::<(core::result::Result::<(), core::integer::u32>,)>) <- PanicResult::Err(v9)
 End:
-  Return(v5, v22, v23)
+  Return(v5, v6, v22)
 
 
 Generated loop lowering for source location:
@@ -2949,30 +2929,28 @@ End:
 
 blk6:
 Statements:
-  (v26: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v27: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<155785504323917466144735657540098748279>()
-  (v28: core::panics::PanicResult::<(core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)>) <- PanicResult::Err(v27)
+  (v26: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<155785504323917466144735657540098748279>()
+  (v27: core::panics::PanicResult::<(core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)>) <- PanicResult::Err(v26)
 End:
-  Return(v12, v26, v28)
+  Return(v12, v4, v27)
 
 blk7:
 Statements:
-  (v29: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v30: ()) <- struct_construct()
-  (v31: core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>) <- LoopResult::Normal(v30)
-  (v32: core::ops::range::RangeIterator::<core::integer::u32>) <- struct_construct(v7, v8)
-  (v33: (core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)) <- struct_construct(v32, v31)
-  (v34: core::panics::PanicResult::<(core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)>) <- PanicResult::Ok(v33)
+  (v28: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
+  (v29: ()) <- struct_construct()
+  (v30: core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>) <- LoopResult::Normal(v29)
+  (v31: core::ops::range::RangeIterator::<core::integer::u32>) <- struct_construct(v7, v8)
+  (v32: (core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)) <- struct_construct(v31, v30)
+  (v33: core::panics::PanicResult::<(core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)>) <- PanicResult::Ok(v32)
 End:
-  Return(v3, v29, v34)
+  Return(v3, v28, v33)
 
 blk8:
 Statements:
-  (v35: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v36: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v37: core::panics::PanicResult::<(core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)>) <- PanicResult::Err(v36)
+  (v34: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v35: core::panics::PanicResult::<(core::ops::range::RangeIterator::<core::integer::u32>, core::internal::LoopResult::<(), core::result::Result::<(), core::integer::u32>>)>) <- PanicResult::Err(v34)
 End:
-  Return(v5, v35, v37)
+  Return(v5, v6, v35)
 
 //! > lowering_diagnostics
 
@@ -3095,10 +3073,9 @@ End:
 
 blk4:
 Statements:
-  (v17: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v5)
-  (v18: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v19: core::panics::PanicResult::<(core::result::Result::<(), core::integer::u32>,)>) <- PanicResult::Err(v18)
+  (v17: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v18: core::panics::PanicResult::<(core::result::Result::<(), core::integer::u32>,)>) <- PanicResult::Err(v17)
 End:
-  Return(v4, v17, v19)
+  Return(v4, v5, v18)
 
 //! > lowering_diagnostics
```

### crates/cairo-lang-lowering/src/lower/test_data/while
```diff
@@ -58,10 +58,9 @@ End:
 
 blk2:
 Statements:
-  (v14: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v5)
-  (v15: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v8)
+  (v14: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v8)
 End:
-  Return(v4, v14, v15)
+  Return(v4, v5, v14)
 
 
 Generated loop lowering for source location:
@@ -137,11 +136,10 @@ End:
 
 blk4:
 Statements:
-  (v18: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v19: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v20: core::panics::PanicResult::<(core::felt252, ())>) <- PanicResult::Err(v19)
+  (v18: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v19: core::panics::PanicResult::<(core::felt252, ())>) <- PanicResult::Err(v18)
 End:
-  Return(v5, v18, v20)
+  Return(v5, v6, v19)
 
 //! > ==========================================================================
 
@@ -338,10 +336,9 @@ End:
 
 blk2:
 Statements:
-  (v15: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v16: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v7)
+  (v15: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v15, v16)
+  Return(v3, v4, v15)
 
 
 Generated loop lowering for source location:
@@ -445,8 +442,7 @@ End:
 
 blk6:
 Statements:
-  (v19: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v20: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v21: core::panics::PanicResult::<(core::felt252, ())>) <- PanicResult::Err(v20)
+  (v19: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v20: core::panics::PanicResult::<(core::felt252, ())>) <- PanicResult::Err(v19)
 End:
-  Return(v5, v19, v21)
+  Return(v5, v6, v20)
```

### crates/cairo-lang-lowering/src/optimizations/gas_redeposit.rs
```diff
@@ -4,14 +4,18 @@ mod test;
 
 use cairo_lang_filesystem::flag::Flag;
 use cairo_lang_filesystem::ids::FlagId;
-use cairo_lang_semantic::corelib;
+use cairo_lang_semantic::{ConcreteVariant, corelib};
 use itertools::{Itertools, zip_eq};
 
 use crate::borrow_check::analysis::{Analyzer, BackAnalysis, StatementLocation};
 use crate::db::LoweringGroup;
 use crate::ids::{ConcreteFunctionWithBodyId, LocationId, SemanticFunctionIdEx};
 use crate::implicits::FunctionImplicitsTrait;
-use crate::{BlockId, FlatLowered, MatchInfo, Statement, StatementCall, VarRemapping, VarUsage};
+use crate::panic::PanicSignatureInfo;
+use crate::{
+    BlockId, FlatLowered, MatchInfo, Statement, StatementCall, StatementEnumConstruct,
+    VarRemapping, VarUsage, VariableId,
+};
 
 /// Adds redeposit gas actions.
 ///
@@ -49,7 +53,11 @@ pub fn gas_redeposit(
         "`GasRedeposit` stage must be called before `LowerImplicits` stage"
     );
 
-    let ctx = GasRedepositContext { fixes: vec![] };
+    let panic_sig = PanicSignatureInfo::new(db, &function_id.signature(db).unwrap());
+    if panic_sig.always_panic {
+        return;
+    }
+    let ctx = GasRedepositContext { fixes: vec![], err_variant: panic_sig.err_variant };
     let mut analysis = BackAnalysis::new(lowered, ctx);
     analysis.get_root_info();
 
@@ -81,27 +89,53 @@ pub fn gas_redeposit(
 pub struct GasRedepositContext {
     /// The list of blocks where we need to insert redeposit_gas.
     fixes: Vec<(BlockId, LocationId)>,
+    /// The panic error variant.
+    pub err_variant: ConcreteVariant,
 }
 
 #[derive(Clone, PartialEq, Debug)]
 pub enum RedepositState {
     /// Gas might be burned if we don't redeposit.
     Required,
-    /// Rediposit was already added, no need to add another one.
-    Redeposited,
+    /// Redeposit is not necessary. This may occur if it has already been handled
+    /// or if the flow is terminating due to a panic.
+    Unnecessary,
+    /// The flow returns the given variable, redeposit is required unless the return var is of the
+    /// error variant.
+    Return(VariableId),
 }
 
 impl Analyzer<'_> for GasRedepositContext {
     type Info = RedepositState;
 
+    fn visit_stmt(
+        &mut self,
+        info: &mut Self::Info,
+        _statement_location: StatementLocation,
+        stmt: &Statement,
+    ) {
+        let RedepositState::Return(var_id) = info else {
+            return;
+        };
+
+        let Statement::EnumConstruct(StatementEnumConstruct { variant, input: _, output }) = stmt
+        else {
+            return;
+        };
+
+        if output == var_id && *variant == self.err_variant {
+            *info = RedepositState::Unnecessary;
+        }
+    }
+
     fn visit_goto(
         &mut self,
         info: &mut Self::Info,
         _statement_location: StatementLocation,
         _target_block_id: BlockId,
         _remapping: &VarRemapping,
     ) {
-        // A goto is a convergence point, gas will get burned unless we redeposit it before the
+        // A goto is a convergence point, gas will get burned unless it is redeposited before the
         // convergence.
         *info = RedepositState::Required
     }
@@ -113,18 +147,26 @@ impl Analyzer<'_> for GasRedepositContext {
         infos: impl Iterator<Item = Self::Info>,
     ) -> Self::Info {
         for (info, arm) in zip_eq(infos, match_info.arms()) {
-            if info == RedepositState::Required {
-                self.fixes.push((arm.block_id, *match_info.location()));
+            match info {
+                RedepositState::Return(_) | RedepositState::Required => {
+                    self.fixes.push((arm.block_id, *match_info.location()));
+                }
+                RedepositState::Unnecessary => {}
             }
         }
 
         // `redeposit_gas` was added, no need to add it until the next convergence point.
-        RedepositState::Redeposited
+        RedepositState::Unnecessary
     }
 
-    fn info_from_return(&mut self, _: StatementLocation, _vars: &[VarUsage]) -> Self::Info {
+    fn info_from_return(&mut self, _: StatementLocation, vars: &[VarUsage]) -> Self::Info {
         // If the function has multiple returns with different gas costs, gas will get burned unless
         // we redeposit it.
-        RedepositState::Required
+        // If however the this return corresponds to a panic, we dont redeposit due to code size
+        // concerns.
+        match vars.last() {
+            Some(VarUsage { var_id, location: _ }) => RedepositState::Return(*var_id),
+            None => RedepositState::Required,
+        }
     }
 }
```

### crates/cairo-lang-lowering/src/panic/mod.rs
```diff
@@ -196,12 +196,12 @@ pub struct PanicSignatureInfo {
     /// The Ok() variant.
     ok_variant: ConcreteVariant,
     /// The Err() variant.
-    err_variant: ConcreteVariant,
+    pub err_variant: ConcreteVariant,
     /// The PanicResult concrete type - the new return type of the function.
     pub actual_return_ty: TypeId,
     /// Does the function always panic.
     /// Note that if it does - the function returned type is always `(Panic, Array<felt252>)`.
-    always_panic: bool,
+    pub always_panic: bool,
 }
 impl PanicSignatureInfo {
     pub fn new(db: &dyn LoweringGroup, signature: &Signature) -> Self {
```

### crates/cairo-lang-lowering/src/test_data/for
```diff
@@ -59,7 +59,6 @@ End:
 
 blk2:
 Statements:
-  (v26: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v16)
-  (v27: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v19)
+  (v26: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v19)
 End:
-  Return(v15, v26, v27)
+  Return(v15, v16, v26)
```

### crates/cairo-lang-lowering/src/test_data/snapshot
```diff
@@ -297,18 +297,16 @@ End:
 
 blk3:
 Statements:
-  (v23: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v9)
-  (v24: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<29721761890975875353235833581453094220424382983267374>()
-  (v25: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v24)
+  (v23: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<29721761890975875353235833581453094220424382983267374>()
+  (v24: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v23)
 End:
-  Return(v8, v23, v25)
+  Return(v8, v9, v24)
 
 blk4:
 Statements:
-  (v26: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v9)
-  (v27: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v12)
+  (v25: core::panics::PanicResult::<(core::integer::u32,)>) <- PanicResult::Err(v12)
 End:
-  Return(v8, v26, v27)
+  Return(v8, v9, v25)
 
 //! > ==========================================================================
 
```

### crates/cairo-lang-lowering/src/test_data/strings
```diff
@@ -238,14 +238,12 @@ End:
 
 blk3:
 Statements:
-  (v46: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v37)
-  (v47: core::panics::PanicResult::<(core::byte_array::ByteArray,)>) <- PanicResult::Err(v40)
+  (v46: core::panics::PanicResult::<(core::byte_array::ByteArray,)>) <- PanicResult::Err(v40)
 End:
-  Return(v36, v46, v47)
+  Return(v36, v37, v46)
 
 blk4:
 Statements:
-  (v48: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v15)
-  (v49: core::panics::PanicResult::<(core::byte_array::ByteArray,)>) <- PanicResult::Err(v18)
+  (v47: core::panics::PanicResult::<(core::byte_array::ByteArray,)>) <- PanicResult::Err(v18)
 End:
-  Return(v14, v48, v49)
+  Return(v14, v15, v47)
```

### crates/cairo-lang-lowering/src/test_data/tests
```diff
@@ -215,18 +215,16 @@ End:
 
 blk6:
 Statements:
-  (v29: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v16)
-  (v30: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v19)
+  (v29: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v19)
 End:
-  Return(v15, v29, v30)
+  Return(v15, v16, v29)
 
 blk7:
 Statements:
-  (v31: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v6)
-  (v32: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
-  (v33: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v32)
+  (v30: (core::panics::Panic, core::array::Array::<core::felt252>)) <- core::panic_with_const_felt252::<375233589013918064796019>()
+  (v31: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v30)
 End:
-  Return(v5, v31, v33)
+  Return(v5, v6, v31)
 
 //! > ==========================================================================
 
```

### crates/cairo-lang-lowering/src/test_data/while
```diff
@@ -44,10 +44,9 @@ End:
 
 blk2:
 Statements:
-  (v16: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v7)
-  (v17: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v10)
+  (v16: core::panics::PanicResult::<((),)>) <- PanicResult::Err(v10)
 End:
-  Return(v6, v16, v17)
+  Return(v6, v7, v16)
 
 //! > ==========================================================================
 
@@ -103,10 +102,9 @@ End:
 
 blk2:
 Statements:
-  (v14: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v5)
-  (v15: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v8)
+  (v14: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v8)
 End:
-  Return(v4, v14, v15)
+  Return(v4, v5, v14)
 
 //! > ==========================================================================
 
@@ -165,10 +163,9 @@ End:
 
 blk2:
 Statements:
-  (v15: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v16: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v7)
+  (v15: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v15, v16)
+  Return(v3, v4, v15)
 
 //! > ==========================================================================
 
@@ -227,10 +224,9 @@ End:
 
 blk2:
 Statements:
-  (v15: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v4)
-  (v16: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v7)
+  (v15: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v7)
 End:
-  Return(v3, v15, v16)
+  Return(v3, v4, v15)
 
 //! > ==========================================================================
 
@@ -364,10 +360,9 @@ End:
 
 blk2:
 Statements:
-  (v16: core::gas::GasBuiltin) <- core::gas::redeposit_gas(v5)
-  (v17: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v8)
+  (v16: core::panics::PanicResult::<(core::felt252,)>) <- PanicResult::Err(v8)
 End:
-  Return(v4, v16, v17)
+  Return(v4, v5, v16)
 
 //! > ==========================================================================
 
```

### crates/cairo-lang-runner/src/profiling_test_data/major_test_cases
```diff
@@ -24,17 +24,17 @@ pow2_14000
 
 //! > expected_profiling_info
 Weight by sierra statement:
-  statement 27: 42003 (withdraw_gas([0], [1]) { fallthrough([4], [5]) 54([6], [7]) })
-  statement 30: 14001 (store_temp<RangeCheck>([4]) -> ([4]))
-  statement 31: 14001 (felt252_is_zero([8]) { fallthrough() 41([9]) })
-  statement 48: 14000 (store_temp<RangeCheck>([4]) -> ([4]))
-  statement 49: 14000 (store_temp<GasBuiltin>([13]) -> ([13]))
-  statement 50: 14000 (store_temp<felt252>([15]) -> ([15]))
-  statement 51: 14000 (store_temp<felt252>([17]) -> ([17]))
-  statement 52: 14000 (function_call<user@test::pow2_by_add_loop>([4], [13], [15], [17]) -> ([18], [19], [20]))
-  statement 53: 14000 (return([18], [19], [20]))
+  statement 26: 42003 (withdraw_gas([0], [1]) { fallthrough([4], [5]) 53([6], [7]) })
+  statement 29: 14001 (store_temp<RangeCheck>([4]) -> ([4]))
+  statement 30: 14001 (felt252_is_zero([8]) { fallthrough() 40([9]) })
+  statement 47: 14000 (store_temp<RangeCheck>([4]) -> ([4]))
+  statement 48: 14000 (store_temp<GasBuiltin>([13]) -> ([13]))
+  statement 49: 14000 (store_temp<felt252>([15]) -> ([15]))
+  statement 50: 14000 (store_temp<felt252>([17]) -> ([17]))
+  statement 51: 14000 (function_call<user@test::pow2_by_add_loop>([4], [13], [15], [17]) -> ([18], [19], [20]))
+  statement 52: 14000 (return([18], [19], [20]))
   statement 17: 3 (store_temp<core::panics::PanicResult::<((),)>>([12]) -> ([12]))
-  statement 39: 3 (store_temp<core::panics::PanicResult::<(core::felt252,)>>([12]) -> ([12]))
+  statement 38: 3 (store_temp<core::panics::PanicResult::<(core::felt252,)>>([12]) -> ([12]))
   statement 3: 1 (store_temp<RangeCheck>([0]) -> ([0]))
   statement 4: 1 (store_temp<GasBuiltin>([1]) -> ([1]))
   statement 5: 1 (store_temp<felt252>([2]) -> ([2]))
@@ -44,9 +44,9 @@ Weight by sierra statement:
   statement 15: 1 (store_temp<RangeCheck>([4]) -> ([4]))
   statement 16: 1 (store_temp<GasBuiltin>([9]) -> ([9]))
   statement 18: 1 (return([4], [9], [12]))
-  statement 37: 1 (store_temp<RangeCheck>([4]) -> ([4]))
-  statement 38: 1 (store_temp<GasBuiltin>([10]) -> ([10]))
-  statement 40: 1 (return([4], [10], [12]))
+  statement 36: 1 (store_temp<RangeCheck>([4]) -> ([4]))
+  statement 37: 1 (store_temp<GasBuiltin>([10]) -> ([10]))
+  statement 39: 1 (return([4], [10], [12]))
 Weight by concrete libfunc:
   libfunc withdraw_gas: 42003
   libfunc store_temp<RangeCheck>: 28004
@@ -156,54 +156,54 @@ validate_call
 
 //! > expected_profiling_info
 Weight by sierra statement:
-  statement 415: 14 (contract_address_try_from_felt252([5], [20]) { fallthrough([21], [22]) 476([23]) })
-  statement 624: 12 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([31]) -> ([31]))
-  statement 607: 10 (array_slice<felt252>([8], [12], [11], [13]) { fallthrough([14], [15]) 640([16]) })
-  statement 616: 10 (array_slice<felt252>([20], [3], [9], [21]) { fallthrough([24], [25]) 626([26]) })
-  statement 391: 9 (withdraw_gas([0], [1]) { fallthrough([5], [6]) 504([7], [8]) })
-  statement 434: 8 (store_temp<core::starknet::account::Call>([39]) -> ([39]))
-  statement 435: 8 (array_append<core::starknet::account::Call>([3], [39]) -> ([40]))
-  statement 601: 8 (u32_try_from_felt252([0], [7]) { fallthrough([8], [9]) 649([10]) })
-  statement 404: 6 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([14]) -> ([14]))
-  statement 614: 6 (u32_overflowing_sub([14], [18], [19]) { fallthrough([20], [21]) 630([22], [23]) })
-  statement 409: 4 (array_snapshot_pop_front<felt252>([15]) { fallthrough([16], [17]) 484([18]) })
-  statement 414: 4 (store_temp<Snapshot<Array<felt252>>>([16]) -> ([16]))
-  statement 418: 4 (array_snapshot_pop_front<felt252>([16]) { fallthrough([24], [25]) 467([26]) })
-  statement 423: 4 (store_temp<core::array::Span::<core::felt252>>([28]) -> ([28]))
-  statement 440: 4 (store_temp<core::array::Span::<core::felt252>>([33]) -> ([33]))
-  statement 441: 4 (store_temp<Array<core::starknet::account::Call>>([40]) -> ([40]))
-  statement 595: 4 (array_snapshot_pop_front<felt252>([2]) { fallthrough([3], [4]) 658([5]) })
-  statement 600: 4 (store_temp<Snapshot<Array<felt252>>>([3]) -> ([3]))
-  statement 613: 4 (store_temp<Snapshot<Array<felt252>>>([15]) -> ([15]))
-  statement 63: 3 (withdraw_gas([0], [1]) { fallthrough([43], [44]) 148([45], [46]) })
-  statement 87: 3 (array_snapshot_pop_front<felt252>([65]) { fallthrough([66], [67]) 99([68]) })
-  statement 103: 3 (withdraw_gas_all([56], [57], [72]) { fallthrough([73], [74]) 116([75], [76]) })
-  statement 114: 3 (store_temp<core::panics::PanicResult::<((),)>>([81]) -> ([81]))
-  statement 394: 3 (store_temp<RangeCheck>([5]) -> ([5]))
-  statement 395: 3 (felt252_is_zero([9]) { fallthrough() 406([10]) })
+  statement 408: 14 (contract_address_try_from_felt252([5], [20]) { fallthrough([21], [22]) 468([23]) })
+  statement 613: 12 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([31]) -> ([31]))
+  statement 596: 10 (array_slice<felt252>([8], [12], [11], [13]) { fallthrough([14], [15]) 629([16]) })
+  statement 605: 10 (array_slice<felt252>([20], [3], [9], [21]) { fallthrough([24], [25]) 615([26]) })
+  statement 384: 9 (withdraw_gas([0], [1]) { fallthrough([5], [6]) 496([7], [8]) })
+  statement 427: 8 (store_temp<core::starknet::account::Call>([39]) -> ([39]))
+  statement 428: 8 (array_append<core::starknet::account::Call>([3], [39]) -> ([40]))
+  statement 590: 8 (u32_try_from_felt252([0], [7]) { fallthrough([8], [9]) 638([10]) })
+  statement 397: 6 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([14]) -> ([14]))
+  statement 603: 6 (u32_overflowing_sub([14], [18], [19]) { fallthrough([20], [21]) 619([22], [23]) })
+  statement 402: 4 (array_snapshot_pop_front<felt252>([15]) { fallthrough([16], [17]) 476([18]) })
+  statement 407: 4 (store_temp<Snapshot<Array<felt252>>>([16]) -> ([16]))
+  statement 411: 4 (array_snapshot_pop_front<felt252>([16]) { fallthrough([24], [25]) 459([26]) })
+  statement 416: 4 (store_temp<core::array::Span::<core::felt252>>([28]) -> ([28]))
+  statement 433: 4 (store_temp<core::array::Span::<core::felt252>>([33]) -> ([33]))
+  statement 434: 4 (store_temp<Array<core::starknet::account::Call>>([40]) -> ([40]))
+  statement 584: 4 (array_snapshot_pop_front<felt252>([2]) { fallthrough([3], [4]) 647([5]) })
+  statement 589: 4 (store_temp<Snapshot<Array<felt252>>>([3]) -> ([3]))
+  statement 602: 4 (store_temp<Snapshot<Array<felt252>>>([15]) -> ([15]))
+  statement 63: 3 (withdraw_gas([0], [1]) { fallthrough([43], [44]) 146([45], [46]) })
+  statement 87: 3 (array_snapshot_pop_front<felt252>([65]) { fallthrough([66], [67]) 98([68]) })
+  statement 102: 3 (withdraw_gas_all([56], [57], [71]) { fallthrough([72], [73]) 115([74], [75]) })
+  statement 113: 3 (store_temp<core::panics::PanicResult::<((),)>>([80]) -> ([80]))
+  statement 387: 3 (store_temp<RangeCheck>([5]) -> ([5]))
+  statement 388: 3 (felt252_is_zero([9]) { fallthrough() 399([10]) })
   statement 61: 2 (store_local<Array<felt252>>([4], [3]) -> ([3]))
-  statement 68: 2 (array_snapshot_pop_front<felt252>([48]) { fallthrough([49], [50]) 136([51]) })
+  statement 68: 2 (array_snapshot_pop_front<felt252>([48]) { fallthrough([49], [50]) 134([51]) })
   statement 76: 2 (store_temp<core::array::Span::<core::felt252>>([55]) -> ([55]))
   statement 77: 2 (store_temp<Array<core::starknet::account::Call>>([53]) -> ([53]))
-  statement 101: 2 (get_builtin_costs() -> ([72]))
-  statement 413: 2 (store_temp<felt252>([20]) -> ([20]))
-  statement 417: 2 (store_temp<RangeCheck>([21]) -> ([21]))
-  statement 422: 2 (store_temp<RangeCheck>([21]) -> ([21]))
-  statement 424: 2 (function_call<user@core::array::SpanFelt252Serde::deserialize>([21], [28]) -> ([29], [30]))
-  statement 425: 2 (store_temp<felt252>([27]) -> ([27]))
-  statement 426: 2 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([30]) { fallthrough([31]) 456([32]) })
-  statement 429: 2 (enum_match<core::option::Option::<core::array::Span::<core::felt252>>>([34]) { fallthrough([35]) 445([36]) })
-  statement 438: 2 (store_temp<RangeCheck>([29]) -> ([29]))
-  statement 439: 2 (store_temp<GasBuiltin>([37]) -> ([37]))
-  statement 442: 2 (store_temp<felt252>([42]) -> ([42]))
-  statement 443: 2 (function_call<user@core::array::deserialize_array_helper::<core::starknet::account::Call, core::starknet::account::CallSerde, core::starknet::account::CallDrop>>([29], [37], [33], [40], [42]) -> ([43], [44], [45]))
-  statement 444: 2 (return([43], [44], [45]))
-  statement 599: 2 (store_temp<felt252>([7]) -> ([7]))
-  statement 606: 2 (store_temp<u32>([11]) -> ([11]))
-  statement 612: 2 (store_temp<u32>([18]) -> ([18]))
-  statement 617: 2 (branch_align() -> ())
-  statement 623: 2 (store_temp<RangeCheck>([24]) -> ([24]))
-  statement 625: 2 (return([24], [31]))
+  statement 100: 2 (get_builtin_costs() -> ([71]))
+  statement 406: 2 (store_temp<felt252>([20]) -> ([20]))
+  statement 410: 2 (store_temp<RangeCheck>([21]) -> ([21]))
+  statement 415: 2 (store_temp<RangeCheck>([21]) -> ([21]))
+  statement 417: 2 (function_call<user@core::array::SpanFelt252Serde::deserialize>([21], [28]) -> ([29], [30]))
+  statement 418: 2 (store_temp<felt252>([27]) -> ([27]))
+  statement 419: 2 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([30]) { fallthrough([31]) 449([32]) })
+  statement 422: 2 (enum_match<core::option::Option::<core::array::Span::<core::felt252>>>([34]) { fallthrough([35]) 438([36]) })
+  statement 431: 2 (store_temp<RangeCheck>([29]) -> ([29]))
+  statement 432: 2 (store_temp<GasBuiltin>([37]) -> ([37]))
+  statement 435: 2 (store_temp<felt252>([42]) -> ([42]))
+  statement 436: 2 (function_call<user@core::array::deserialize_array_helper::<core::starknet::account::Call, core::starknet::account::CallSerde, core::starknet::account::CallDrop>>([29], [37], [33], [40], [42]) -> ([43], [44], [45]))
+  statement 437: 2 (return([43], [44], [45]))
+  statement 588: 2 (store_temp<felt252>([7]) -> ([7]))
+  statement 595: 2 (store_temp<u32>([11]) -> ([11]))
+  statement 601: 2 (store_temp<u32>([18]) -> ([18]))
+  statement 606: 2 (branch_align() -> ())
+  statement 612: 2 (store_temp<RangeCheck>([24]) -> ([24]))
+  statement 614: 2 (return([24], [31]))
   statement 1: 1 (finalize_locals() -> ())
   statement 3: 1 (array_new<felt252>() -> ([5]))
   statement 5: 1 (store_temp<felt252>([6]) -> ([6]))
@@ -250,17 +250,17 @@ Weight by sierra statement:
   statement 75: 1 (store_temp<GasBuiltin>([44]) -> ([44]))
   statement 78: 1 (store_temp<felt252>([54]) -> ([54]))
   statement 79: 1 (function_call<user@core::array::deserialize_array_helper::<core::starknet::account::Call, core::starknet::account::CallSerde, core::starknet::account::CallDrop>>([43], [44], [55], [53], [54]) -> ([56], [57], [58]))
-  statement 80: 1 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([58]) { fallthrough([59]) 128([60]) })
-  statement 83: 1 (enum_match<core::option::Option::<core::array::Array::<core::starknet::account::Call>>>([62]) { fallthrough([63]) 121([64]) })
-  statement 102: 1 (store_temp<BuiltinCosts>([72]) -> ([72]))
-  statement 106: 1 (array_new<felt252>() -> ([78]))
-  statement 111: 1 (store_temp<RangeCheck>([73]) -> ([73]))
-  statement 112: 1 (store_temp<GasBuiltin>([77]) -> ([77]))
-  statement 113: 1 (store_temp<System>([2]) -> ([2]))
-  statement 115: 1 (return([73], [77], [2], [81]))
-  statement 402: 1 (store_temp<RangeCheck>([5]) -> ([5]))
-  statement 403: 1 (store_temp<GasBuiltin>([11]) -> ([11]))
-  statement 405: 1 (return([5], [11], [14]))
+  statement 80: 1 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([58]) { fallthrough([59]) 127([60]) })
+  statement 83: 1 (enum_match<core::option::Option::<core::array::Array::<core::starknet::account::Call>>>([62]) { fallthrough([63]) 120([64]) })
+  statement 101: 1 (store_temp<BuiltinCosts>([71]) -> ([71]))
+  statement 105: 1 (array_new<felt252>() -> ([77]))
+  statement 110: 1 (store_temp<RangeCheck>([72]) -> ([72]))
+  statement 111: 1 (store_temp<GasBuiltin>([76]) -> ([76]))
+  statement 112: 1 (store_temp<System>([2]) -> ([2]))
+  statement 114: 1 (return([72], [76], [2], [80]))
+  statement 395: 1 (store_temp<RangeCheck>([5]) -> ([5]))
+  statement 396: 1 (store_temp<GasBuiltin>([11]) -> ([11]))
+  statement 398: 1 (return([5], [11], [14]))
 Weight by concrete libfunc:
   libfunc store_temp<felt252>: 28
   libfunc array_slice<felt252>: 20
@@ -402,36 +402,36 @@ validate_call
 
 //! > expected_profiling_info
 Weight by sierra statement:
-  statement 379: 7 (contract_address_try_from_felt252([5], [20]) { fallthrough([21], [22]) 440([23]) })
-  statement 355: 6 (withdraw_gas([0], [1]) { fallthrough([5], [6]) 468([7], [8]) })
-  statement 368: 6 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([14]) -> ([14]))
-  statement 588: 6 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([31]) -> ([31]))
-  statement 571: 5 (array_slice<felt252>([8], [12], [11], [13]) { fallthrough([14], [15]) 604([16]) })
-  statement 580: 5 (array_slice<felt252>([20], [3], [9], [21]) { fallthrough([24], [25]) 590([26]) })
-  statement 398: 4 (store_temp<core::starknet::account::Call>([39]) -> ([39]))
-  statement 399: 4 (array_append<core::starknet::account::Call>([3], [39]) -> ([40]))
-  statement 565: 4 (u32_try_from_felt252([0], [7]) { fallthrough([8], [9]) 613([10]) })
-  statement 27: 3 (withdraw_gas([0], [1]) { fallthrough([19], [20]) 112([21], [22]) })
-  statement 51: 3 (array_snapshot_pop_front<felt252>([41]) { fallthrough([42], [43]) 63([44]) })
-  statement 67: 3 (withdraw_gas_all([32], [33], [48]) { fallthrough([49], [50]) 80([51], [52]) })
-  statement 78: 3 (store_temp<core::panics::PanicResult::<((),)>>([57]) -> ([57]))
-  statement 578: 3 (u32_overflowing_sub([14], [18], [19]) { fallthrough([20], [21]) 594([22], [23]) })
+  statement 372: 7 (contract_address_try_from_felt252([5], [20]) { fallthrough([21], [22]) 432([23]) })
+  statement 348: 6 (withdraw_gas([0], [1]) { fallthrough([5], [6]) 460([7], [8]) })
+  statement 361: 6 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([14]) -> ([14]))
+  statement 577: 6 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([31]) -> ([31]))
+  statement 560: 5 (array_slice<felt252>([8], [12], [11], [13]) { fallthrough([14], [15]) 593([16]) })
+  statement 569: 5 (array_slice<felt252>([20], [3], [9], [21]) { fallthrough([24], [25]) 579([26]) })
+  statement 391: 4 (store_temp<core::starknet::account::Call>([39]) -> ([39]))
+  statement 392: 4 (array_append<core::starknet::account::Call>([3], [39]) -> ([40]))
+  statement 554: 4 (u32_try_from_felt252([0], [7]) { fallthrough([8], [9]) 602([10]) })
+  statement 27: 3 (withdraw_gas([0], [1]) { fallthrough([19], [20]) 110([21], [22]) })
+  statement 51: 3 (array_snapshot_pop_front<felt252>([41]) { fallthrough([42], [43]) 62([44]) })
+  statement 66: 3 (withdraw_gas_all([32], [33], [47]) { fallthrough([48], [49]) 79([50], [51]) })
+  statement 77: 3 (store_temp<core::panics::PanicResult::<((),)>>([56]) -> ([56]))
+  statement 567: 3 (u32_overflowing_sub([14], [18], [19]) { fallthrough([20], [21]) 583([22], [23]) })
   statement 25: 2 (store_local<Array<felt252>>([4], [3]) -> ([3]))
-  statement 32: 2 (array_snapshot_pop_front<felt252>([24]) { fallthrough([25], [26]) 100([27]) })
+  statement 32: 2 (array_snapshot_pop_front<felt252>([24]) { fallthrough([25], [26]) 98([27]) })
   statement 40: 2 (store_temp<core::array::Span::<core::felt252>>([31]) -> ([31]))
   statement 41: 2 (store_temp<Array<core::starknet::account::Call>>([29]) -> ([29]))
-  statement 65: 2 (get_builtin_costs() -> ([48]))
-  statement 358: 2 (store_temp<RangeCheck>([5]) -> ([5]))
-  statement 359: 2 (felt252_is_zero([9]) { fallthrough() 370([10]) })
-  statement 373: 2 (array_snapshot_pop_front<felt252>([15]) { fallthrough([16], [17]) 448([18]) })
-  statement 378: 2 (store_temp<Snapshot<Array<felt252>>>([16]) -> ([16]))
-  statement 382: 2 (array_snapshot_pop_front<felt252>([16]) { fallthrough([24], [25]) 431([26]) })
-  statement 387: 2 (store_temp<core::array::Span::<core::felt252>>([28]) -> ([28]))
-  statement 404: 2 (store_temp<core::array::Span::<core::felt252>>([33]) -> ([33]))
-  statement 405: 2 (store_temp<Array<core::starknet::account::Call>>([40]) -> ([40]))
-  statement 559: 2 (array_snapshot_pop_front<felt252>([2]) { fallthrough([3], [4]) 622([5]) })
-  statement 564: 2 (store_temp<Snapshot<Array<felt252>>>([3]) -> ([3]))
-  statement 577: 2 (store_temp<Snapshot<Array<felt252>>>([15]) -> ([15]))
+  statement 64: 2 (get_builtin_costs() -> ([47]))
+  statement 351: 2 (store_temp<RangeCheck>([5]) -> ([5]))
+  statement 352: 2 (felt252_is_zero([9]) { fallthrough() 363([10]) })
+  statement 366: 2 (array_snapshot_pop_front<felt252>([15]) { fallthrough([16], [17]) 440([18]) })
+  statement 371: 2 (store_temp<Snapshot<Array<felt252>>>([16]) -> ([16]))
+  statement 375: 2 (array_snapshot_pop_front<felt252>([16]) { fallthrough([24], [25]) 423([26]) })
+  statement 380: 2 (store_temp<core::array::Span::<core::felt252>>([28]) -> ([28]))
+  statement 397: 2 (store_temp<core::array::Span::<core::felt252>>([33]) -> ([33]))
+  statement 398: 2 (store_temp<Array<core::starknet::account::Call>>([40]) -> ([40]))
+  statement 548: 2 (array_snapshot_pop_front<felt252>([2]) { fallthrough([3], [4]) 611([5]) })
+  statement 553: 2 (store_temp<Snapshot<Array<felt252>>>([3]) -> ([3]))
+  statement 566: 2 (store_temp<Snapshot<Array<felt252>>>([15]) -> ([15]))
   statement 1: 1 (finalize_locals() -> ())
   statement 3: 1 (array_new<felt252>() -> ([5]))
   statement 5: 1 (store_temp<felt252>([6]) -> ([6]))
@@ -454,35 +454,35 @@ Weight by sierra statement:
   statement 39: 1 (store_temp<GasBuiltin>([20]) -> ([20]))
   statement 42: 1 (store_temp<felt252>([30]) -> ([30]))
   statement 43: 1 (function_call<user@core::array::deserialize_array_helper::<core::starknet::account::Call, core::starknet::account::CallSerde, core::starknet::account::CallDrop>>([19], [20], [31], [29], [30]) -> ([32], [33], [34]))
-  statement 44: 1 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([34]) { fallthrough([35]) 92([36]) })
-  statement 47: 1 (enum_match<core::option::Option::<core::array::Array::<core::starknet::account::Call>>>([38]) { fallthrough([39]) 85([40]) })
-  statement 66: 1 (store_temp<BuiltinCosts>([48]) -> ([48]))
-  statement 70: 1 (array_new<felt252>() -> ([54]))
-  statement 75: 1 (store_temp<RangeCheck>([49]) -> ([49]))
-  statement 76: 1 (store_temp<GasBuiltin>([53]) -> ([53]))
-  statement 77: 1 (store_temp<System>([2]) -> ([2]))
-  statement 79: 1 (return([49], [53], [2], [57]))
-  statement 366: 1 (store_temp<RangeCheck>([5]) -> ([5]))
-  statement 367: 1 (store_temp<GasBuiltin>([11]) -> ([11]))
-  statement 369: 1 (return([5], [11], [14]))
-  statement 377: 1 (store_temp<felt252>([20]) -> ([20]))
-  statement 381: 1 (store_temp<RangeCheck>([21]) -> ([21]))
-  statement 386: 1 (store_temp<RangeCheck>([21]) -> ([21]))
-  statement 388: 1 (function_call<user@core::array::SpanFelt252Serde::deserialize>([21], [28]) -> ([29], [30]))
-  statement 389: 1 (store_temp<felt252>([27]) -> ([27]))
-  statement 390: 1 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([30]) { fallthrough([31]) 420([32]) })
-  statement 393: 1 (enum_match<core::option::Option::<core::array::Span::<core::felt252>>>([34]) { fallthrough([35]) 409([36]) })
-  statement 402: 1 (store_temp<RangeCheck>([29]) -> ([29]))
-  statement 403: 1 (store_temp<GasBuiltin>([37]) -> ([37]))
-  statement 406: 1 (store_temp<felt252>([42]) -> ([42]))
-  statement 407: 1 (function_call<user@core::array::deserialize_array_helper::<core::starknet::account::Call, core::starknet::account::CallSerde, core::starknet::account::CallDrop>>([29], [37], [33], [40], [42]) -> ([43], [44], [45]))
-  statement 408: 1 (return([43], [44], [45]))
-  statement 563: 1 (store_temp<felt252>([7]) -> ([7]))
-  statement 570: 1 (store_temp<u32>([11]) -> ([11]))
-  statement 576: 1 (store_temp<u32>([18]) -> ([18]))
-  statement 581: 1 (branch_align() -> ())
-  statement 587: 1 (store_temp<RangeCheck>([24]) -> ([24]))
-  statement 589: 1 (return([24], [31]))
+  statement 44: 1 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Array::<core::starknet::account::Call>>)>>([34]) { fallthrough([35]) 91([36]) })
+  statement 47: 1 (enum_match<core::option::Option::<core::array::Array::<core::starknet::account::Call>>>([38]) { fallthrough([39]) 84([40]) })
+  statement 65: 1 (store_temp<BuiltinCosts>([47]) -> ([47]))
+  statement 69: 1 (array_new<felt252>() -> ([53]))
+  statement 74: 1 (store_temp<RangeCheck>([48]) -> ([48]))
+  statement 75: 1 (store_temp<GasBuiltin>([52]) -> ([52]))
+  statement 76: 1 (store_temp<System>([2]) -> ([2]))
+  statement 78: 1 (return([48], [52], [2], [56]))
+  statement 359: 1 (store_temp<RangeCheck>([5]) -> ([5]))
+  statement 360: 1 (store_temp<GasBuiltin>([11]) -> ([11]))
+  statement 362: 1 (return([5], [11], [14]))
+  statement 370: 1 (store_temp<felt252>([20]) -> ([20]))
+  statement 374: 1 (store_temp<RangeCheck>([21]) -> ([21]))
+  statement 379: 1 (store_temp<RangeCheck>([21]) -> ([21]))
+  statement 381: 1 (function_call<user@core::array::SpanFelt252Serde::deserialize>([21], [28]) -> ([29], [30]))
+  statement 382: 1 (store_temp<felt252>([27]) -> ([27]))
+  statement 383: 1 (enum_match<core::panics::PanicResult::<(core::array::Span::<core::felt252>, core::option::Option::<core::array::Span::<core::felt252>>)>>([30]) { fallthrough([31]) 413([32]) })
+  statement 386: 1 (enum_match<core::option::Option::<core::array::Span::<core::felt252>>>([34]) { fallthrough([35]) 402([36]) })
+  statement 395: 1 (store_temp<RangeCheck>([29]) -> ([29]))
+  statement 396: 1 (store_temp<GasBuiltin>([37]) -> ([37]))
+  statement 399: 1 (store_temp<felt252>([42]) -> ([42]))
+  statement 400: 1 (function_call<user@core::array::deserialize_array_helper::<core::starknet::account::Call, core::starknet::account::CallSerde, core::starknet::account::CallDrop>>([29], [37], [33], [40], [42]) -> ([43], [44], [45]))
+  statement 401: 1 (return([43], [44], [45]))
+  statement 552: 1 (store_temp<felt252>([7]) -> ([7]))
+  statement 559: 1 (store_temp<u32>([11]) -> ([11]))
+  statement 565: 1 (store_temp<u32>([18]) -> ([18]))
+  statement 570: 1 (branch_align() -> ())
+  statement 576: 1 (store_temp<RangeCheck>([24]) -> ([24]))
+  statement 578: 1 (return([24], [31]))
 Weight by concrete libfunc:
   libfunc store_temp<felt252>: 12
   libfunc array_snapshot_pop_front<felt252>: 11
@@ -799,57 +799,57 @@ erc20_transfer
 
 //! > expected_profiling_info
 Weight by sierra statement:
-  statement 302: 10 (storage_base_address_from_felt252([0], [29]) -> ([30], [31]))
-  statement 386: 10 (storage_base_address_from_felt252([89], [108]) -> ([109], [110]))
-  statement 416: 10 (storage_base_address_from_felt252([109], [138]) -> ([139], [140]))
-  statement 501: 10 (storage_base_address_from_felt252([198], [217]) -> ([218], [219]))
-  statement 537: 9 (emit_event_syscall([233], [234], [250], [251]) { fallthrough([252], [253]) 550([254], [255], [256]) })
-  statement 395: 8 (storage_write_syscall([90], [55], [115], [113], [111]) { fallthrough([116], [117]) 720([118], [119], [120]) })
-  statement 403: 8 (storage_write_syscall([116], [117], [114], [123], [121]) { fallthrough([124], [125]) 704([126], [127], [128]) })
-  statement 510: 8 (storage_write_syscall([199], [164], [224], [222], [220]) { fallthrough([225], [226]) 579([227], [228], [229]) })
-  statement 518: 8 (storage_write_syscall([225], [226], [223], [232], [230]) { fallthrough([233], [234]) 563([235], [236], [237]) })
-  statement 61: 7 (contract_address_try_from_felt252([5], [14]) { fallthrough([15], [16]) 217([17]) })
-  statement 315: 7 (storage_read_syscall([1], [3], [40], [38]) { fallthrough([41], [42], [43]) 827([44], [45], [46]) })
-  statement 327: 7 (storage_read_syscall([41], [42], [39], [53]) { fallthrough([54], [55], [56]) 785([57], [58], [59]) })
-  statement 430: 7 (storage_read_syscall([124], [125], [149], [147]) { fallthrough([150], [151], [152]) 686([153], [154], [155]) })
-  statement 442: 7 (storage_read_syscall([150], [151], [148], [162]) { fallthrough([163], [164], [165]) 644([166], [167], [168]) })
-  statement 102: 6 (withdraw_gas_all([33], [6], [44]) { fallthrough([45], [46]) 168([47], [48]) })
-  statement 105: 5 (get_execution_info_v2_syscall([46], [3]) { fallthrough([49], [50], [51]) 153([52], [53], [54]) })
-  statement 526: 5 (store_temp<test::erc_20::Event>([243]) -> ([243]))
+  statement 295: 10 (storage_base_address_from_felt252([0], [27]) -> ([28], [29]))
+  statement 379: 10 (storage_base_address_from_felt252([87], [106]) -> ([107], [108]))
+  statement 409: 10 (storage_base_address_from_felt252([107], [136]) -> ([137], [138]))
+  statement 494: 10 (storage_base_address_from_felt252([196], [215]) -> ([216], [217]))
+  statement 530: 9 (emit_event_syscall([231], [232], [248], [249]) { fallthrough([250], [251]) 543([252], [253], [254]) })
+  statement 388: 8 (storage_write_syscall([88], [53], [113], [111], [109]) { fallthrough([114], [115]) 701([116], [117], [118]) })
+  statement 396: 8 (storage_write_syscall([114], [115], [112], [121], [119]) { fallthrough([122], [123]) 687([124], [125], [126]) })
+  statement 503: 8 (storage_write_syscall([197], [162], [222], [220], [218]) { fallthrough([223], [224]) 568([225], [226], [227]) })
+  statement 511: 8 (storage_write_syscall([223], [224], [221], [230], [228]) { fallthrough([231], [232]) 554([233], [234], [235]) })
+  statement 60: 7 (contract_address_try_from_felt252([5], [14]) { fallthrough([15], [16]) 212([17]) })
+  statement 308: 7 (storage_read_syscall([1], [3], [38], [36]) { fallthrough([39], [40], [41]) 804([42], [43], [44]) })
+  statement 320: 7 (storage_read_syscall([39], [40], [37], [51]) { fallthrough([52], [53], [54]) 764([55], [56], [57]) })
+  statement 423: 7 (storage_read_syscall([122], [123], [147], [145]) { fallthrough([148], [149], [150]) 671([151], [152], [153]) })
+  statement 435: 7 (storage_read_syscall([148], [149], [146], [160]) { fallthrough([161], [162], [163]) 631([164], [165], [166]) })
+  statement 100: 6 (withdraw_gas_all([33], [6], [43]) { fallthrough([44], [45]) 163([46], [47]) })
+  statement 103: 5 (get_execution_info_v2_syscall([45], [3]) { fallthrough([48], [49], [50]) 150([51], [52], [53]) })
+  statement 519: 5 (store_temp<test::erc_20::Event>([241]) -> ([241]))
   statement 37: 3 (store_temp<core::panics::PanicResult::<((),)>>([28]) -> ([28]))
-  statement 51: 3 (withdraw_gas([1], [2]) { fallthrough([5], [6]) 236([7], [8]) })
-  statement 82: 3 (array_snapshot_pop_front<felt252>([28]) { fallthrough([38], [39]) 98([40]) })
-  statement 138: 3 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>,)>>([76]) -> ([76]))
-  statement 338: 3 (u128_overflowing_sub([60], [61], [69]) { fallthrough([70], [71]) 348([72], [73]) })
-  statement 356: 3 (u128_overflowing_sub([77], [48], [68]) { fallthrough([84], [85]) 364([86], [87]) })
-  statement 453: 3 (u128_overflowing_add([169], [170], [178]) { fallthrough([179], [180]) 463([181], [182]) })
-  statement 471: 3 (u128_overflowing_add([186], [157], [177]) { fallthrough([193], [194]) 479([195], [196]) })
-  statement 548: 3 (store_temp<core::panics::PanicResult::<(test::erc_20::ContractState, ())>>([260]) -> ([260]))
+  statement 50: 3 (withdraw_gas([1], [2]) { fallthrough([5], [6]) 231([7], [8]) })
+  statement 81: 3 (array_snapshot_pop_front<felt252>([28]) { fallthrough([38], [39]) 96([40]) })
+  statement 136: 3 (store_temp<core::panics::PanicResult::<(core::array::Span::<core::felt252>,)>>([75]) -> ([75]))
+  statement 331: 3 (u128_overflowing_sub([58], [59], [67]) { fallthrough([68], [69]) 341([70], [71]) })
+  statement 349: 3 (u128_overflowing_sub([75], [46], [66]) { fallthrough([82], [83]) 357([84], [85]) })
+  statement 446: 3 (u128_overflowing_add([167], [168], [176]) { fallthrough([177], [178]) 456([179], [180]) })
+  statement 464: 3 (u128_overflowing_add([184], [155], [175]) { fallthrough([191], [192]) 472([193], [194]) })
+  statement 541: 3 (store_temp<core::panics::PanicResult::<(test::erc_20::ContractState, ())>>([258]) -> ([258]))
   statement 1: 2 (const_as_box<Const<Tuple<felt252>, Const<felt252, 2>>, 0>() -> ([4]))
   statement 4: 2 (store_temp<core::array::Span::<core::felt252>>([6]) -> ([6]))
   statement 24: 2 (store_temp<core::array::Span::<core::felt252>>([17]) -> ([17]))
-  statement 55: 2 (array_snapshot_pop_front<felt252>([9]) { fallthrough([10], [11]) 223([12]) })
-  statement 60: 2 (store_temp<Snapshot<Array<felt252>>>([10]) -> ([10]))
-  statement 64: 2 (array_snapshot_pop_front<felt252>([10]) { fallthrough([18], [19]) 203([20]) })
-  statement 69: 2 (store_temp<Snapshot<Array<felt252>>>([18]) -> ([18]))
-  statement 70: 2 (u128s_from_felt252([15], [22]) { fallthrough([23], [24]) 194([25], [26], [27]) })
-  statement 73: 2 (array_snapshot_pop_front<felt252>([18]) { fallthrough([28], [29]) 186([30]) })
-  statement 78: 2 (store_temp<Snapshot<Array<felt252>>>([28]) -> ([28]))
-  statement 79: 2 (u128s_from_felt252([23], [32]) { fallthrough([33], [34]) 176([35], [36], [37]) })
-  statement 100: 2 (get_builtin_costs() -> ([44]))
-  statement 122: 2 (store_temp<core::integer::u256>([56]) -> ([56]))
-  statement 300: 2 (pedersen([2], [27], [21]) -> ([28], [29]))
-  statement 320: 2 (u128s_from_felt252([30], [43]) { fallthrough([47], [48]) 802([49], [50], [51]) })
-  statement 332: 2 (u128s_from_felt252([47], [56]) { fallthrough([60], [61]) 772([62], [63], [64]) })
-  statement 384: 2 (pedersen([28], [106], [102]) -> ([107], [108]))
-  statement 414: 2 (pedersen([107], [136], [130]) -> ([137], [138]))
-  statement 435: 2 (u128s_from_felt252([139], [152]) { fallthrough([156], [157]) 661([158], [159], [160]) })
-  statement 447: 2 (u128s_from_felt252([156], [165]) { fallthrough([169], [170]) 631([171], [172], [173]) })
-  statement 499: 2 (pedersen([137], [215], [211]) -> ([216], [217]))
-  statement 527: 2 (store_temp<Array<felt252>>([238]) -> ([238]))
-  statement 528: 2 (store_temp<Array<felt252>>([239]) -> ([239]))
-  statement 904: 2 (store_temp<Array<felt252>>([6]) -> ([6]))
-  statement 905: 2 (store_temp<Array<felt252>>([34]) -> ([34]))
+  statement 54: 2 (array_snapshot_pop_front<felt252>([9]) { fallthrough([10], [11]) 218([12]) })
+  statement 59: 2 (store_temp<Snapshot<Array<felt252>>>([10]) -> ([10]))
+  statement 63: 2 (array_snapshot_pop_front<felt252>([10]) { fallthrough([18], [19]) 198([20]) })
+  statement 68: 2 (store_temp<Snapshot<Array<felt252>>>([18]) -> ([18]))
+  statement 69: 2 (u128s_from_felt252([15], [22]) { fallthrough([23], [24]) 189([25], [26], [27]) })
+  statement 72: 2 (array_snapshot_pop_front<felt252>([18]) { fallthrough([28], [29]) 181([30]) })
+  statement 77: 2 (store_temp<Snapshot<Array<felt252>>>([28]) -> ([28]))
+  statement 78: 2 (u128s_from_felt252([23], [32]) { fallthrough([33], [34]) 171([35], [36], [37]) })
+  statement 98: 2 (get_builtin_costs() -> ([43]))
+  statement 120: 2 (store_temp<core::integer::u256>([55]) -> ([55]))
+  statement 293: 2 (pedersen([2], [25], [19]) -> ([26], [27]))
+  statement 313: 2 (u128s_from_felt252([28], [41]) { fallthrough([45], [46]) 779([47], [48], [49]) })
+  statement 325: 2 (u128s_from_felt252([45], [54]) { fallthrough([58], [59]) 751([60], [61], [62]) })
+  statement 377: 2 (pedersen([26], [104], [100]) -> ([105], [106]))
+  statement 407: 2 (pedersen([105], [134], [128]) -> ([135], [136]))
+  statement 428: 2 (u128s_from_felt252([137], [150]) { fallthrough([154], [155]) 646([156], [157], [158]) })
+  statement 440: 2 (u128s_from_felt252([154], [163]) { fallthrough([167], [168]) 618([169], [170], [171]) })
+  statement 492: 2 (pedersen([135], [213], [209]) -> ([214], [215]))
+  statement 520: 2 (store_temp<Array<felt252>>([236]) -> ([236]))
+  statement 521: 2 (store_temp<Array<felt252>>([237]) -> ([237]))
+  statement 879: 2 (store_temp<Array<felt252>>([6]) -> ([6]))
+  statement 880: 2 (store_temp<Array<felt252>>([34]) -> ([34]))
   statement 5: 1 (cheatcode<10052436086942832998170947883001859293934451>([6]) -> ([7]))
   statement 7: 1 (array_new<felt252>() -> ([8]))
   statement 9: 1 (store_temp<felt252>([9]) -> ([9]))
@@ -869,121 +869,121 @@ Weight by sierra statement:
   statement 35: 1 (store_temp<Pedersen>([18]) -> ([18]))
   statement 36: 1 (store_temp<System>([21]) -> ([21]))
   statement 38: 1 (return([19], [25], [18], [21], [28]))
-  statement 54: 1 (store_temp<RangeCheck>([5]) -> ([5]))
-  statement 59: 1 (store_temp<felt252>([14]) -> ([14]))
-  statement 63: 1 (store_temp<RangeCheck>([15]) -> ([15]))
-  statement 68: 1 (store_temp<felt252>([22]) -> ([22]))
-  statement 72: 1 (store_temp<RangeCheck>([23]) -> ([23]))
-  statement 77: 1 (store_temp<felt252>([32]) -> ([32]))
-  statement 81: 1 (store_temp<RangeCheck>([33]) -> ([33]))
-  statement 101: 1 (store_temp<BuiltinCosts>([44]) -> ([44]))
-  statement 104: 1 (store_temp<RangeCheck>([45]) -> ([45]))
-  statement 107: 1 (store_temp<Box<core::starknet::info::v2::ExecutionInfo>>([51]) -> ([51]))
-  statement 116: 1 (store_temp<RangeCheck>([45]) -> ([45]))
-  statement 117: 1 (store_temp<GasBuiltin>([49]) -> ([49]))
-  statement 118: 1 (store_temp<Pedersen>([0]) -> ([0]))
-  statement 119: 1 (store_temp<System>([50]) -> ([50]))
-  statement 120: 1 (store_temp<ContractAddress>([59]) -> ([59]))
-  statement 121: 1 (store_temp<ContractAddress>([16]) -> ([16]))
-  statement 123: 1 (function_call<user@test::erc_20::StorageImpl::transfer_helper>([45], [49], [0], [50], [62], [59], [16], [56]) -> ([63], [64], [65], [66], [67]))
-  statement 124: 1 (enum_match<core::panics::PanicResult::<(test::erc_20::ContractState, ())>>([67]) { fallthrough([68]) 140([69]) })
-  statement 128: 1 (array_new<felt252>() -> ([71]))
-  statement 134: 1 (store_temp<Pedersen>([65]) -> ([65]))
-  statement 135: 1 (store_temp<RangeCheck>([63]) -> ([63]))
-  statement 136: 1 (store_temp<GasBuiltin>([70]) -> ([70]))
-  statement 137: 1 (store_temp<System>([66]) -> ([66]))
-  statement 139: 1 (return([65], [63], [70], [66], [76]))
-  statement 255: 1 (felt252_is_zero([9]) { fallthrough() 270([10]) })
-  statement 274: 1 (felt252_is_zero([15]) { fallthrough() 289([16]) })
-  statement 299: 1 (store_temp<felt252>([27]) -> ([27]))
-  statement 301: 1 (store_temp<felt252>([29]) -> ([29]))
-  statement 312: 1 (store_temp<u32>([40]) -> ([40]))
-  statement 313: 1 (store_temp<Pedersen>([28]) -> ([28]))
-  statement 314: 1 (store_temp<RangeCheck>([30]) -> ([30]))
-  statement 317: 1 (store_temp<felt252>([43]) -> ([43]))
-  statement 318: 1 (store_temp<GasBuiltin>([41]) -> ([41]))
-  statement 319: 1 (store_temp<System>([42]) -> ([42]))
-  statement 324: 1 (store_temp<u32>([39]) -> ([39]))
-  statement 325: 1 (store_temp<StorageAddress>([53]) -> ([53]))
-  statement 326: 1 (store_temp<RangeCheck>([47]) -> ([47]))
-  statement 329: 1 (store_temp<felt252>([56]) -> ([56]))
-  statement 330: 1 (store_temp<GasBuiltin>([54]) -> ([54]))
-  statement 331: 1 (store_temp<System>([55]) -> ([55]))
-  statement 339: 1 (branch_align() -> ())
-  statement 343: 1 (store_temp<RangeCheck>([70]) -> ([77]))
-  statement 344: 1 (store_temp<GasBuiltin>([74]) -> ([78]))
-  statement 345: 1 (store_temp<u128>([71]) -> ([79]))
-  statement 346: 1 (store_temp<core::bool>([76]) -> ([80]))
-  statement 347: 1 (jump() { 356() })
-  statement 357: 1 (branch_align() -> ())
-  statement 359: 1 (store_temp<RangeCheck>([84]) -> ([89]))
-  statement 360: 1 (store_temp<GasBuiltin>([88]) -> ([90]))
-  statement 361: 1 (store_temp<u128>([85]) -> ([91]))
-  statement 362: 1 (store_temp<u128>([79]) -> ([92]))
-  statement 363: 1 (jump() { 374() })
-  statement 374: 1 (enum_match<core::bool>([80]) { fallthrough([99]) 739([100]) })
-  statement 383: 1 (store_temp<felt252>([106]) -> ([106]))
-  statement 385: 1 (store_temp<felt252>([108]) -> ([108]))
-  statement 392: 1 (store_temp<u32>([115]) -> ([115]))
-  statement 393: 1 (store_temp<Pedersen>([107]) -> ([107]))
-  statement 394: 1 (store_temp<RangeCheck>([109]) -> ([109]))
-  statement 400: 1 (store_temp<GasBuiltin>([116]) -> ([116]))
-  statement 401: 1 (store_temp<u32>([114]) -> ([114]))
-  statement 402: 1 (store_temp<StorageAddress>([123]) -> ([123]))
-  statement 413: 1 (store_temp<felt252>([136]) -> ([136]))
-  statement 415: 1 (store_temp<felt252>([138]) -> ([138]))
-  statement 426: 1 (store_temp<GasBuiltin>([124]) -> ([124]))
-  statement 427: 1 (store_temp<u32>([149]) -> ([149]))
-  statement 428: 1 (store_temp<Pedersen>([137]) -> ([137]))
-  statement 429: 1 (store_temp<RangeCheck>([139]) -> ([139]))
-  statement 432: 1 (store_temp<felt252>([152]) -> ([152]))
-  statement 433: 1 (store_temp<GasBuiltin>([150]) -> ([150]))
-  statement 434: 1 (store_temp<System>([151]) -> ([151]))
-  statement 439: 1 (store_temp<u32>([148]) -> ([148]))
-  statement 440: 1 (store_temp<StorageAddress>([162]) -> ([162]))
-  statement 441: 1 (store_temp<RangeCheck>([156]) -> ([156]))
-  statement 444: 1 (store_temp<felt252>([165]) -> ([165]))
-  statement 445: 1 (store_temp<GasBuiltin>([163]) -> ([163]))
-  statement 446: 1 (store_temp<System>([164]) -> ([164]))
-  statement 454: 1 (branch_align() -> ())
-  statement 458: 1 (store_temp<RangeCheck>([179]) -> ([186]))
-  statement 459: 1 (store_temp<GasBuiltin>([183]) -> ([187]))
-  statement 460: 1 (store_temp<u128>([180]) -> ([188]))
-  statement 461: 1 (store_temp<core::bool>([185]) -> ([189]))
-  statement 462: 1 (jump() { 471() })
-  statement 472: 1 (branch_align() -> ())
-  statement 474: 1 (store_temp<RangeCheck>([193]) -> ([198]))
-  statement 475: 1 (store_temp<GasBuiltin>([197]) -> ([199]))
-  statement 476: 1 (store_temp<u128>([194]) -> ([200]))
-  statement 477: 1 (store_temp<u128>([188]) -> ([201]))
-  statement 478: 1 (jump() { 489() })
-  statement 489: 1 (enum_match<core::bool>([189]) { fallthrough([208]) 598([209]) })
-  statement 498: 1 (store_temp<felt252>([215]) -> ([215]))
-  statement 500: 1 (store_temp<felt252>([217]) -> ([217]))
-  statement 507: 1 (store_temp<u32>([224]) -> ([224]))
-  statement 508: 1 (store_temp<Pedersen>([216]) -> ([216]))
-  statement 509: 1 (store_temp<RangeCheck>([218]) -> ([218]))
-  statement 515: 1 (store_temp<GasBuiltin>([225]) -> ([225]))
-  statement 516: 1 (store_temp<u32>([223]) -> ([223]))
-  statement 517: 1 (store_temp<StorageAddress>([232]) -> ([232]))
-  statement 520: 1 (array_new<felt252>() -> ([238]))
-  statement 521: 1 (array_new<felt252>() -> ([239]))
-  statement 529: 1 (function_call<user@test::erc_20::EventIsEvent::append_keys_and_data>([243], [238], [239]) -> ([244], [245]))
-  statement 536: 1 (store_temp<GasBuiltin>([233]) -> ([233]))
-  statement 539: 1 (store_temp<GasBuiltin>([252]) -> ([252]))
-  statement 544: 1 (store_temp<RangeCheck>([218]) -> ([218]))
-  statement 545: 1 (store_temp<GasBuiltin>([257]) -> ([257]))
-  statement 546: 1 (store_temp<Pedersen>([216]) -> ([216]))
-  statement 547: 1 (store_temp<System>([253]) -> ([253]))
-  statement 549: 1 (return([218], [257], [216], [253], [260]))
-  statement 871: 1 (enum_match<test::erc_20::Event>([0]) { fallthrough([3]) 907([4]) })
-  statement 874: 1 (store_temp<felt252>([5]) -> ([5]))
-  statement 875: 1 (array_append<felt252>([1], [5]) -> ([6]))
-  statement 882: 1 (array_append<felt252>([2], [12]) -> ([13]))
-  statement 889: 1 (array_append<felt252>([13], [19]) -> ([20]))
-  statement 898: 1 (array_append<felt252>([20], [28]) -> ([29]))
-  statement 903: 1 (array_append<felt252>([29], [33]) -> ([34]))
-  statement 906: 1 (return([6], [34]))
+  statement 53: 1 (store_temp<RangeCheck>([5]) -> ([5]))
+  statement 58: 1 (store_temp<felt252>([14]) -> ([14]))
+  statement 62: 1 (store_temp<RangeCheck>([15]) -> ([15]))
+  statement 67: 1 (store_temp<felt252>([22]) -> ([22]))
+  statement 71: 1 (store_temp<RangeCheck>([23]) -> ([23]))
+  statement 76: 1 (store_temp<felt252>([32]) -> ([32]))
+  statement 80: 1 (store_temp<RangeCheck>([33]) -> ([33]))
+  statement 99: 1 (store_temp<BuiltinCosts>([43]) -> ([43]))
+  statement 102: 1 (store_temp<RangeCheck>([44]) -> ([44]))
+  statement 105: 1 (store_temp<Box<core::starknet::info::v2::ExecutionInfo>>([50]) -> ([50]))
+  statement 114: 1 (store_temp<RangeCheck>([44]) -> ([44]))
+  statement 115: 1 (store_temp<GasBuiltin>([48]) -> ([48]))
+  statement 116: 1 (store_temp<Pedersen>([0]) -> ([0]))
+  statement 117: 1 (store_temp<System>([49]) -> ([49]))
+  statement 118: 1 (store_temp<ContractAddress>([58]) -> ([58]))
+  statement 119: 1 (store_temp<ContractAddress>([16]) -> ([16]))
+  statement 121: 1 (function_call<user@test::erc_20::StorageImpl::transfer_helper>([44], [48], [0], [49], [61], [58], [16], [55]) -> ([62], [63], [64], [65], [66]))
+  statement 122: 1 (enum_match<core::panics::PanicResult::<(test::erc_20::ContractState, ())>>([66]) { fallthrough([67]) 138([68]) })
+  statement 126: 1 (array_new<felt252>() -> ([70]))
+  statement 132: 1 (store_temp<Pedersen>([64]) -> ([64]))
+  statement 133: 1 (store_temp<RangeCheck>([62]) -> ([62]))
+  statement 134: 1 (store_temp<GasBuiltin>([69]) -> ([69]))
+  statement 135: 1 (store_temp<System>([65]) -> ([65]))
+  statement 137: 1 (return([64], [62], [69], [65], [75]))
+  statement 250: 1 (felt252_is_zero([9]) { fallthrough() 264([10]) })
+  statement 268: 1 (felt252_is_zero([14]) { fallthrough() 282([15]) })
+  statement 292: 1 (store_temp<felt252>([25]) -> ([25]))
+  statement 294: 1 (store_temp<felt252>([27]) -> ([27]))
+  statement 305: 1 (store_temp<u32>([38]) -> ([38]))
+  statement 306: 1 (store_temp<Pedersen>([26]) -> ([26]))
+  statement 307: 1 (store_temp<RangeCheck>([28]) -> ([28]))
+  statement 310: 1 (store_temp<felt252>([41]) -> ([41]))
+  statement 311: 1 (store_temp<GasBuiltin>([39]) -> ([39]))
+  statement 312: 1 (store_temp<System>([40]) -> ([40]))
+  statement 317: 1 (store_temp<u32>([37]) -> ([37]))
+  statement 318: 1 (store_temp<StorageAddress>([51]) -> ([51]))
+  statement 319: 1 (store_temp<RangeCheck>([45]) -> ([45]))
+  statement 322: 1 (store_temp<felt252>([54]) -> ([54]))
+  statement 323: 1 (store_temp<GasBuiltin>([52]) -> ([52]))
+  statement 324: 1 (store_temp<System>([53]) -> ([53]))
+  statement 332: 1 (branch_align() -> ())
+  statement 336: 1 (store_temp<RangeCheck>([68]) -> ([75]))
+  statement 337: 1 (store_temp<GasBuiltin>([72]) -> ([76]))
+  statement 338: 1 (store_temp<u128>([69]) -> ([77]))
+  statement 339: 1 (store_temp<core::bool>([74]) -> ([78]))
+  statement 340: 1 (jump() { 349() })
+  statement 350: 1 (branch_align() -> ())
+  statement 352: 1 (store_temp<RangeCheck>([82]) -> ([87]))
+  statement 353: 1 (store_temp<GasBuiltin>([86]) -> ([88]))
+  statement 354: 1 (store_temp<u128>([83]) -> ([89]))
+  statement 355: 1 (store_temp<u128>([77]) -> ([90]))
+  statement 356: 1 (jump() { 367() })
+  statement 367: 1 (enum_match<core::bool>([78]) { fallthrough([97]) 718([98]) })
+  statement 376: 1 (store_temp<felt252>([104]) -> ([104]))
+  statement 378: 1 (store_temp<felt252>([106]) -> ([106]))
+  statement 385: 1 (store_temp<u32>([113]) -> ([113]))
+  statement 386: 1 (store_temp<Pedersen>([105]) -> ([105]))
+  statement 387: 1 (store_temp<RangeCheck>([107]) -> ([107]))
+  statement 393: 1 (store_temp<GasBuiltin>([114]) -> ([114]))
+  statement 394: 1 (store_temp<u32>([112]) -> ([112]))
+  statement 395: 1 (store_temp<StorageAddress>([121]) -> ([121]))
+  statement 406: 1 (store_temp<felt252>([134]) -> ([134]))
+  statement 408: 1 (store_temp<felt252>([136]) -> ([136]))
+  statement 419: 1 (store_temp<GasBuiltin>([122]) -> ([122]))
+  statement 420: 1 (store_temp<u32>([147]) -> ([147]))
+  statement 421: 1 (store_temp<Pedersen>([135]) -> ([135]))
+  statement 422: 1 (store_temp<RangeCheck>([137]) -> ([137]))
+  statement 425: 1 (store_temp<felt252>([150]) -> ([150]))
+  statement 426: 1 (store_temp<GasBuiltin>([148]) -> ([148]))
+  statement 427: 1 (store_temp<System>([149]) -> ([149]))
+  statement 432: 1 (store_temp<u32>([146]) -> ([146]))
+  statement 433: 1 (store_temp<StorageAddress>([160]) -> ([160]))
+  statement 434: 1 (store_temp<RangeCheck>([154]) -> ([154]))
+  statement 437: 1 (store_temp<felt252>([163]) -> ([163]))
+  statement 438: 1 (store_temp<GasBuiltin>([161]) -> ([161]))
+  statement 439: 1 (store_temp<System>([162]) -> ([162]))
+  statement 447: 1 (branch_align() -> ())
+  statement 451: 1 (store_temp<RangeCheck>([177]) -> ([184]))
+  statement 452: 1 (store_temp<GasBuiltin>([181]) -> ([185]))
+  statement 453: 1 (store_temp<u128>([178]) -> ([186]))
+  statement 454: 1 (store_temp<core::bool>([183]) -> ([187]))
+  statement 455: 1 (jump() { 464() })
+  statement 465: 1 (branch_align() -> ())
+  statement 467: 1 (store_temp<RangeCheck>([191]) -> ([196]))
+  statement 468: 1 (store_temp<GasBuiltin>([195]) -> ([197]))
+  statement 469: 1 (store_temp<u128>([192]) -> ([198]))
+  statement 470: 1 (store_temp<u128>([186]) -> ([199]))
+  statement 471: 1 (jump() { 482() })
+  statement 482: 1 (enum_match<core::bool>([187]) { fallthrough([206]) 585([207]) })
+  statement 491: 1 (store_temp<felt252>([213]) -> ([213]))
+  statement 493: 1 (store_temp<felt252>([215]) -> ([215]))
+  statement 500: 1 (store_temp<u32>([222]) -> ([222]))
+  statement 501: 1 (store_temp<Pedersen>([214]) -> ([214]))
+  statement 502: 1 (store_temp<RangeCheck>([216]) -> ([216]))
+  statement 508: 1 (store_temp<GasBuiltin>([223]) -> ([223]))
+  statement 509: 1 (store_temp<u32>([221]) -> ([221]))
+  statement 510: 1 (store_temp<StorageAddress>([230]) -> ([230]))
+  statement 513: 1 (array_new<felt252>() -> ([236]))
+  statement 514: 1 (array_new<felt252>() -> ([237]))
+  statement 522: 1 (function_call<user@test::erc_20::EventIsEvent::append_keys_and_data>([241], [236], [237]) -> ([242], [243]))
+  statement 529: 1 (store_temp<GasBuiltin>([231]) -> ([231]))
+  statement 532: 1 (store_temp<GasBuiltin>([250]) -> ([250]))
+  statement 537: 1 (store_temp<RangeCheck>([216]) -> ([216]))
+  statement 538: 1 (store_temp<GasBuiltin>([255]) -> ([255]))
+  statement 539: 1 (store_temp<Pedersen>([214]) -> ([214]))
+  statement 540: 1 (store_temp<System>([251]) -> ([251]))
+  statement 542: 1 (return([216], [255], [214], [251], [258]))
+  statement 846: 1 (enum_match<test::erc_20::Event>([0]) { fallthrough([3]) 882([4]) })
+  statement 849: 1 (store_temp<felt252>([5]) -> ([5]))
+  statement 850: 1 (array_append<felt252>([1], [5]) -> ([6]))
+  statement 857: 1 (array_append<felt252>([2], [12]) -> ([13]))
+  statement 864: 1 (array_append<felt252>([13], [19]) -> ([20]))
+  statement 873: 1 (array_append<felt252>([20], [28]) -> ([29]))
+  statement 878: 1 (array_append<felt252>([29], [33]) -> ([34]))
+  statement 881: 1 (return([6], [34]))
 Weight by concrete libfunc:
   libfunc storage_base_address_from_felt252: 40
   libfunc storage_write_syscall: 32
```

### crates/cairo-lang-runner/src/profiling_test_data/profiling
```diff
@@ -161,16 +161,16 @@ main
 
 //! > expected_profiling_info
 Weight by sierra statement:
-  statement 25: 18 (withdraw_gas([0], [1]) { fallthrough([3], [4]) 49([5], [6]) })
-  statement 28: 6 (store_temp<RangeCheck>([3]) -> ([3]))
-  statement 29: 6 (felt252_is_zero([7]) { fallthrough() 39([8]) })
-  statement 44: 5 (store_temp<RangeCheck>([3]) -> ([3]))
-  statement 45: 5 (store_temp<GasBuiltin>([13]) -> ([13]))
-  statement 46: 5 (store_temp<felt252>([15]) -> ([15]))
-  statement 47: 5 (function_call<user@test::main[31-113]>([3], [13], [15]) -> ([16], [17], [18]))
-  statement 48: 5 (return([16], [17], [18]))
+  statement 24: 18 (withdraw_gas([0], [1]) { fallthrough([3], [4]) 48([5], [6]) })
+  statement 27: 6 (store_temp<RangeCheck>([3]) -> ([3]))
+  statement 28: 6 (felt252_is_zero([7]) { fallthrough() 38([8]) })
+  statement 43: 5 (store_temp<RangeCheck>([3]) -> ([3]))
+  statement 44: 5 (store_temp<GasBuiltin>([13]) -> ([13]))
+  statement 45: 5 (store_temp<felt252>([15]) -> ([15]))
+  statement 46: 5 (function_call<user@test::main[31-113]>([3], [13], [15]) -> ([16], [17], [18]))
+  statement 47: 5 (return([16], [17], [18]))
   statement 15: 3 (store_temp<core::panics::PanicResult::<((),)>>([12]) -> ([12]))
-  statement 37: 3 (store_temp<core::panics::PanicResult::<(core::felt252, ())>>([12]) -> ([12]))
+  statement 36: 3 (store_temp<core::panics::PanicResult::<(core::felt252, ())>>([12]) -> ([12]))
   statement 2: 1 (store_temp<RangeCheck>([0]) -> ([0]))
   statement 3: 1 (store_temp<GasBuiltin>([1]) -> ([1]))
   statement 4: 1 (store_temp<felt252>([2]) -> ([2]))
@@ -179,9 +179,9 @@ Weight by sierra statement:
   statement 13: 1 (store_temp<RangeCheck>([3]) -> ([3]))
   statement 14: 1 (store_temp<GasBuiltin>([8]) -> ([8]))
   statement 16: 1 (return([3], [8], [12]))
-  statement 35: 1 (store_temp<RangeCheck>([3]) -> ([3]))
-  statement 36: 1 (store_temp<GasBuiltin>([9]) -> ([9]))
-  statement 38: 1 (return([3], [9], [12]))
+  statement 34: 1 (store_temp<RangeCheck>([3]) -> ([3]))
+  statement 35: 1 (store_temp<GasBuiltin>([9]) -> ([9]))
+  statement 37: 1 (return([3], [9], [12]))
 Weight by concrete libfunc:
   libfunc withdraw_gas: 18
   libfunc store_temp<RangeCheck>: 14
```
