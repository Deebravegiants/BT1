# [?] goten/fix-bv-mul-overflow (#20571)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-09-17
Source: https://github.com/aptos-labs/aptos-core/commit/b683b5011120c20ef8497bee9bf5b18c3a9cac1d
Type: security-commit

## Details
goten/fix-bv-mul-overflow (#20571)

## Patch
### third_party/move/move-prover/boogie-backend/src/lib.rs
```diff
@@ -243,7 +243,7 @@ fn bv_helper() -> Vec<BvInfo> {
     bv_info.push(bv_16);
     let bv_32 = BvInfo {
         base: 32,
-        max: "2147483647".to_string(),
+        max: "4294967295".to_string(),
     };
     bv_info.push(bv_32);
     let bv_64 = BvInfo {
```

### third_party/move/move-prover/boogie-backend/src/prelude/prelude.bpl
```diff
@@ -326,7 +326,8 @@ procedure {:inline 1} $SubBv{{impl.base}}(src1: bv{{impl.base}}, src2: bv{{impl.
 
 procedure {:inline 1} $MulBv{{impl.base}}(src1: bv{{impl.base}}, src2: bv{{impl.base}}) returns (dst: bv{{impl.base}})
 {
-    if ($Lt'Bv{{impl.base}}'($Mul'Bv{{impl.base}}'(src1, src2), src1)) {
+    if (src2 != 0bv{{impl.base}} &&
+        $Gt'Bv{{impl.base}}'(src1, $Div'Bv{{impl.base}}'({{impl.max}}bv{{impl.base}}, src2))) {
         call $ExecFailureAbort();
         return;
     }
```

### third_party/move/move-prover/tests/sources/regression/bv_mul_overflow.exp
```diff
@@ -0,0 +1,22 @@
+Move prover returns: exiting with verification errors
+error: abort not covered by any of the `aborts_if` clauses
+   ┌─ tests/sources/regression/bv_mul_overflow.move:55:5
+   │
+53 │           (x | 0u8) * 129u8
+   │           ----------------- abort happened here with execution failure
+54 │       }
+55 │ ╭     spec multiply_incorrect {
+56 │ │         requires x == 2;
+57 │ │         aborts_if false;
+58 │ │         ensures result <= 255u8;
+59 │ │         ensures result == 2u8;
+60 │ │         ensures result  == (2 * 129);
+61 │ │     }
+   │ ╰─────^
+   │
+   =     at tests/sources/regression/bv_mul_overflow.move:52: multiply_incorrect
+   =     at tests/sources/regression/bv_mul_overflow.move:56: multiply_incorrect (spec)
+   =     at tests/sources/regression/bv_mul_overflow.move:52: multiply_incorrect
+   =         x = <redacted>
+   =     at tests/sources/regression/bv_mul_overflow.move:53: multiply_incorrect
+   =         ABORTED
```

### third_party/move/move-prover/tests/sources/regression/bv_mul_overflow.move
```diff
@@ -0,0 +1,62 @@
+/// Title: Bitvector multiplication returns 2 instead of reporting a u8 overflow
+///
+/// Description:
+/// The public function multiplies a u8 value by 129. Its precondition fixes
+/// the input to 2, so the mathematical product is 258. Checked u8 arithmetic
+/// must abort because 258 is greater than 255. The prover instead accepts
+/// both `aborts_if false` and the direct postcondition `result == 2u8`.
+/// The identity `x | 0u8` selects the bitvector path without changing x.
+///
+/// Reproduction:
+/// `cargo test -p move-prover --test testsuite bv_mul_overflow -- --test-threads=1`
+///
+/// Observed behavior:
+/// The test passes because the prover accepts BvMulOverflow::multiply_incorrect.
+/// It proves that the call does not abort and returns the wrapped value 2.
+///
+/// Concrete counterexample:
+/// Set x to 2. The expression `x | 0u8` is 2, and 2 * 129 is 258.
+/// There is no valid u8 result for this checked multiplication, so execution
+/// must abort. The accepted contract instead describes a normal return of 2.
+///
+/// Expected behavior:
+/// Verification must fail because `aborts_if false` does not cover the
+/// required overflow. The result postcondition should be unreachable.
+///
+/// Root cause:
+/// `BitOr` marks its result as `Bitwise`, and the `Mul` transfer rule merges
+/// that classification into the multiplication result:
+/// third_party/move/move-prover/bytecode-pipeline/src/number_operation_analysis.rs:1153-1172.
+/// The backend emits `$OrBv8` for `|` and selects `$MulBv8` for `*`:
+/// third_party/move/move-prover/boogie-backend/src/bytecode_translator.rs:7674-7687,7930-8010.
+/// `$MulBv8` is defined in:
+/// third_party/move/move-prover/boogie-backend/src/prelude/prelude.bpl:327-334.
+/// Its overflow check compares the wrapped product with the first operand.
+/// Here 258 wraps to 2, so the check becomes 2 < 2 and misses the abort.
+///
+/// A correct check needs the maximum value of the bitvector width. That value
+/// comes from `BvInfo::max`, which `bv_helper` populates per width, and the
+/// bv32 entry holds the maximum of a *signed* 32-bit integer, 2147483647,
+/// where every other width holds `2^n - 1`:
+/// third_party/move/move-prover/boogie-backend/src/lib.rs:244-247.
+/// The same understated bound is unsound on its own: `$IsValid'bv32'` is an
+/// assumption, not a check, so a bv32 literal above 2147483647 assumes false
+/// and makes everything after it vacuous
+/// (third_party/move/move-prover/boogie-backend/src/prelude/prelude.bpl:396-398),
+/// while `$CastBv{n}to32` and `$int2bv32` abort above the same bound
+/// (prelude.bpl:721-726,404-411) and the `$bv2int`/`$int2bv` round-trip axiom
+/// is guarded by it (prelude.bpl:420-422).
+/// Both defects are therefore fixed together: `bv_helper` gets the unsigned
+/// bv32 maximum, and `$MulBv{n}` compares `src1` against `MAX / src2`.
+module 0x42::BvMulOverflow {
+    public fun multiply_incorrect(x: u8): u8 {
+        (x | 0u8) * 129u8
+    }
+    spec multiply_incorrect {
+        requires x == 2;
+        aborts_if false;
+        ensures result <= 255u8;
+        ensures result == 2u8;
+        ensures result  == (2 * 129);
+    }
+}
```
