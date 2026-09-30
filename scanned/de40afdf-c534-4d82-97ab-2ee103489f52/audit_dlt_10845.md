# [?] fix: prevent panic in  test setup

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2025-07-01
Source: https://github.com/stacks-network/stacks-core/commit/66bfc13bd4ecfb012b3d89057fc0c50cfe9a5313
Type: security-commit

## Details
fix: prevent panic in  test setup

## Patch
### testnet/stacks-node/src/tests/signer/v0.rs
```diff
@@ -292,11 +292,11 @@ impl SignerTest<SpawnedSigner> {
             Ok(self
                 .stacks_client
                 .get_reward_set_signers(reward_cycle)
-                .expect("Failed to check if reward set is calculated")
-                .map(|reward_set| {
+                .and_then(|reward_set| {
                     debug!("Signer set: {reward_set:?}");
+                    Ok(reward_set.is_some())
                 })
-                .is_some())
+                .unwrap_or(false))
         })
         .expect("Timed out waiting for reward set calculation");
         info!("Signer set calculated");
```
