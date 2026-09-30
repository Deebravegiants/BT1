# [?] fix(op-revm): return error instead of panic when enveloped_tx is missing (bluealloy/revm#3055)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2025-10-07
Source: https://github.com/ethereum-optimism/optimism/commit/727ab9add6a7a4212a156846d6da01ef2249016f
Type: security-commit

## Details
fix(op-revm): return error instead of panic when enveloped_tx is missing (bluealloy/revm#3055)

* fix(op-revm): return error instead of panic when enveloped_tx is missing

* Update crates/op-revm/src/handler.rs

Co-authored-by: rakita <rakita@users.noreply.github.com>

* fmt

---------

Co-authored-by: rakita <rakita@users.noreply.github.com>

## Patch
### src/handler.rs
```diff
@@ -124,11 +124,11 @@ where
 
             if !ctx.cfg().is_fee_charge_disabled() {
                 // account for additional cost of l1 fee and operator fee
-                let enveloped_tx = ctx
-                    .tx()
-                    .enveloped_tx()
-                    .expect("all not deposit tx have enveloped tx")
-                    .clone();
+                let Some(enveloped_tx) = ctx.tx().enveloped_tx().cloned() else {
+                    return Err(ERROR::from_string(
+                        "[OPTIMISM] Failed to load enveloped transaction.".into(),
+                    ));
+                };
 
                 // compute L1 cost
                 additional_cost = ctx.chain_mut().calculate_tx_l1_cost(&enveloped_tx, spec);
```
