# [?] [prover] Fix 3 unsoundness bugs in Boogie encoding (#20603)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-09-27
Source: https://github.com/aptos-labs/aptos-core/commit/ec1e75bb095640a47c061c15ac5c45c96dafb50f
Type: security-commit

## Details
[prover] Fix 3 unsoundness bugs in Boogie encoding (#20603)

Three independent defects in the Boogie encoding, each of which let the prover
report success for a specification that is false of the real program.

1. The merged enum `$Update` dispatcher closed its `if s is <variant>` chain
   with `else s`, so updating a field the dispatched variant does not carry
   was encoded as the identity and `result == update_field(e, f, v)` could be
   discharged against a body that wrote nothing. The chain now ends in an
   uninterpreted `$Arbitrary_update` companion taking the receiver and the new
   value, matching how every sibling emitter already fails closed. When the
   chain covers every variant the `else` is unreachable, so the last variant
   becomes the bare `else` and no companion is declared; this is the common
   case, and the wrapper is `{:inline}`, so a dead companion would otherwise
   be inlined into every field update.

2. A global borrow was rooted at `$Global(a)`, carrying the address alone, so
   `&mut A[addr].x` and `&mut B[addr].x` had the same location and path and a
   write through one updated both memories (#20592). `$Global` gains a
   resource-type component, a `unique` identity constant per resource-type
   memory. The guarantee holds while distinct resource types render to
   distinct Boogie names; name-colliding pairs still share one memory, exactly
   as on main, and are addressed by the name-injectivity change stacked on
   this one.

3. `Bytecode::modifies` reported the `&mut` arguments of a direct call but not
   of a call through a function value: `Invoke` fell through to the generic
   `Call` arm, which inspects only `dests`, so the referenced value was not
   havoced at the loop head (#20591). `Invoke` now shares the `Function` arm.
   The function operand is never reference-typed, so results stay precise.

Each fix has a regression test under tests/sources/regression/ shown to fail
without it: enum_update_out_of_variant, borrow_global_distinct_types,
loop_invoke_mut_ref.

Tested: move-prover testsuite 390 passed (functional/choice.move is a known
flake); all four aptos-framework prover suites pass with 0 prover errors;
clippy under the xclippy flag set and nightly fmt are clean.

Co-authored-by: Claude Opus 5.5 (1M context) <noreply@anthropic.com>

## Patch
### third_party/move/move-model/bytecode/src/stackless_bytecode.rs
```diff
@@ -976,7 +976,11 @@ impl Bytecode {
                 // write-ref only distorts the value of the reference, but not the pointer itself
                 (add_abort(vec![], aa), vec![(srcs[0], false)])
             },
-            Call(_, dests, Function(..), srcs, aa) => {
+            // `Invoke` shares this arm rather than falling through to the generic `Call`
+            // arm below, which reports only `dests`: a call through a function value
+            // distorts the values behind its `&mut` arguments exactly as a direct call
+            // does. See `regression/loop_invoke_mut_ref.move`.
+            Call(_, dests, Function(..) | Invoke, srcs, aa) => {
                 let mut val_targets = vec![];
                 let mut mut_targets = vec![];
                 for src in srcs {
```

### third_party/move/move-prover/boogie-backend/src/boogie_helpers.rs
```diff
@@ -169,16 +169,20 @@ pub fn boogie_variant_field_update(
     inst: &[Type],
 ) -> String {
     let struct_env = &field_env.struct_env;
-    let suffix = boogie_type_suffix_for_struct(struct_env, inst, false);
     format!(
         "$Update'{}'_{}_{}",
-        suffix,
-        // remove parentheses and spaces from field type name
-        field_type_name.replace(['(', ')'], "").replace(' ', "_"),
+        boogie_type_suffix_for_struct(struct_env, inst, false),
+        boogie_field_type_name_component(&field_type_name),
         field_env.get_name().display(struct_env.symbol_pool()),
     )
 }
 
+/// Mangles a rendered field type into a Boogie name component. Shared by the enum `$Update`
+/// wrapper's emitter and `boogie_variant_field_update`, whose names must match.
+pub fn boogie_field_type_name_component(field_type_name: &str) -> String {
+    field_type_name.replace(['(', ')'], "").replace(' ', "_")
+}
+
 /// Return whether the field renders as a bitvector. `ty` is the field's
 /// (instantiated) type; signed-containing types never render as bitvectors.
 pub fn field_bv_flag_global_state(
@@ -344,6 +348,13 @@ pub fn boogie_resource_memory_name(
     )
 }
 
+/// Creates the name of the unique identity constant for a resource type's memory, given
+/// that memory's name (see `boogie_resource_memory_name`). The constant is the `t`
+/// component of a `$Global` location -- see `$Location` in prelude.bpl.
+pub fn boogie_resource_memory_id_name(memory_name: &str) -> String {
+    format!("{}_$id", memory_name)
+}
+
 /// Creates a string for a memory label.
 fn boogie_memory_label(memory_label: &Option<MemoryLabel>) -> String {
     if let Some(l) = memory_label {
```

### third_party/move/move-prover/boogie-backend/src/bytecode_translator.rs
```diff
@@ -12,18 +12,20 @@ use crate::{
         boogie_behavioral_fun_spec_name, boogie_behavioral_result_fun_name,
         boogie_behavioral_spec_fun_name, boogie_byte_blob, boogie_closure_pack_name,
         boogie_constant_blob, boogie_debug_track_abort, boogie_debug_track_local,
-        boogie_debug_track_return, boogie_equality_for_type, boogie_field_sel, boogie_field_update,
-        boogie_fun_apply_name, boogie_fun_param_name, boogie_function_name, boogie_int_suffix,
+        boogie_debug_track_return, boogie_equality_for_type, boogie_field_sel,
+        boogie_field_type_name_component, boogie_field_update, boogie_fun_apply_name,
+        boogie_fun_param_name, boogie_function_name, boogie_int_suffix,
         boogie_make_vec_from_strings, boogie_modifies_memory_name, boogie_native_fun_has_spec_fun,
         boogie_native_spec_fun_name, boogie_num_literal, boogie_num_type_base,
-        boogie_reflection_type_info, boogie_reflection_type_name, boogie_resource_memory_name,
-        boogie_spec_fun_name, boogie_struct_field_name, boogie_struct_field_result_fun_name,
-        boogie_struct_field_spec_fun_name, boogie_struct_name, boogie_struct_variant_name,
-        boogie_temp, boogie_temp_from_suffix, boogie_type, boogie_type_for_struct_field,
-        boogie_type_param, boogie_type_suffix, boogie_type_suffix_for_struct,
-        boogie_type_suffix_for_struct_variant, boogie_variant_field_update,
-        boogie_well_formed_check, boogie_well_formed_expr, bv_flag_for_type,
-        compute_evaluator_memory_union, field_bv_flag_global_state, TypeIdentToken,
+        boogie_reflection_type_info, boogie_reflection_type_name, boogie_resource_memory_id_name,
+        boogie_resource_memory_name, boogie_spec_fun_name, boogie_struct_field_name,
+        boogie_struct_field_result_fun_name, boogie_struct_field_spec_fun_name, boogie_struct_name,
+        boogie_struct_variant_name, boogie_temp, boogie_temp_from_suffix, boogie_type,
+        boogie_type_for_struct_field, boogie_type_param, boogie_type_suffix,
+        boogie_type_suffix_for_struct, boogie_type_suffix_for_struct_variant,
+        boogie_variant_field_update, boogie_well_formed_check, boogie_well_formed_expr,
+        bv_flag_for_type, compute_evaluator_memory_union, field_bv_flag_global_state,
+        TypeIdentToken,
     },
     options::BoogieOptions,
     spec_translator::{LabelInfo, SpecTranslator},
@@ -5345,35 +5347,54 @@ impl StructTranslator<'_> {
                 &mut field_variant_map,
             );
         }
+        let num_variants = struct_env.get_variants().count();
         for ((field, (field_type, field_type_uninst)), variant_name) in field_variant_map {
-            self.emit_function(
-                &format!(
-                    "$Update'{}'_{}_{}(s: {}, x: {}): {}",
-                    struct_name,
-                    // type name is needed in the update function name
-                    // to distinguish fields with the same name but different types in different variants
-                    // remove parentheses and spaces from field type name
-                    field_type_uninst.replace(['(', ')'], "").replace(' ', "_"),
-                    field,
-                    struct_name,
-                    field_type,
-                    struct_name
-                ),
-                || {
-                    let mut else_symbol = "";
-                    for struct_variant_name in &variant_name {
-                        let match_condition = format!("s is {}", struct_variant_name);
-                        let update_str =
-                            format!("$Update'{}'_{}(s, x)", struct_variant_name, field);
-                        emitln!(writer, "{} if {} then", else_symbol, match_condition);
-                        emitln!(writer, "{}", update_str);
-                        if else_symbol.is_empty() {
-                            else_symbol = "else";
-                        }
-                    }
-                    emitln!(writer, "else s");
-                },
+            // The field type is part of the name so that same-named fields of different
+            // types in different variants stay apart; `boogie_variant_field_update`
+            // renders it the same way caller-side.
+            let name_suffix = format!(
+                "'{}'_{}_{}",
+                struct_name,
+                boogie_field_type_name_component(&field_type_uninst),
+                field
             );
+            let signature = format!("(s: {}, x: {}): {}", struct_name, field_type, struct_name);
+            // A receiver outside `variant_name` lacks the field, so updating it yields an
+            // unspecified value (`$Arbitrary_update`), never `s` unchanged. If every
+            // constructor is covered the last one becomes the bare `else`: no companion,
+            // so no unconstrained term is inlined into every update of this field.
+            let covers_all_variants = variant_name.len() == num_variants;
+            let (guarded, closing) = match variant_name.split_last() {
+                Some((last, rest)) if covers_all_variants => {
+                    (rest, format!("$Update'{}'_{}(s, x)", last, field))
+                },
+                Some(_) | None => (
+                    &variant_name[..],
+                    format!("$Arbitrary_update{}(s, x)", name_suffix),
+                ),
+            };
+            if !covers_all_variants {
+                emitln!(
+                    writer,
+                    "function $Arbitrary_update{}{};",
+                    name_suffix,
+                    signature
+                );
+            }
+            self.emit_function(&format!("$Update{}{}", name_suffix, signature), || {
+                for (i, struct_variant_name) in guarded.iter().enumerate() {
+                    let else_symbol = if i == 0 { "" } else { "else" };
+                    emitln!(
+                        writer,
+                        "{} if s is {} then",
+                        else_symbol,
+                        struct_variant_name
+                    );
+                    emitln!(writer, "$Update'{}'_{}(s, x)", struct_variant_name, field);
+                }
+                let else_symbol = if guarded.is_empty() { "" } else { "else " };
+                emitln!(writer, "{}{}", else_symbol, closing);
+            });
         }
 
         self.emit_is_valid_struct(struct_env, struct_name);
@@ -5756,15 +5777,15 @@ impl StructTranslator<'_> {
         }
 
         if struct_env.has_memory() {
-            // Emit memory variable.
-            let memory_name = boogie_resource_memory_name(
-                env,
-                &struct_env
-                    .get_qualified_id()
-                    .instantiate(self.type_inst.to_owned()),
-                &None,
-            );
+            // Emit memory variable, and the identity constant naming it (the `t` of
+            // `$Global`); `unique` gives pairwise distinctness across resource types.
+            let memory_name = boogie_resource_memory_name(env, &qid, &None);
             emitln!(writer, "var {}: $Memory {};", memory_name, struct_name);
+            emitln!(
+                writer,
+                "const unique {}: int;",
+                boogie_resource_memory_id_name(&memory_name)
+            );
         }
 
         // Emit compare function and procedure
@@ -7386,19 +7407,19 @@ impl FunctionTranslator<'_> {
                         let inst = self.inst_slice(inst);
                         let addr_str = str_local(srcs[0]);
                         let dest_str = str_local(dests[0]);
-                        let memory = boogie_resource_memory_name(
-                            env,
-                            &mid.qualified_inst(*sid, inst),
-                            &None,
-                        );
+                        let mem_qid = mid.qualified_inst(*sid, inst);
+                        let memory = boogie_resource_memory_name(env, &mem_qid, &None);
+                        let memory_id = boogie_resource_memory_id_name(&memory);
                         emitln!(writer, "if (!$ResourceExists({}, {})) {{", memory, addr_str);
                         writer.with_indent(|| emitln!(writer, "call $ExecFailureAbort();"));
                         emitln!(writer, "} else {");
                         writer.with_indent(|| {
                             emitln!(
                                 writer,
-                                "{} := $Mutation($Global({}), EmptyVec(), $ResourceValue({}, {}));",
+                                "{} := $Mutation($Global({}, {}), EmptyVec(), \
+                                 $ResourceValue({}, {}));",
                                 dest_str,
+                                memory_id,
                                 addr_str,
                                 memory,
                                 addr_str
@@ -8204,6 +8225,9 @@ impl FunctionTranslator<'_> {
             },
             GlobalRoot(memory) => {
                 assert!(matches!(edge, BorrowEdge::Direct));
+                // `t` is not re-checked: the typed `$Memory`/`$Mutation` pairing already
+                // pins the resource type, provided distinct resource types render to
+                // distinct Boogie names.
                 let memory = &memory.to_owned().instantiate(self.type_inst);
                 let memory_name = boogie_resource_memory_name(env, memory, &None);
                 emitln!(
```

### third_party/move/move-prover/boogie-backend/src/prelude/prelude.bpl
```diff
@@ -465,9 +465,12 @@ function {:inline} $IsEqual'bool'(x: bool, y: bool): bool {
 // Memory
 
 datatype $Location {
-    // A global resource location within the statically known resource type's memory,
-    // where `a` is an address.
-    $Global(a: int),
+    // A global resource location, where `t` is the identity of the resource type's
+    // memory and `a` is an address. `t` is part of the location because an address
+    // alone is unique only within one resource type: without it, `&mut A[addr].f` and
+    // `&mut B[addr].f` share one identity, and `$IsSameMutation`/`$IsParentMutation`
+    // would let a write-back through one update the other.
+    $Global(t: int, a: int),
     // A local location. `i` is the unique index of the local.
     $Local(i: int),
     // The location of a reference outside of the verification scope, for example, a `&mut` parameter
```

### third_party/move/move-prover/tests/sources/functional/closures/lambda_captured_fun_loop.exp
```diff
@@ -33,7 +33,8 @@ error: post-condition does not hold
    =     at tests/sources/functional/closures/lambda_captured_fun_loop.move:23: wrap2
    =         i = <redacted>
    =     at tests/sources/functional/closures/lambda_captured_fun_loop.move:24: wrap2
-   =     enter loop, variable(s) i havocked and reassigned
+   =     enter loop, variable(s) v, i havocked and reassigned
+   =         v = <redacted>
    =         i = <redacted>
    =     at tests/sources/functional/closures/lambda_captured_fun_loop.move:24: wrap2
    =     at tests/sources/functional/closures/lambda_captured_fun_loop.move:22: wrap2
```

### third_party/move/move-prover/tests/sources/regression/borrow_global_distinct_types.exp
```diff
@@ -0,0 +1,23 @@
+Move prover returns: exiting with verification errors
+error: post-condition does not hold
+   ┌─ tests/sources/regression/borrow_global_distinct_types.move:43:9
+   │
+43 │         ensures result == 0; // error: the field returned was never written
+   │         ^^^^^^^^^^^^^^^^^^^^
+   │
+   =     at tests/sources/regression/borrow_global_distinct_types.move:33: write_zero_and_return_other
+   =     at tests/sources/regression/borrow_global_distinct_types.move:42: write_zero_and_return_other (spec)
+   =     at tests/sources/regression/borrow_global_distinct_types.move:33: write_zero_and_return_other
+   =         choose_a = <redacted>
+   =         addr = <redacted>
+   =     at tests/sources/regression/borrow_global_distinct_types.move:34: write_zero_and_return_other
+   =         a = <redacted>
+   =     at tests/sources/regression/borrow_global_distinct_types.move:35: write_zero_and_return_other
+   =         b = <redacted>
+   =     at tests/sources/regression/borrow_global_distinct_types.move:36: write_zero_and_return_other
+   =         selected = <redacted>
+   =     at tests/sources/regression/borrow_global_distinct_types.move:37: write_zero_and_return_other
+   =     at tests/sources/regression/borrow_global_distinct_types.move:38: write_zero_and_return_other
+   =     at tests/sources/regression/borrow_global_distinct_types.move:33: write_zero_and_return_other
+   =         result = <redacted>
+   =     at tests/sources/regression/borrow_global_distinct_types.move:43: write_zero_and_return_other (spec)
```

### third_party/move/move-prover/tests/sources/regression/borrow_global_distinct_types.move
```diff
@@ -0,0 +1,60 @@
+// Copyright © Aptos Foundation
+// SPDX-License-Identifier: Apache-2.0
+
+// Two `&mut` references into global storage must not alias when they point into
+// different resource types at the same address.
+//
+// The root of a global borrow is a `$Location`, which used to carry the address and
+// nothing else. A field borrow appends only the field offset to the path, so
+// `&mut A[addr].x` and `&mut B[addr].x` produced the same location and the same path.
+// `$IsSameMutation` and `$IsParentMutation` decide on the location and the path alone,
+// so the two counted as one reference: when the write through either was written back,
+// the prover updated both memories and the field of the resource that was never
+// written also looked changed.
+//
+// Move keeps resources apart by type as well as by address, so `$Global` now carries
+// the identity of the resource type's memory next to the address. Each resource type's
+// memory gets a `unique` identity constant, which gives pairwise distinctness across
+// all resource types.
+
+module 0x42::borrow_global_distinct_types {
+
+    struct A has key {
+        x: u64
+    }
+
+    struct B has key {
+        x: u64
+    }
+
+    /// Writes zero through one resource and reads the field of the other, so the
+    /// value returned was never written. With `A.x = 1` and `B.x = 2` this returns 2
+    /// when `choose_a` holds and 1 otherwise, so it is never 0.
+    public fun write_zero_and_return_other(choose_a: bool, addr: address): u64 {
+        let a = &mut A[addr].x;
+        let b = &mut B[addr].x;
+        let selected = if (choose_a) a else b;
+        *selected = 0;
+        if (choose_a) B[addr].x else A[addr].x
+    }
+
+    spec write_zero_and_return_other {
+        requires exists<A>(addr) && exists<B>(addr);
+        ensures result == 0; // error: the field returned was never written
+    }
+
+    /// Reads back the field that really was written. This must verify: separating the
+    /// two roots must not cost the legitimate write-back.
+    public fun write_zero_and_return_same(choose_a: bool, addr: address): u64 {
+        let a = &mut A[addr].x;
+        let b = &mut B[addr].x;
+        let selected = if (choose_a) a else b;
+        *selected = 0;
+        if (choose_a) A[addr].x else B[addr].x
+    }
+
+    spec write_zero_and_return_same {
+        requires exists<A>(addr) && exists<B>(addr);
+        ensures result == 0;
+    }
+}
```

### third_party/move/move-prover/tests/sources/regression/enum_update_out_of_variant.exp
```diff
@@ -0,0 +1,15 @@
+Move prover returns: exiting with verification errors
+error: post-condition does not hold
+   ┌─ tests/sources/regression/enum_update_out_of_variant.move:29:9
+   │
+29 │         ensures result == update_field(e, f, _v); // error: unspecified for a C receiver
+   │         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
+   │
+   =     at tests/sources/regression/enum_update_out_of_variant.move:24: set_f_unchanged
+   =     at tests/sources/regression/enum_update_out_of_variant.move:28: set_f_unchanged (spec)
+   =     at tests/sources/regression/enum_update_out_of_variant.move:24: set_f_unchanged
+   =         e = <redacted>
+   =         _v = <redacted>
+   =     at tests/sources/regression/enum_update_out_of_variant.move:25: set_f_unchanged
+   =         result = <redacted>
+   =     at tests/sources/regression/enum_update_out_of_variant.move:29: set_f_unchanged (spec)
```

### third_party/move/move-prover/tests/sources/regression/enum_update_out_of_variant.move
```diff
@@ -0,0 +1,45 @@
+// Copyright © Aptos Foundation
+// SPDX-License-Identifier: Apache-2.0
+
+// Updating a field on an enum receiver whose variant does not declare that field
+// must not be provably a no-op.
+//
+// `update_field(s, f, v)` is a user-facing spec builtin that accepts enum receivers,
+// and for an enum field the backend emits a merged `$Update` wrapper that dispatches
+// on the receiver's constructor. That dispatch chain used to close with `else s`, so
+// a receiver outside the wrapper's variant set was returned unchanged. The encoding
+// therefore claimed that updating a field the dispatched variant does not carry is
+// the identity, which let the prover discharge `result == update_field(e, f, v)`
+// against a body that never wrote anything.
+//
+// The chain now closes with an uninterpreted value, so such a receiver is
+// unspecified rather than unchanged.
+
+module 0x42::enum_update_out_of_variant {
+
+    enum E has copy, drop { A { f: u64 }, C { g: bool } }
+
+    /// `update_field(e, f, _v)` type-checks on a `C` receiver even though `C` carries
+    /// no field `f`. Returning `e` unchanged must not satisfy it.
+    public fun set_f_unchanged(e: E, _v: u64): E {
+        e
+    }
+    spec set_f_unchanged {
+        requires e is C;
+        ensures result == update_field(e, f, _v); // error: unspecified for a C receiver
+    }
+
+    /// Positive control on a receiver the wrapper does cover: the dispatch must stay
+    /// precise there, i.e. an `A` receiver must not be routed to the unspecified arm.
+    /// This has to verify.
+    public fun set_f_covered(e: E, v: u64): E {
+        if (e is A) {
+            e.f = v
+        };
+        e
+    }
+    spec set_f_covered {
+        requires e is A;
+        ensures result == update_field(e, f, v);
+    }
+}
```

### third_party/move/move-prover/tests/sources/regression/loop_invoke_mut_ref.exp
```diff
@@ -0,0 +1,46 @@
+Move prover returns: exiting with verification errors
+error: post-condition does not hold
+   ┌─ tests/sources/regression/loop_invoke_mut_ref.move:42:9
+   │
+42 │         ensures result == 0; // error: the loop body writes 1 through `x`
+   │         ^^^^^^^^^^^^^^^^^^^^
+   │
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:30: apply_in_loop
+   =         x = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:31: apply_in_loop
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:32: apply_in_loop
+   =         f = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:33: apply_in_loop
+   =         <redacted> = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:34: apply_in_loop
+   =     enter loop, variable(s) x, $t2 havocked and reassigned
+   =         x = <redacted>
+   =         <redacted> = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:38: apply_in_loop
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:30: apply_in_loop
+   =         result = <redacted>
+   =         x = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:42: apply_in_loop (spec)
+
+error: post-condition does not hold
+   ┌─ tests/sources/regression/loop_invoke_mut_ref.move:57:9
+   │
+57 │         ensures result == 0; // error: the loop body writes 2 through `x`
+   │         ^^^^^^^^^^^^^^^^^^^^
+   │
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:45: invoke_with_destination_in_loop
+   =         x = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:46: invoke_with_destination_in_loop
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:47: invoke_with_destination_in_loop
+   =         f = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:48: invoke_with_destination_in_loop
+   =         <redacted> = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:49: invoke_with_destination_in_loop
+   =     enter loop, variable(s) x, $t2 havocked and reassigned
+   =         x = <redacted>
+   =         <redacted> = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:53: invoke_with_destination_in_loop
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:45: invoke_with_destination_in_loop
+   =         result = <redacted>
+   =         x = <redacted>
+   =     at tests/sources/regression/loop_invoke_mut_ref.move:57: invoke_with_destination_in_loop (spec)
```

### third_party/move/move-prover/tests/sources/regression/loop_invoke_mut_ref.move
```diff
@@ -0,0 +1,71 @@
+// Copyright © Aptos Foundation
+// SPDX-License-Identifier: Apache-2.0
+
+// A loop must forget any value its body can change, including the value behind a
+// `&mut` argument passed to a call through a function value.
+//
+// The loop analysis asks each instruction what it modifies. A direct call reports
+// its `&mut` arguments as well as its results, but a call through a function value
+// used to report only the explicit results. The value behind the reference was
+// therefore not havoced at the loop head, and the prover kept the value it had
+// before the loop. The backend already emits the implicit `x := f(x)` return for a
+// `&mut` argument of such a call, so only the modification query was out of step.
+//
+// `apply_in_loop` writes 0 through `x`, then calls `set_one` through a function value
+// inside a loop, which writes 1, so `result == 0` must be rejected.
+// `invoke_with_destination_in_loop` is the same with a call that also returns a value,
+// which pins that the `&mut` arguments are reported even when `dests` is non-empty.
+
+module 0x42::loop_invoke_mut_ref {
+
+    fun set_one(x: &mut u64) {
+        *x = 1;
+    }
+
+    fun set_two_and_return(x: &mut u64): u64 {
+        *x = 2;
+        7
+    }
+
+    public fun apply_in_loop(x: &mut u64): u64 {
+        *x = 0;
+        let f: |&mut u64| has copy + drop = set_one;
+        let i = 0;
+        while (i < 1) {
+            f(x);
+            i += 1;
+        };
+        *x
+    }
+
+    spec apply_in_loop {
+        ensures result == 0; // error: the loop body writes 1 through `x`
+    }
+
+    public fun invoke_with_destination_in_loop(x: &mut u64): u64 {
+        *x = 0;
+        let f: |&mut u64| u64 has copy + drop = set_two_and_return;
+        let i = 0;
+        while (i < 1) {
+            let _call_result = f(x);
+            i += 1;
+        };
+        *x
+    }
+
+    spec invoke_with_destination_in_loop {
+        ensures result == 0; // error: the loop body writes 2 through `x`
+    }
+
+    /// Control, outside any loop: the return value of a call through a function value
+    /// must still be handled precisely, so this has to keep verifying. It pins that
+    /// the fix reports the `&mut` arguments without over-havocking the results.
+    public fun invoke_with_destination_control(x: &mut u64): u64 {
+        let f: |&mut u64| u64 has copy + drop = set_two_and_return;
+        f(x)
+    }
+
+    spec invoke_with_destination_control {
+        ensures result == 7;
+    }
+}
```
