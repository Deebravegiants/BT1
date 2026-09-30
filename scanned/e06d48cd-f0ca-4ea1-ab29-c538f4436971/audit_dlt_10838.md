# [?] feat: signer-only check for shadow block exploit

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-03-13
Source: https://github.com/stacks-network/stacks-core/commit/ba59fe77cc01d9ae1a7f9d9d792f4b452389a28c
Type: security-commit

## Details
feat: signer-only check for shadow block exploit

## Patch
### stacks-signer/src/chainstate/v2.rs
```diff
@@ -167,6 +167,16 @@ impl GlobalStateView {
         }
 
         if let Some(tenure_change) = block.get_tenure_change_tx_payload() {
+            if &tenure_change.prev_tenure_consensus_hash != parent_tenure_id {
+                warn!(
+                    "Block commit parent tenure mismatch: the block commit's parent_block_ptr does not correspond to the actual parent tenure";
+                    "committed_parent_tenure" => %parent_tenure_id,
+                    "actual_parent_tenure" => %tenure_change.prev_tenure_consensus_hash,
+                    "consensus_hash" => %block.header.consensus_hash,
+                    "signer_signature_hash" => %block.header.signer_signature_hash(),
+                );
+                return Err(RejectReason::InvalidParentBlock);
+            }
             Self::validate_tenure_change_payload(
                 tenure_change,
                 block,
```
