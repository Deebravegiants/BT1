# [?] fix: clamp logderivative inverse range to fix nightly debug build OOB (#22312)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-04-06
Source: https://github.com/AztecProtocol/aztec-packages/commit/5f080e9d292da4e83fdb972fa6b730a602d95cc5
Type: security-commit

## Details
fix: clamp logderivative inverse range to fix nightly debug build OOB (#22312)

## Summary
Fixes nightly barretenberg debug build which crashes with SIGABRT (exit
code 134) in test
`AvmRecursiveTests.TwoLayerAvmRecursionFailsWithWrongPIs`.

**Root cause:** In `compute_logderivative_inverse()`, the multi-threaded
path splits work by `circuit_size`, but `inverse_polynomial.coeffs()`
only covers the actual (non-virtual) data. When a thread chunk's `start`
exceeds the polynomial's actual size, `coeffs()[start]` is out of bounds
— caught by `_GLIBCXX_DEBUG`'s span bounds checking in the debug build
preset.

**Fix:** Clamp `start`/`end` to the polynomial's actual data range
before `batch_invert`. Virtual zero elements need no inversion.

Note: The `batch_invert` reserve→resize fix from the original PR #22312
is no longer needed as it was already applied on `next`. PR #22314 can
be closed as duplicate.

## Patch
### barretenberg/cpp/src/barretenberg/honk/proof_system/logderivative_library.hpp
```diff
@@ -59,11 +59,17 @@ void compute_logderivative_inverse(Polynomials& polynomials, auto& relation_para
             });
             inverse_polynomial.at(i) = denominator;
         }
-        FF* ffstart = &inverse_polynomial.coeffs()[start];
-        std::span<FF> to_invert(ffstart, end - start);
-        // Compute inverse polynomial I in place by inverting the product at each row
-        // Note: zeroes are ignored as they are not used anyway
-        FF::batch_invert(to_invert);
+        // Clamp to the polynomial's actual (non-virtual) data range; virtual zero elements need no inversion.
+        const size_t actual_size = inverse_polynomial.size();
+        const size_t clamped_start = std::min(start, actual_size);
+        const size_t clamped_end = std::min(end, actual_size);
+        if (clamped_start < clamped_end) {
+            FF* ffstart = &inverse_polynomial.coeffs()[clamped_start];
+            std::span<FF> to_invert(ffstart, clamped_end - clamped_start);
+            // Compute inverse polynomial I in place by inverting the product at each row
+            // Note: zeroes are ignored as they are not used anyway
+            FF::batch_invert(to_invert);
+        }
     };
     if constexpr (UseMultithreading) {
         parallel_for([&](const ThreadChunk& chunk) {
```
