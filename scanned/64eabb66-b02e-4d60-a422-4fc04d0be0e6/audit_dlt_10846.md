# [?] Fix race condition in idle_tenure_extend_active_mining

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2025-06-23
Source: https://github.com/stacks-network/stacks-core/commit/04d69df7ee3ff2068db0415443c9340049045382
Type: security-commit

## Details
Fix race condition in idle_tenure_extend_active_mining

Signed-off-by: Jacinta Ferrant <jacinta.ferrant@gmail.com>

## Patch
### testnet/stacks-node/src/tests/signer/v0.rs
```diff
@@ -6819,6 +6819,12 @@ fn idle_tenure_extend_active_mining() {
                 TEST_MINE_STALL.set(false);
             });
 
+            // We must actually have a new block response to ensure its tenure extend timestamp advances
+            wait_for(30, || {
+                Ok(signer_test.get_latest_block_response(slot_id) != last_response)
+            })
+            .expect("Failed to find a new block response");
+
             let latest_response = signer_test.get_latest_block_response(slot_id);
             let naka_blocks = test_observer::get_mined_nakamoto_blocks();
             info!(
```
