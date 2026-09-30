# [?] fix: syn-sel should be range-checked when overflow (#913)

## Summary
Severity: Unknown
Chain: ZK
Component: zkonduit/ezkl
Published: 2025-01-23
Source: https://github.com/zkonduit/ezkl/commit/fc5be4f9493353ab0c893f5c166fd231fb2c4e0a
Type: security-commit

## Details
fix: syn-sel should be range-checked when overflow (#913)

## Patch
### src/circuit/ops/chip.rs
```diff
@@ -592,9 +592,9 @@ impl<F: PrimeField + TensorType + PartialOrd + std::hash::Hash> BaseConfig<F> {
                         // this is 0 if the index is the same as the column index (starting from 1)
 
                         let col_expr = sel.clone()
-                            * table
+                            * (table
                                 .selector_constructor
-                                .get_expr_at_idx(col_idx, synthetic_sel);
+                                .get_expr_at_idx(col_idx, synthetic_sel));
 
                         let multiplier =
                             table.selector_constructor.get_selector_val_at_idx(col_idx);
@@ -626,6 +626,40 @@ impl<F: PrimeField + TensorType + PartialOrd + std::hash::Hash> BaseConfig<F> {
                         res
                     });
                 }
+
+                // add a degree-k custom constraint of the following form to the range check and
+                // static lookup configuration.
+                // 𝑚𝑢𝑙𝑡𝑖𝑠𝑒𝑙 · ∏ (𝑠𝑒𝑙 − 𝑖) = 0 where 𝑠𝑒𝑙 is the synthetic_sel, and the product is over the set of overflowed columns
+                // and 𝑚𝑢𝑙𝑡𝑖𝑠𝑒𝑙 is the selector value at the column index
+                cs.create_gate("range_check_on_sel", |cs| {
+                    let synthetic_sel = match len {
+                        1 => Expression::Constant(F::from(1)),
+                        _ => match index {
+                            VarTensor::Advice { inner: advices, .. } => {
+                                cs.query_advice(advices[x][y], Rotation(0))
+                            }
+                            _ => unreachable!(),
+                        },
+                    };
+
+                    let range_check_on_synthetic_sel = match len {
+                        1 => Expression::Constant(F::from(0)),
+                        _ => {
+                            let mut initial_expr = Expression::Constant(F::from(1));
+                            for i in 0..len {
+                                initial_expr = initial_expr
+                                    * (synthetic_sel.clone()
+                                        - Expression::Constant(F::from(i as u64)))
+                            }
+                            initial_expr
+                        }
+                    };
+
+                    let sel = cs.query_selector(multi_col_selector);
+
+                    Constraints::with_selector(sel, vec![range_check_on_synthetic_sel])
+                });
+
                 self.static_lookups
                     .selectors
                     .insert((nl.clone(), x, y), multi_col_selector);
@@ -904,9 +938,9 @@ impl<F: PrimeField + TensorType + PartialOrd + std::hash::Hash> BaseConfig<F> {
                         let default_x = range_check.get_first_element(col_idx);
 
                         let col_expr = sel.clone()
-                            * range_check
+                            * (range_check
                                 .selector_constructor
-                                .get_expr_at_idx(col_idx, synthetic_sel);
+                                .get_expr_at_idx(col_idx, synthetic_sel));
 
                         let multiplier = range_check
                             .selector_constructor
@@ -929,6 +963,40 @@ impl<F: PrimeField + TensorType + PartialOrd + std::hash::Hash> BaseConfig<F> {
                         res
                     });
                 }
+
+                // add a degree-k custom constraint of the following form to the range check and
+                // static lookup configuration.
+                // 𝑚𝑢𝑙𝑡𝑖𝑠𝑒𝑙 · ∏ (𝑠𝑒𝑙 − 𝑖) = 0 where 𝑠𝑒𝑙 is the synthetic_sel, and the product is over the set of overflowed columns
+                // and 𝑚𝑢𝑙𝑡𝑖𝑠𝑒𝑙 is the selector value at the column index
+                cs.create_gate("range_check_on_sel", |cs| {
+                    let synthetic_sel = match len {
+                        1 => Expression::Constant(F::from(1)),
+                        _ => match index {
+                            VarTensor::Advice { inner: advices, .. } => {
+                                cs.query_advice(advices[x][y], Rotation(0))
+                            }
+                            _ => unreachable!(),
+                        },
+                    };
+
+                    let range_check_on_synthetic_sel = match len {
+                        1 => Expression::Constant(F::from(0)),
+                        _ => {
+                            let mut initial_expr = Expression::Constant(F::from(1));
+                            for i in 0..len {
+                                initial_expr = initial_expr
+                                    * (synthetic_sel.clone()
+                                        - Expression::Constant(F::from(i as u64)))
+                            }
+                            initial_expr
+                        }
+                    };
+
+                    let sel = cs.query_selector(multi_col_selector);
+
+                    Constraints::with_selector(sel, vec![range_check_on_synthetic_sel])
+                });
+
                 self.range_checks
                     .selectors
                     .insert((range, x, y), multi_col_selector);
```
