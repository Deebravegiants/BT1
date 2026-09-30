# [?] Avoid call to panic_with_byte_array in simple usage of panic! (#5958)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-07-07
Source: https://github.com/starkware-libs/cairo/commit/1af57c96ae39654ac4ba086c50c108c7c34e3d59
Type: security-commit

## Details
Avoid call to panic_with_byte_array in simple usage of panic! (#5958)

## Patch
### corelib/src/byte_array.cairo
```diff
@@ -14,7 +14,7 @@ use core::zeroable::NonZeroIntoImpl;
 /// A magic constant for identifying serialization of ByteArrays. An array of felt252s with this
 /// magic as one of the felt252s indicates that right after it you should expect a serialized
 /// ByteArray. This is currently used mainly for prints and panics.
-pub(crate) const BYTE_ARRAY_MAGIC: felt252 =
+pub const BYTE_ARRAY_MAGIC: felt252 =
     0x46a6158a16a947e5916b2a2ca68501a45e93d7110e81aa2d6438b1c57c879a3;
 const BYTES_IN_U128: usize = 16;
 const BYTES_IN_BYTES31_MINUS_ONE: usize = BYTES_IN_BYTES31 - 1;
```

### crates/cairo-lang-runner/src/profiling_test_data/circuit
```diff
@@ -35,35 +35,33 @@ eval_circuit
 
 //! > expected_profiling_info
 Weight by sierra statement:
-  statement 134: 22 (eval_circuit<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>([1], [2], [95], [93], [16], [96], [97]) { fallthrough([98], [99], [100]) 168([101], [102], [103], [104]) })
-  statement 26: 7 (add_circuit_input<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>([17], [26]) { fallthrough([27]) 114([28]) })
-  statement 126: 7 (add_circuit_input<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>([28], [92]) { fallthrough([93]) 214([94]) })
-  statement 11: 6 (try_into_circuit_modulus([15]) { fallthrough([16]) 300() })
-  statement 129: 5 (get_circuit_descriptor<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>() -> ([95]))
-  statement 136: 5 (get_circuit_output<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>, core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>>([100]) -> ([105], [106]))
-  statement 166: 5 (store_temp<core::panics::PanicResult::<(core::circuit::u384,)>>([117]) -> ([117]))
-  statement 10: 4 (store_temp<Tuple<BoundedInt<0, 79228162514264337593543950335>, BoundedInt<0, 79228162514264337593543950335>, BoundedInt<0, 79228162514264337593543950335>, BoundedInt<0, 79228162514264337593543950335>>>([15]) -> ([15]))
-  statement 24: 4 (store_temp<Tuple<U96Guarantee, U96Guarantee, U96Guarantee, U96Guarantee>>([26]) -> ([26]))
-  statement 125: 4 (store_temp<Tuple<U96Guarantee, U96Guarantee, U96Guarantee, U96Guarantee>>([92]) -> ([92]))
-  statement 23: 2 (store_temp<CircuitInputAccumulator<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>>([17]) -> ([17]))
-  statement 140: 2 (u96_limbs_less_than_guarantee_verify<4>([106]) { fallthrough([107]) 155([108]) })
-  statement 142: 2 (u96_limbs_less_than_guarantee_verify<3>([107]) { fallthrough([109]) 152([110]) })
-  statement 144: 2 (u96_limbs_less_than_guarantee_verify<2>([109]) { fallthrough([111]) 149([112]) })
-  statement 3: 1 (finalize_locals() -> ())
-  statement 25: 1 (store_local<RangeCheck96>([8], [7]) -> ([7]))
-  statement 132: 1 (store_temp<BoundedInt<0, 0>>([96]) -> ([96]))
-  statement 133: 1 (store_temp<BoundedInt<1, 1>>([97]) -> ([97]))
-  statement 138: 1 (store_temp<AddMod>([98]) -> ([98]))
-  statement 139: 1 (store_temp<MulMod>([99]) -> ([99]))
-  statement 147: 1 (store_temp<U96Guarantee>([113]) -> ([114]))
-  statement 148: 1 (jump() { 157() })
-  statement 158: 1 (u96_guarantee_verify([7], [114]) -> ([115]))
-  statement 161: 1 (store_temp<RangeCheck>([0]) -> ([0]))
-  statement 162: 1 (store_temp<AddMod>([98]) -> ([98]))
-  statement 163: 1 (store_temp<MulMod>([99]) -> ([99]))
-  statement 164: 1 (store_temp<RangeCheck96>([115]) -> ([115]))
-  statement 165: 1 (store_temp<GasBuiltin>([4]) -> ([4]))
-  statement 167: 1 (return([0], [98], [99], [115], [4], [117]))
+  statement 64: 22 (eval_circuit<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>([0], [1], [45], [43], [8], [46], [47]) { fallthrough([48], [49], [50]) 94([51], [52], [53], [54]) })
+  statement 21: 7 (add_circuit_input<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>([10], [19]) { fallthrough([20]) 46([21]) })
+  statement 57: 7 (add_circuit_input<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>([21], [42]) { fallthrough([43]) 136([44]) })
+  statement 6: 6 (try_into_circuit_modulus([7]) { fallthrough([8]) 163() })
+  statement 59: 5 (get_circuit_descriptor<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>() -> ([45]))
+  statement 66: 5 (get_circuit_output<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>, core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>>([50]) -> ([55], [56]))
+  statement 92: 5 (store_temp<core::panics::PanicResult::<(core::circuit::u384,)>>([67]) -> ([67]))
+  statement 5: 4 (store_temp<Tuple<BoundedInt<0, 79228162514264337593543950335>, BoundedInt<0, 79228162514264337593543950335>, BoundedInt<0, 79228162514264337593543950335>, BoundedInt<0, 79228162514264337593543950335>>>([7]) -> ([7]))
+  statement 19: 4 (store_temp<Tuple<U96Guarantee, U96Guarantee, U96Guarantee, U96Guarantee>>([19]) -> ([19]))
+  statement 56: 4 (store_temp<Tuple<U96Guarantee, U96Guarantee, U96Guarantee, U96Guarantee>>([42]) -> ([42]))
+  statement 18: 2 (store_temp<CircuitInputAccumulator<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>>([10]) -> ([10]))
+  statement 69: 2 (u96_limbs_less_than_guarantee_verify<4>([56]) { fallthrough([57]) 84([58]) })
+  statement 71: 2 (u96_limbs_less_than_guarantee_verify<3>([57]) { fallthrough([59]) 81([60]) })
+  statement 73: 2 (u96_limbs_less_than_guarantee_verify<2>([59]) { fallthrough([61]) 78([62]) })
+  statement 20: 1 (store_temp<RangeCheck96>([9]) -> ([9]))
+  statement 62: 1 (store_temp<BoundedInt<0, 0>>([46]) -> ([46]))
+  statement 63: 1 (store_temp<BoundedInt<1, 1>>([47]) -> ([47]))
+  statement 65: 1 (branch_align() -> ())
+  statement 67: 1 (store_temp<AddMod>([48]) -> ([48]))
+  statement 68: 1 (store_temp<MulMod>([49]) -> ([49]))
+  statement 76: 1 (store_temp<U96Guarantee>([63]) -> ([64]))
+  statement 77: 1 (jump() { 86() })
+  statement 86: 1 (u96_guarantee_verify([9], [64]) -> ([65]))
+  statement 89: 1 (store_temp<AddMod>([48]) -> ([48]))
+  statement 90: 1 (store_temp<MulMod>([49]) -> ([49]))
+  statement 91: 1 (store_temp<RangeCheck96>([65]) -> ([65]))
+  statement 93: 1 (return([48], [49], [65], [67]))
 Weight by concrete libfunc:
   libfunc eval_circuit<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>: 22
   libfunc add_circuit_input<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>: 14
@@ -76,49 +74,44 @@ Weight by concrete libfunc:
   libfunc store_temp<AddMod>: 2
   libfunc store_temp<CircuitInputAccumulator<Circuit<(core::circuit::MulModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::SubModGate::<core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>, core::circuit::CircuitInput::<1>>>, core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>, core::circuit::InverseGate::<core::circuit::AddModGate::<core::circuit::CircuitInput::<0>, core::circuit::CircuitInput::<1>>>)>>>: 2
   libfunc store_temp<MulMod>: 2
+  libfunc store_temp<RangeCheck96>: 2
   libfunc u96_limbs_less_than_guarantee_verify<2>: 2
   libfunc u96_limbs_less_than_guarantee_verify<3>: 2
   libfunc u96_limbs_less_than_guarantee_verify<4>: 2
-  libfunc finalize_locals: 1
+  libfunc branch_align: 1
   libfunc jump: 1
-  libfunc store_local<RangeCheck96>: 1
   libfunc store_temp<BoundedInt<0, 0>>: 1
   libfunc store_temp<BoundedInt<1, 1>>: 1
-  libfunc store_temp<GasBuiltin>: 1
-  libfunc store_temp<RangeCheck96>: 1
-  libfunc store_temp<RangeCheck>: 1
   libfunc store_temp<U96Guarantee>: 1
   libfunc u96_guarantee_verify: 1
   return: 1
 Weight by generic libfunc:
-  libfunc store_temp: 29
+  libfunc store_temp: 28
   libfunc eval_circuit: 22
   libfunc add_circuit_input: 14
   libfunc try_into_circuit_modulus: 6
   libfunc u96_limbs_less_than_guarantee_verify: 6
   libfunc get_circuit_descriptor: 5
   libfunc get_circuit_output: 5
-  libfunc finalize_locals: 1
+  libfunc branch_align: 1
   libfunc jump: 1
-  libfunc store_local: 1
   libfunc u96_guarantee_verify: 1
   return: 1
 Weight by user function (inc. generated):
-  function test::eval_circuit: 92
+  function test::eval_circuit: 90
 Weight by original user function (exc. generated):
-  function test::eval_circuit: 92
+  function test::eval_circuit: 90
 Weight by Cairo function:
   function core::circuit::AddInputResultImpl::next: 25
-  function core::circuit::EvalCircuitImpl::eval_ex: 24
-  function lib.cairo::eval_circuit: 11
+  function core::circuit::EvalCircuitImpl::eval_ex: 25
   function core::circuit::U384TryIntoCircuitModulus::try_into: 10
+  function lib.cairo::eval_circuit: 9
   function core::circuit::IntoU96GuaranteeImplByNext::into_u96_guarantee: 8
   function core::circuit::CircuitOutputsImpl::get_output: 5
   function core::circuit::EvalCircuitImpl::eval: 5
   function core::circuit::IntoU96GuaranteeImplFinal::into_u96_guarantee: 2
   function core::circuit::DestructU96Guarantee::destruct: 1
-  function unknown: 1
 Weight by Sierra stack trace:
-  test::eval_circuit: 92
+  test::eval_circuit: 90
 Weight by Cairo stack trace:
-  test::eval_circuit: 92
+  test::eval_circuit: 90
```

### crates/cairo-lang-semantic/src/expr/expansion_test_data/inline_macros
```diff
@@ -83,3 +83,88 @@ error: Type annotations needed. Failed to infer ?0.
  --> lib.cairo:2:1
 array![]
 ^******^
+
+//! > ==========================================================================
+
+//! > Test expansion of panic macro with no arguments
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: false)
+
+//! > expr_code
+panic!()
+
+//! > expanded_code
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0, 0)
+
+//! > diagnostics
+
+//! > ==========================================================================
+
+//! > Test expansion of panic macro with a simple short string
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: false)
+
+//! > expr_code
+panic!("0123456")
+
+//! > expanded_code
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0x30313233343536, 7)
+
+//! > diagnostics
+
+//! > ==========================================================================
+
+//! > Test expansion of panic macro with a 31 byte string.
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: false)
+
+//! > expr_code
+panic!("0123456789012345678901234567890")
+
+//! > expanded_code
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 1, 0x30313233343536373839303132333435363738393031323334353637383930, 0, 0)
+
+//! > diagnostics
+
+//! > ==========================================================================
+
+//! > Test expansion of panic macro with a simple 35 bytes string.
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: false)
+
+//! > expr_code
+panic!("01234567890123456789012345678901234")
+
+//! > expanded_code
+core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 1, 0x30313233343536373839303132333435363738393031323334353637383930, 0x31323334, 4)
+
+//! > diagnostics
+
+//! > ==========================================================================
+
+//! > Test expansion of panic macro with args
+
+//! > test_runner_name
+test_expand_expr(expect_diagnostics: true)
+
+//! > expr_code
+panic!("bad_format(})")
+
+//! > expanded_code
+{
+    let mut __formatter_for_panic_macro__: core::fmt::Formatter = core::traits::Default::default();
+    core::result::ResultTrait::<(), core::fmt::Error>::unwrap(
+write!(__formatter_for_panic_macro__, "bad_format(})")
+    );
+    core::panics::panic_with_byte_array(@__formatter_for_panic_macro__.buffer)
+}
+
+//! > diagnostics
+error: Plugin diagnostic: Closing `}` without a matching `{`.
+ --> lib.cairo:2:8
+panic!("bad_format(})")
+       ^*************^
```

### crates/cairo-lang-semantic/src/inline_macros/panic.rs
```diff
@@ -3,11 +3,73 @@ use cairo_lang_defs::plugin::{
     InlineMacroExprPlugin, InlinePluginResult, MacroPluginMetadata, NamedPlugin,
     PluginGeneratedFile,
 };
-use cairo_lang_defs::plugin_utils::unsupported_bracket_diagnostic;
-use cairo_lang_syntax::node::ast::WrappedArgList;
+use cairo_lang_defs::plugin_utils::{try_extract_unnamed_arg, unsupported_bracket_diagnostic};
+use cairo_lang_syntax::node::ast::{Arg, WrappedArgList};
 use cairo_lang_syntax::node::db::SyntaxGroup;
 use cairo_lang_syntax::node::{ast, TypedSyntaxNode};
 use indoc::formatdoc;
+use num_bigint::BigUint;
+
+use super::write::FELT252_BYTES;
+
+/// Try to generate a simple panic handlic code.
+/// Return true if successful and updates the buiilder if successful.
+fn try_handle_simple_panic(
+    db: &dyn SyntaxGroup,
+    builder: &mut PatchBuilder<'_>,
+    arguments: &[Arg],
+) -> bool {
+    let format_string_expr = match arguments {
+        [] => {
+            // Trivial panic!() with no arguments case.
+            builder.add_str(
+                "core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, 0, 0);",
+            );
+            return true;
+        }
+        [arg] => {
+            let Some(ast::Expr::String(format_string_expr)) = try_extract_unnamed_arg(db, arg)
+            else {
+                return false;
+            };
+            format_string_expr
+        }
+        // We have more than one argument, fallback to more generic handling.
+        _ => return false,
+    };
+
+    let Some(format_str) = format_string_expr.string_value(db) else {
+        return false;
+    };
+
+    if format_str.find(|c| c == '{' || c == '}').is_some() {
+        return false;
+    }
+
+    builder.add_str(&format!(
+        "core::panics::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, {}, ",
+        format_str.len() / FELT252_BYTES,
+    ));
+
+    for chunk in format_str.as_bytes().chunks(FELT252_BYTES) {
+        builder.add_str(&format!("{:#x}, ", BigUint::from_bytes_be(chunk)));
+    }
+
+    let remainder_size = format_str.len() % FELT252_BYTES;
+    if remainder_size == 0 {
+        // Adding the empty remainder word.
+        builder.add_str("0, ");
+    }
+    builder.add_str(&format!("{remainder_size}))"));
+
+    builder.add_str(&format!(
+        "core::panic(array![core::byte_array::BYTE_ARRAY_MAGIC, 0, '{}', {}",
+        format_str,
+        format_str.len()
+    ));
+
+    true
+}
 
 /// Macro for panicking with a format string.
 #[derive(Default, Debug)]
@@ -25,11 +87,10 @@ impl InlineMacroExprPlugin for PanicMacro {
         let WrappedArgList::ParenthesizedArgList(arguments_syntax) = syntax.arguments(db) else {
             return unsupported_bracket_diagnostic(db, syntax);
         };
+
         let mut builder = PatchBuilder::new(db, syntax);
         let arguments = arguments_syntax.arguments(db).elements(db);
-        if arguments.is_empty() {
-            builder.add_str(r#"core::panics::panic_with_byte_array(@"")"#);
-        } else {
+        if !try_handle_simple_panic(db, &mut builder, &arguments) {
             builder.add_modified(RewriteNode::interpolate_patched(
                 &formatdoc! {
                     r#"
```

### crates/cairo-lang-semantic/src/inline_macros/write.rs
```diff
@@ -13,6 +13,8 @@ use cairo_lang_utils::{try_extract_matches, OptionHelper};
 use indoc::indoc;
 use num_bigint::{BigInt, Sign};
 
+pub const FELT252_BYTES: usize = 31;
+
 /// Macro for writing into a formatter.
 #[derive(Debug, Default)]
 pub struct WriteMacro;
@@ -407,7 +409,6 @@ impl FormattingInfo {
         pending_chars: &mut String,
         ident_count: usize,
     ) {
-        const FELT252_BYTES: usize = 31;
         for chunk in pending_chars.as_bytes().chunks(FELT252_BYTES) {
             self.add_indentation(builder, ident_count);
             builder.add_modified(RewriteNode::interpolate_patched(
```
