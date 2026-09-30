# [?] AppendableBlock: fix potential panic when invalid config is used

## Summary
Severity: Unknown
Chain: Casper
Component: casper-network/casper-node
Published: 2023-01-03
Source: https://github.com/casper-network/casper-node/commit/a821b4f145c15f80ced13b0fbd4b9fba313377a7
Type: security-commit

## Details
AppendableBlock: fix potential panic when invalid config is used

When an invalid `DeployConfig` is used, the implementation of
`AppendableBlock::would_exceed_approval_limits` can panic due to
arithmetic operations that can overflow. Replace these with safer
variants. Also add some tests for the use case that was failing.

Signed-off-by: Alexandru Sardan <alexandru@casperlabs.io>

## Patch
### node/src/types/appendable_block.rs
```diff
@@ -13,7 +13,7 @@ use crate::types::{
     DeployHashWithApprovals,
 };
 
-#[derive(Debug, Error)]
+#[derive(Debug, Error, PartialEq)]
 pub(crate) enum AddError {
     #[error("would exceed maximum transfer count per block")]
     TransferCount,
@@ -190,7 +190,12 @@ impl AppendableBlock {
             - self.transfers.len()
             + self.deploy_config.block_max_deploy_count as usize
             - self.deploys.len();
-        additional_approvals > remaining_approval_slots - remaining_deploy_slots + 1
+        if let Some(total_approvals) = additional_approvals.checked_add(remaining_deploy_slots) {
+            // safe to subtract since `additional_approvals` is at least 1
+            total_approvals - 1 > remaining_approval_slots
+        } else {
+            true
+        }
     }
 }
 
@@ -221,3 +226,61 @@ impl Display for AppendableBlock {
         )
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use crate::types::Deploy;
+    use casper_types::{testing::TestRng, TimeDiff};
+    use rand::Rng;
+
+    impl AppendableBlock {
+        pub(crate) fn deploy_and_transfer_set(&self) -> &HashSet<DeployHash> {
+            &self.deploy_and_transfer_set
+        }
+    }
+
+    fn test_limits_with_config(deploy_config: &DeployConfig) {
+        let mut rng = TestRng::new();
+
+        let ttl = TimeDiff::from_seconds(rng.gen_range(360..3600));
+        let deploy = Deploy::random_valid_native_transfer_with_timestamp_and_ttl(
+            &mut rng,
+            Timestamp::now(),
+            ttl,
+        );
+        let mut block = AppendableBlock::new(*deploy_config, Timestamp::now());
+        // expected not to panic and return an error gracefully
+        assert_eq!(
+            block.add(
+                DeployHashWithApprovals::new(*deploy.hash(), deploy.approvals().clone()),
+                &deploy.footprint().unwrap(),
+            ),
+            Err(AddError::ApprovalCount)
+        );
+    }
+
+    #[test]
+    fn test_approval_limits_invalid_max_transfer_count() {
+        // set an invalid size for `block_max_transfer_count` in the deploy config
+        let deploy_config = DeployConfig {
+            block_max_approval_count: 3000,
+            block_max_transfer_count: 3000,
+            ..Default::default()
+        };
+
+        test_limits_with_config(&deploy_config);
+    }
+
+    #[test]
+    fn test_approval_limits_invalid_max_approval_count() {
+        let deploy_config = DeployConfig {
+            block_max_transfer_count: 3000,
+            block_max_approval_count: 0,
+            block_max_deploy_count: 300,
+            ..Default::default()
+        };
+
+        test_limits_with_config(&deploy_config);
+    }
+}
```
