# [H] IsLtArraySubAir is unsound

## Summary
Severity: High
Reporter: ed255
Contest weight: 0.5440
Dataset id: 4889
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The IsLtArraySubAir circuit keeps a diff_marker that is supposed to select the first element in the array that differs. But if it picks the first element of the array, even if it doesn't differ, the constraints pass. With this we can have cases where x < y but instead of constraining out=true we can constrain out = false.  
For example consider the following inputs:  
• x = [0, 0].  
• y = [0, 1].  
The expected valid witness is:  
• diff_marker = [0, 1].  
• diff_val = 1.  
• out = 1.  
But the following witness also passes the constraints:  
• diff_marker = [1, 0].  
• diff_val = 0.  
• out = 0.

Impact Explanation:  
IsLtArraySubAir is used in VolatileBoundaryChip. I'm don't know yet how is this chip used to assess the impact so I'll give it Medium but it could be High.

## Proof of Concept
This proof of concept shows the issue for inputs like x = [0, 0], y = [0,1]:  
```diff
--- a/crates/circuits/primitives/src/is_less_than_array/mod.rs
+++ b/crates/circuits/primitives/src/is_less_than_array/mod.rs
@@ -220,16 +220,25 @@ impl<F: PrimeField32, const NUM: usize> TraceSubRowGenerator<F> for IsLtArraySub
    (aux, out): (IsLtArrayAuxColsMut<'a, F>, &'a mut F),
) {
    tracing::trace!("IsLtArraySubAir::generate_subrow x={:?}, y={:?}", x, y);
-
    let mut is_eq = true;
-
    *aux.diff_val = F::ZERO;
-
    for (x_i, y_i, diff_marker) in izip!(x, y, aux.diff_marker.iter_mut()) {
-
        if x_i != y_i && is_eq {
-
            is_eq = false;
-
            *diff_marker = F::ONE;
-
            *aux.diff_val = *y_i - *x_i;
-
        } else {
-
            *diff_marker = F::ZERO;
+
        let original = false;
+
        if original {
+
            let mut is_eq = true;
+
            *aux.diff_val = F::ZERO;
+
            for (x_i, y_i, diff_marker) in izip!(x, y, aux.diff_marker.iter_mut()) {
+
                if x_i != y_i && is_eq {
+
                    is_eq = false;
+
                    *diff_marker = F::ONE;
+
                    *aux.diff_val = *y_i - *x_i;
+
                } else {
+
                    *diff_marker = F::ZERO;
+
                }
            }
+
        } else {
+
            // Overwrite
+
            *aux.diff_val = F::ZERO;
+
            aux.diff_marker[0] = F::ONE;
+
            aux.diff_marker[1] = F::ZERO;
+
            // *out = F::ZERO;
        }
    }
    // diff_val can be "negative" but shifted_diff is in [0, 2^{max_bits+1})
    let shifted_diff =
@@ -237,6 +246,12 @@ impl<F: PrimeField32, const NUM: usize> TraceSubRowGenerator<F> for IsLtArraySub
    let lower_u32 = shifted_diff & ((1 << self.max_bits()) - 1);
    *out = F::from_bool(shifted_diff != lower_u32);
+
    println!(
+
        "dbg diff_marker={:?}, diff_val={:?}",
+
        aux.diff_marker, aux.diff_val
+
    );
+
    println!("dbg x={:?} < y={:?} out={}", x, y, *out == F::ONE);
+
    // decompose lower_u32 into limbs and range check
    range_checker.decompose(lower_u32, self.max_bits(), aux.lt_decomp);
}
```

## Recommendation
Add a constrain to make sure we can't set the marker earlier than the first diff. For example constrain that if diff_value=0, then diff_marker[last] = 1 (the only condition for diff_value=0 is that all values are the same, which is guaranteed with diff_marker has 1 at the last position and diff_value=0).
