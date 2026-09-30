# [?] Fix slot-based collator panic during warp sync (#11072) (#11381)

## Summary
Severity: Unknown
Chain: Polkadot
Component: paritytech/polkadot-sdk
Published: 2026-04-02
Source: https://github.com/paritytech/polkadot-sdk/commit/a1a2bbfdb435f381ba633e62c022090f1efa4fca
Type: security-commit

## Details
Fix slot-based collator panic during warp sync (#11072) (#11381)

When a parachain collator starts with `--authoring=slot-based` and
performs warp sync, the `slot-based-block-builder` essential task
immediately calls `slot_duration()` which requires
`AuraApi_slot_duration`. During warp sync the runtime isn't ready, so
this fails and the task returns, shutting down the node.

The lookahead collator avoids this by calling `wait_for_aura()` before
starting. This PR adds an equivalent guard to the slot-based collator.

### Manual test
Before the fix the collator panicked after the relay chain warp sync
with AuraApi_slot_duration not available, which does not occur anymore
now.
```
 ./target/release/polkadot-parachain \                                                                                                                                                                                                                                                                          
    --chain asset-hub-polkadot \
    --sync warp \
    --authoring=slot-based \
    --tmp -- --sync warp
```
Closes #11072.

---------

Co-authored-by: cmd[bot] <41898282+github-actions[bot]@users.noreply.github.com>
Co-authored-by: clangenb <clangenb@users.noreply.github.com>

## Patch
### cumulus/polkadot-omni-node/lib/src/nodes/aura.rs
```diff
@@ -666,9 +666,16 @@ where
 			max_pov_percentage: node_extra_args.max_pov_percentage,
 		};
 
-		// We have a separate function only to be able to use `docify::export` on this piece of
-		// code.
-		Self::launch_slot_based_collator(params);
+		let wait_client = client.clone();
+		let fut = async move {
+			wait_for_aura::<Block, RuntimeApi, AuraId>(wait_client).await;
+			// We have a separate function only to be able to use `docify::export` on this
+			// piece of code.
+			Self::launch_slot_based_collator(params);
+		};
+		task_manager
+			.spawn_essential_handle()
+			.spawn("slot-based-collator-init", None, fut);
 
 		Ok(())
 	}
```

### prdoc/pr_11381.prdoc
```diff
@@ -0,0 +1,23 @@
+title: Fix slot-based collator panic during warp sync (#11072)
+doc:
+- audience: Node Dev
+  description: |-
+    When a parachain collator starts with `--authoring=slot-based` and performs warp sync, the `slot-based-block-builder` essential task immediately calls `slot_duration()` which requires `AuraApi_slot_duration`. During warp sync the runtime isn't ready, so this fails and the task returns, shutting down the node.
+
+    The lookahead collator avoids this by calling `wait_for_aura()` before starting. This PR adds an equivalent guard to the slot-based collator.
+
+    ### Manual test
+    Before the fix the collator panicked after the relay chain warp sync with AuraApi_slot_duration not available, which does not occur anymore now.
+    ```
+     ./target/release/polkadot-parachain \
+        --chain asset-hub-polkadot \
+        --sync warp \
+        --authoring=slot-based \
+        --tmp -- --sync warp
+    ```
+    Closes #11072.
+crates:
+- name: cumulus-client-consensus-aura
+  bump: patch
+- name: polkadot-omni-node-lib
+  bump: patch
```
