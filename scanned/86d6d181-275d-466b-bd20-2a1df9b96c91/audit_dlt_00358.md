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

_Trimmed to 38 lines — full report: https://github.com/aptos-labs/aptos-core/commit/760099358b4e85b2a4c61f528e67b15887f755de_
