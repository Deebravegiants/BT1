# [?] [prover] fix unsound result_of/write_of axioms on &mut (#19767)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-05-15
Source: https://github.com/aptos-labs/aptos-core/commit/760099358b4e85b2a4c61f528e67b15887f755de
Type: security-commit

## Details
[prover] fix unsound result_of/write_of axioms on &mut (#19767)

## Description

Fixes a soundness bug in the Move Prover's `result_of` / `write_of_j` axiom emission for function values with both a declared return and at least one `&mut` parameter.

### Original codex finding

> Medium: Unsound Move Prover axiom for result_of with &mut. For function values with at least one mutable-reference parameter and a declared return value, the new backend makes the hidden &mut post-state slots q0..qN inputs to the generated result_of evaluator. It then emits a universal axiom stating that ensures_of holds for every such post-state q when paired with result_of(..., q). The same code also emits write_of functionality axioms saying that whenever ensures_of holds, each post-state q_j must equal a fixed write_of_j value determined only by the inputs. Combined, these axioms imply that every possible q_j equals the same fixed write_of_j value. For normal inhabited types such as u64, this is contradictory and can make the Boogie verification context inconsistent. In an inconsistent context, the prover may verify arbitrary false postconditions or invariants. This is limited to Move Prover/developer verification tooling and is not directly reachable from validator or fullnode runtime inputs.

### Fix

Align the per-type evaluator with the per-function Skolem path: `result_of` is now a single tuple-returning Skolem keyed only on inputs, returning `Tuple<declared..., post_states...>`. `BehaviorKind::ResultOf` and `BehaviorKind::WriteOf(j)` share this symbol — callers project the declared-result slice or the j-th post-state slot. The unsound pairing of a universal-over-q axiom with per-mutref functionality axioms is gone; one sound axiom ties the Skolem to `ensures_of` by splatting its tuple components into the corresponding `ensures_of` slots.

Concretely:
- `boogie_behavioral_eval_fun_name` normalizes `ResultOf` and `WriteOf(j)` to the same Boogie symbol.
- `generate_result_of_function_and_axiom` emits the tuple Skolem and a single `forall mem, f, p_*` axiom; the per-mutref `write_of_j` function and functionality axiom emission is removed.
- `translate_behavior_via_evaluator` adds tuple-projection wrapping for `ResultOf` (single index or truncate) and `WriteOf(j)` (single index), mirroring the existing closure-direct path.

## How Has This Been Tested?

- Full `move-prover` suite (232 tests, including new regression `result_of_mut_ref_soundness.move` under `tests/sources/functional/closures/`).
- Inference suite (24 tests) — exercises spec inference paths that construct `WriteOf(j)` carriers.
- aptos-framework prover suite (`move_stdlib_prover_tests`, `move_token_prover_tests`, `move_aptos_stdlib_prover_tests`, `move_framework_prover_tests`).
- Clippy / fmt / machete clean.
- Zero existing `.exp` baselines changed.

## Key Areas to Review

- `bytecode_translator.rs::generate_result_of_function_and_axiom` — the new tuple Skolem and single connecting axiom. Compare to the existing per-function Skolem path in the same file, which this now mirrors.
- `spec_translator.rs::translate_behavior_via_evaluator` — projection wrapping for `ResultOf` / `WriteOf(j)`; the post-state-clone skip for `ResultOf` parallels the closure-direct path's existing handling.
- `boogie_helpers.rs::boogie_behavioral_eval_fun_name` — symbol normalization that makes `ResultOf` and `WriteOf(j)` resolve to the same Skolem.

## Type of Change
- [x] Bug fix

## Which Components or Systems Does This Change Impact?
- [x] Other (specify): Move Prover (developer verification tooling)

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

### third_party/move/move-prover/boogie-backend/src/boogie_helpers.rs
```diff
@@ -1354,12 +1354,27 @@ pub fn boogie_struct_field_result_fun_name(
 /// Return name of the behavioral predicate evaluation function for a function type.
 /// These inline functions dispatch on closure variants to evaluate behavioral predicates.
 /// Format: `${kind}'${type_suffix}'`
+///
+/// `ResultOf` and `WriteOf(j)` share a single tuple-returning Skolem symbol:
+/// the Skolem returns `Tuple<declared..., post_states...>` and callers project
+/// the appropriate slice. Sharing the symbol is what keeps `ensures_of` and
+/// `result_of` mutually consistent — the alternative (separate `write_of_j`
+/// Skolems pinned by a functionality axiom) is unsound when combined with a
+/// universal axiom over post-state inputs.
 pub fn boogie_behavioral_eval_fun_name(
     env: &GlobalEnv,
     fun_type: &Type,
     kind: BehaviorKind,
 ) -> String {
-    format!("${}'{}'", kind, boogie_type_suffix(env, fun_type, false))
+    let kind_name = match kind {
+        BehaviorKind::ResultOf | BehaviorKind::WriteOf(_) => "result_of".to_string(),
+        _ => kind.to_string(),
+    };
+    format!(
+        "${}'{}'",
+        kind_name,
+        boogie_type_suffix(env, fun_type, false)
+    )
 }
 
 /// Return name of a per-function behavioral spec function for a closure target function.
```

### third_party/move/move-prover/boogie-backend/src/bytecode_translator.rs
```diff
@@ -2053,14 +2053,27 @@ impl<'env> BoogieTranslator<'env> {
 
     /// Generate the uninterpreted `result_of` function and its connecting axiom.
     ///
-    /// The Skolem takes `(memory, fun, params, &mut post-state slots)` as
-    /// inputs and returns the declared return type only. The axiom ties it
-    /// to `ensures_of` by splatting the Skolem output into the result slots:
+    /// The Skolem takes only `(memory, fun, params)` and returns a tuple
+    /// `(declared_results..., &mut post-states...)`. `BehaviorKind::ResultOf`
+    /// and `BehaviorKind::WriteOf(j)` share this symbol — callers project the
+    /// declared-result slice or the j-th post-state slot, respectively. The
+    /// axiom ties it to `ensures_of` by splatting the Skolem's tuple
+    /// components into the corresponding `ensures_of` slots:
     ///
     /// ```text
-    /// axiom forall mem, f, p_*, q_* ::
-    ///     ensures_of(mem, f, p_*, result_of(mem, f, p_*, q_*), q_*)
+    /// axiom forall mem, f, p_* ::
+    ///     (var _r := result_of(mem, f, p_*);
+    ///      ensures_of(mem, f, p_*, _r->$0, ..., _r->$<N+K-1>))
     /// ```
+    ///
+    /// Earlier versions of this generator made the `&mut` post-state slots
+    /// `q_*` *inputs* to `result_of` and universally quantified the axiom over
+    /// them, plus emitted separate `write_of_j` Skolems with functionality
+    /// axioms saying `ensures_of(..., q_*) ==> q_j == write_of_j(inputs)`. The
+    /// two together implied `forall q_j: q_j == write_of_j(inputs)`, which is
+    /// inconsistent for inhabited types. Using a single tuple Skolem keyed on
+    /// inputs alone — matching the per-function Skolem path — eliminates that
+    /// inconsistency at the source.
     fn generate_result_of_function_and_axiom(
         &self,
         fun_type: &Type,
@@ -2080,7 +2093,8 @@ impl<'env> BoogieTranslator<'env> {
             .collect();
         let post_state_types = Self::behavioral_post_state_types(&params_flat);
 
-        if declared_results.is_empty() {
+        // Nothing to Skolemize when there are no observable outputs.
+        if declared_results.is_empty() && post_state_types.is_empty() {
             return;
         }
 
@@ -2096,7 +2110,7 @@ impl<'env> BoogieTranslator<'env> {
         let ensures_of_name =
             boogie_behavioral_eval_fun_name(env, fun_type, BehaviorKind::EnsuresOf);
 
-        // Inputs: memory, fun, p0..pN, q0..qK (post-state slots).
+        // Inputs: memory, fun, p0..pN. No post-state inputs.
         let mut param_decls: Vec<String> = eval_mem_decls;
         param_decls.push(format!("f: {}", fun_ty_boogie_name));
         let mut input_args: Vec<String> = eval_mem_args;
@@ -2109,21 +2123,18 @@ impl<'env> BoogieTranslator<'env> {
             ));
             input_args.push(format!("p{}", pos));
         }
-        let mut post_args: Vec<String> = Vec::with_capacity(post_state_types.len());
-        for (pos, ty) in post_state_types.iter().enumerate() {
-            param_decls.push(format!("q{}: {}", pos, boogie_type(env, ty, false)));
-            post_args.push(format!("q{}", pos));
-        }
-        let all_call_args = {
-            let mut v = input_args.clone();
-            v.extend(post_args.iter().cloned());
-            v
-        };
 
-        let result_type = if declared_results.len() == 1 {
-            boogie_type(env, &declared_results[0], false)
+        // Output tuple: declared results followed by `&mut` post-states.
+        // References are stripped — spec predicates work on values.
+        let output_types: Vec<Type> = declared_results
+            .iter()
+            .chain(post_state_types.iter())
+            .cloned()
+            .collect();
+        let result_type = if output_types.len() == 1 {
+            boogie_type(env, &output_types[0], false)
         } else {
-            boogie_type(env, &Type::Tuple(declared_results.clone()), false)
+            boogie_type(env, &Type::Tuple(output_types.clone()), false)
         };
 
         emitln!(
@@ -2134,13 +2145,12 @@ impl<'env> BoogieTranslator<'env> {
             result_type
         );
 
-        let result_of_call = format!("{}({})", result_of_name, all_call_args.join(", "));
+        let result_of_call = format!("{}({})", result_of_name, input_args.join(", "));
 
-        // ensures_of takes: input_args, then result slots (declared + post-state).
+        // ensures_of takes: input_args, then output slots (declared + post-state).
         let mut ensures_args = input_args.clone();
-        if declared_results.len() == 1 {
+        if output_types.len() == 1 {
             ensures_args.push(result_of_call.clone());
-            ensures_args.extend(post_args.iter().cloned());
             let body = format!("{}({})", ensures_of_name, ensures_args.join(", "));
             emitln!(
                 self.writer,
@@ -2150,11 +2160,10 @@ impl<'env> BoogieTranslator<'env> {
                 body
             );
         } else {
-            let tuple_projections: Vec<String> = (0..declared_results.len())
+            let tuple_projections: Vec<String> = (0..output_types.len())
                 .map(|i| format!("_r->${}", i))
                 .collect();
             ensures_args.extend(tuple_projections);
-            ensures_args.extend(post_args.iter().cloned());
             let body = format!(
                 "(var _r := {}; {}({}))",
                 result_of_call,
@@ -2169,61 +2178,6 @@ impl<'env> BoogieTranslator<'env> {
                 body
             );
         }
-
-        // Per-`&mut`-parameter functionality projections. `write_of_<j>`
-        // takes only the input slots (no post-state) and returns the j-th
-        // `&mut` post-state. The functionality axiom says: whenever
-        // `ensures_of(..., q_*)` holds, `q_j == write_of_<j>(inputs)`.
-        // Together with the `result_of` axiom this lets the verifier derive
-        // that all outputs of a deterministic `f` are functions of inputs.
-        let input_decls: Vec<String> = param_decls
-            .iter()
-            .take(param_decls.len() - post_state_types.len())
-            .cloned()
-            .collect();
-        for (j, ty) in post_state_types.iter().enumerate() {
-            let write_of_name =
-                boogie_behavioral_eval_fun_name(env, fun_type, BehaviorKind::WriteOf(j));
-            let write_of_call = format!("{}({})", write_of_name, input_args.join(", "));
-            emitln!(
-                self.writer,
-                "function {}({}): {};",
-                write_of_name,
-                input_decls.join(", "),
-                boogie_type(env, ty, false)
-            );
-            // Quantifier vars: inputs + remaining q's (for ensures_of's tail).
-            let q_decls: Vec<String> = post_state_types
-                .iter()
-                .enumerate()
-                .map(|(i, ty)| format!("q{}: {}", i, boogie_type(env, ty, false)))
-                .collect();
-            let r_decls: Vec<String> = declared_results
-                .iter()
-                .enumerate()
-                .map(|(i, ty)| format!("r{}: {}", i, boogie_type(env, ty, false)))
-                .collect();
-            let r_args: Vec<String> = (0..declared_results.len())
-                .map(|i| format!("r{}", i))
-                .collect();
-            let mut all_quant = input_decls.clone();
-            all_quant.extend(r_decls);
-            all_quant.extend(q_decls);
-            let mut ensures_call_args = input_args.clone();
-            ensures_call_args.extend(r_args);
-            ensures_call_args.extend(post_args.iter().cloned());
-            let ensures_call = format!("{}({})", ensures_of_name, ensures_call_args.join(", "));
-            emitln!(
-                self.writer,
-                "axiom (forall {} :: {{{}, {}}} {} ==> q{} == {});",
-                all_quant.join(", "),
-                ensures_call,
-                write_of_call,
-                ensures_call,
-                j,
-                write_of_call
-            );
-        }
     }
 
     /// Generate per-function behavioral spec functions for closure target functions.
```

### third_party/move/move-prover/boogie-backend/src/spec_translator.rs
```diff
@@ -1732,6 +1732,57 @@ impl SpecTranslator<'_> {
 
         let eval_fun_name = boogie_behavioral_eval_fun_name(self.env, &inst_fun_type, kind);
 
+        // The `ResultOf`/`WriteOf(j)` evaluator shares a single tuple Skolem
+        // returning `(declared..., post_states...)`. Compute the projection
+        // needed at this call site — matches `translate_behavior_for_closure`.
+        let (num_explicit_results, num_mut_refs) = match &inst_fun_type {
+            Type::Fun(arg_ty, result_ty, _) => {
+                let n_args = arg_ty
+                    .clone()
+                    .flatten()
+                    .iter()
+                    .filter(|ty| ty.is_mutable_reference())
+                    .count();
+                ((*result_ty).clone().flatten().len(), n_args)
+            },
+            _ => (0, 0),
+        };
+        let total_outputs = num_explicit_results + num_mut_refs;
+        let multi_in_boogie = total_outputs > 1;
+        let projection = match kind {
+            BehaviorKind::ResultOf if multi_in_boogie && total_outputs > num_explicit_results => {
+                if num_explicit_results == 1 {
+                    Some(ProjKind::Single(0))
+                } else {
+                    Some(ProjKind::Truncate(num_explicit_results))
+                }
+            },
+            BehaviorKind::WriteOf(j) if multi_in_boogie => {
+                Some(ProjKind::Single(num_explicit_results + j))
+            },
+            _ => None,
+        };
+
+        // For `ResultOf`, `wrap_mut_ref_bp_inputs` appends trailing post-state
+        // clones to `pred_args`. The tuple Skolem doesn't take them — the
+        // post-state is in its output tuple instead — so skip them here.
+        // `WriteOf(j)` never has trailing post-state clones.
+        let emit_arg_count = match kind {
+            BehaviorKind::ResultOf => {
+                let num_inputs = match &inst_fun_type {
+                    Type::Fun(arg_ty, _, _) => arg_ty.clone().flatten().len(),
+                    _ => pred_args.len(),
+                };
+                num_inputs.min(pred_args.len())
+            },
+            _ => pred_args.len(),
+        };
+
+        match projection {
+            Some(ProjKind::Single(_)) => emit!(self.writer, "("),
+            Some(ProjKind::Truncate(_)) => emit!(self.writer, "(var _r := "),
+            None => {},
+        }
         emit!(self.writer, "{}(", eval_fun_name);
         let has_mem =
             self.emit_evaluator_memory_args(node_id, &inst_fun_type, kind, &range.pre, &range.post);
@@ -1761,11 +1812,19 @@ impl SpecTranslator<'_> {
         } else {
             (None, None)
         };
-        let last_idx = pred_args.len().saturating_sub(1);
-        for (i, arg) in pred_args.iter().enumerate() {
+        // `post_sub` substitutes the last `pred_args` slot — that's the trailing
+        // post-state clone for `EnsuresOf`. For `ResultOf` we've truncated away
+        // that slot, so the substitution would land on an input by mistake; gate
+        // it accordingly.
+        let post_sub_idx = if matches!(kind, BehaviorKind::ResultOf) {
+            None
+        } else {
+            Some(pred_args.len().saturating_sub(1))
+        };
+        for (i, arg) in pred_args.iter().take(emit_arg_count).enumerate() {
             emit!(self.writer, ", ");
             if let Some(ref var) = post_sub {
-                if i == last_idx {
+                if Some(i) == post_sub_idx {
                     emit!(self.writer, "{}", var);
                     continue;
                 }
@@ -1779,6 +1838,19 @@ impl SpecTranslator<'_> {
             self.translate_behavior_arg(arg);
         }
         emit!(self.writer, ")");
+        match projection {
+            Some(ProjKind::Single(idx)) => emit!(self.writer, ")->${}", idx),
+            Some(ProjKind::Truncate(n)) => {
+                emit!(self.writer, "; $Tuple{}(", n);
+                let mut sep = "";
+                for i in 0..n {
+                    emit!(self.writer, "{}_r->${}", sep, i);
+                    sep = ", ";
+                }
+                emit!(self.writer, "))");
+            },
+            None => {},
+        }
     }
 
     /// Position of the first `&mut T` parameter in a function type — used by
```

### third_party/move/move-prover/tests/sources/functional/closures/result_of_mut_ref_soundness.move
```diff
@@ -0,0 +1,30 @@
+// flag: --check-inconsistency
+//
+// Checks that the verification context for `result_of` / `write_of_j` on
+// `&mut`-bearing function values is satisfiable across the shapes the
+// per-type evaluator handles (single `&mut`, multiple `&mut`, and
+// multi-declared return + `&mut`).
+module 0x42::result_of_mut_ref_soundness {
+
+    // 1 declared + 1 `&mut`.
+    fun apply_mut(f: |&mut u64| u64, x: &mut u64): u64 { f(x) }
+    spec apply_mut {
+        ensures result == result_of<f>(x);
+        ensures ensures_of<f>(x, result);
+    }
+
+    // 1 declared + 2 `&mut`.
+    fun apply_two_mut(f: |&mut u64, &mut u64| u64, p: &mut u64, q: &mut u64): u64 {
+        f(p, q)
+    }
+    spec apply_two_mut {
+        ensures result == result_of<f>(p, q);
+        ensures ensures_of<f>(p, q, result);
+    }
+
+    // 2 declared + 1 `&mut`.
+    fun apply_mut_multi(f: |&mut u64| (u64, u64), x: &mut u64): (u64, u64) { f(x) }
+    spec apply_mut_multi {
+        ensures (result_1, result_2) == result_of<f>(x);
+    }
+}
```
