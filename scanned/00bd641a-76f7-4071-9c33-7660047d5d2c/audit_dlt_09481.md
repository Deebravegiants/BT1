# [?] Fix to integer overflows and an additional check to avoid another potential source of panics

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2024-11-17
Source: https://github.com/casper-network/casper-node/commit/8c9123ebc12c48f6daf812d3f47064a916fbd8cf
Type: security-commit

## Details
Fix to integer overflows and an additional check to avoid another potential source of panics

## Patch
### node/src/components/contract_runtime/rewards.rs
```diff
@@ -445,13 +445,14 @@ pub(crate) async fn fetch_data_and_calculate_rewards_for_era<REv: ReactorEventT>
                             acc.saturating_add(*current_era_reward)
                         });
                 let seigniorage_target_fraction = Ratio::new(
-                    actual_total_seigniorage.as_u128(),
-                    expected_total_seigniorage.as_u128(),
+                    actual_total_seigniorage.low_u128(),
+                    expected_total_seigniorage.low_u128(),
                 );
-                metrics.seigniorage_target_fraction.set(
-                    Ratio::to_f64(&seigniorage_target_fraction)
-                        .expect("expected fraction as float"),
-                )
+                let gauge_value = match Ratio::to_f64(&seigniorage_target_fraction) {
+                    Some(v) => v,
+                    None => f64::NAN,
+                };
+                metrics.seigniorage_target_fraction.set(gauge_value)
             }
             Err(_) => (),
         }
```
