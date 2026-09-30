# [?] fix(types): reject out-of-bounds count in splice_at_count

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-06-12
Source: https://github.com/AztecProtocol/aztec-packages/commit/981c174b571556b57e3078fc33b15e9f0d2ae67c
Type: security-commit

## Details
fix(types): reject out-of-bounds count in splice_at_count

## Audit finding 10 — `splice_at_count.nr` (`splice_at_count`)

One of the informational/warning audit findings (index: #269). Reviewers' description:

> The `splice_at_count()` method does not validate whether `count <= N`. If `count > N`, then `count` is not a valid splice point: the helper loop is skipped, the validation never switches to `array2`, and `array1` is accepted unchanged. A caller may therefore believe the result includes `count` elements from `array1` followed by elements from `array2`, even though `count` is outside the array bounds.

**Why it matters:** `splice_at_count(array1, count, array2)` is meant to produce `array1[0..count]` followed by `array2[0..N-count]`. When `count > N`, the unconstrained helper's loop (`count..N`) is empty and the validator never switches to `array2`, so the function just returns `array1` unchanged — masking a caller bug while the caller believes a real splice happened. Informational/warning severity.

## Resolution

Add `assert(count <= N, "Invalid count: splice_at_count requires count <= N")` at the top of the function — the boundary `count == N` stays valid (result is `array1` unchanged). Both current callers already guarantee `count <= N`, so no valid behavior changes.

## Tests

`should_fail` for `count > N` (just-over and far-over); single-element arrays; the existing happy-path coverage for counts `0..N` is retained. 20/20 splice_at_count tests pass; `nargo fmt` clean.

## Constraint impact

`splice_at_count` has exactly four call sites, all in `rollup-lib` — **no kernel circuit is affected**. The added line is a single `u32` `count <= N` comparison per call, and neither call site is in a loop.

Call sites:
- `checkpoint_merge/utils/merge_checkpoint_rollups.nr` — 2 calls (`checkpoint_header_hashes`, `fees`); `count = num_left_checkpoints`, `N = MAX_CHECKPOINTS_PER_EPOCH`.
- `tx_base/components/public_tx_effect_builder.nr` — 2 calls (`private_logs`, `contract_class_log_hashes`), inside the non-reverted `if` (both branches are constrained); `count` = the respective non-revertible array length.

Impacted circuit binaries:

| Circuit | Crate | `splice_at_count` calls | Added ACIR opcodes (~4/call) |
| --- | --- | --- | --- |
| Checkpoint merge | `rollup-checkpoint-merge` | 2 | ~8 |
| Public tx base | `rollup-tx-base-public` (+ `rollup-tx-base-public-simulated`) | 2 | ~8 |

- Kernel circuits: none.
- Private tx base (`rollup-tx-base-private`): not affected — `public_tx_effect_builder` is on the public-only path.
- Recursive parents (block-root, block-merge, checkpoint-root, rollup-root): no change — proof-verification cost is independent of the inner circuit's gate count.

Per-call cost was measured with `nargo info` (nargo 1.0.0-beta.21): an isolated `assert(count <= 4096)` on a `u32` raises a trivial `main` from 2 → 6 ACIR opcodes, i.e. **~4 ACIR opcodes per call** (plus an unconstrained Brillig `directive_integer_quotient` for witness generation, which adds no proving constraints). The cost is fixed per call — independent of `N` and of runtime data — so each affected circuit gains ~8 ACIR opcodes, negligible (≪0.01%) against these circuits' size. ACIR opcodes are the nargo-available proxy; exact UltraHonk gate counts would require `bb gates` on the fully compiled circuit.

## Patch
### noir-projects/noir-protocol-circuits/crates/types/src/utils/arrays/splice_at_count.nr
```diff
@@ -17,6 +17,11 @@ pub fn splice_at_count<T, let N: u32>(array1: [T; N], count: u32, array2: [T; N]
 where
     T: Eq,
 {
+    // `count` is the splice point: `result[0..count]` comes from `array1` and `result[count..N]` from
+    // `array2`. A `count` greater than `N` is not a valid splice point, so reject it rather than
+    // silently returning `array1` unchanged (the helper loop would be skipped). `count == N` is valid.
+    assert(count <= N, "Invalid count: splice_at_count requires count <= N");
+
     // Safety: result is constrained below by `validate_splice_at_count_result`.
     let result = unsafe { splice_at_count_helper(array1, count, array2) };
 
@@ -92,6 +97,26 @@ mod tests {
         assert_eq(result, [1, 2, 3, 4, 5]);
     }
 
+    #[test(should_fail_with = "Invalid count: splice_at_count requires count <= N")]
+    fn count_out_of_bounds_fails() {
+        let array1 = [1, 2, 3, 4, 5];
+        let array2 = [10, 20, 30, 40, 50];
+        let _ = splice_at_count(array1, 6, array2);
+    }
+
+    #[test(should_fail_with = "Invalid count: splice_at_count requires count <= N")]
+    fn count_far_out_of_bounds_fails() {
+        let array1 = [1, 2, 3, 4, 5];
+        let array2 = [10, 20, 30, 40, 50];
+        let _ = splice_at_count(array1, 100, array2);
+    }
+
+    #[test]
+    fn splice_single_element_arrays() {
+        assert_eq(splice_at_count([1], 0, [9]), [9]); // count 0: all from array2
+        assert_eq(splice_at_count([1], 1, [9]), [1]); // count == N: all from array1
+    }
+
     #[test]
     fn merge_one_from_array1_rest_from_array2() {
         let array1 = [1, 2, 3, 4, 5];
```
