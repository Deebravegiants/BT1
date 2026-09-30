# [?] avoid logging an underflow, more underflow checks

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-01-26
Source: https://github.com/namada-net/namada/commit/94848b58850a0784012ac412f6b39079dafc5ec0
Type: security-commit

## Details
avoid logging an underflow, more underflow checks

## Patch
### crates/namada/src/ledger/governance/mod.rs
```diff
@@ -397,17 +397,19 @@ where
         if !is_valid_grace_epoch {
             tracing::info!(
                 "Expected min duration between the end and grace epoch \
-                 {min_grace_epoch}, but got {}",
-                grace_epoch - end_epoch
+                 {min_grace_epoch}, but got grace = {}, end = {}",
+                grace_epoch,
+                end_epoch
             );
         }
         let is_valid_max_proposal_period = start_epoch < grace_epoch
             && grace_epoch.0 - start_epoch.0 <= max_proposal_period;
         if !is_valid_max_proposal_period {
             tracing::info!(
                 "Expected max duration between the start and grace epoch \
-                 {max_proposal_period}, but got {}",
-                grace_epoch - start_epoch
+                 {max_proposal_period}, but got grace ={}, start = {}",
+                grace_epoch,
+                start_epoch
             );
         }
 
@@ -512,8 +514,11 @@ where
             self.force_read(&funds_key, ReadType::Post)?;
 
         if let Some(pre_balance) = pre_balance {
-            Ok(post_funds >= min_funds_parameter
-                && post_balance - pre_balance == post_funds)
+            let is_post_funds_greater_than_minimum =
+                post_funds >= min_funds_parameter;
+            let is_valid_funds = post_balance >= pre_balance
+                && post_balance - pre_balance == post_funds;
+            Ok(is_post_funds_greater_than_minimum && is_valid_funds)
         } else {
             Ok(post_funds >= min_funds_parameter && post_balance == post_funds)
         }
```
