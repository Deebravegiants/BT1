# [?] Avoid crashing upon failing to process self chunk endorsements (#11751)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-07-11
Source: https://github.com/near/nearcore/commit/e7802e5b2a8d3dbbaa6f44c962b6f70a58854e3f
Type: security-commit

## Details
Avoid crashing upon failing to process self chunk endorsements (#11751)

This is a stopgap measure for the problem highlighted in #11750 

There's a corner case related to switching validator key that brings the
node to temporarily fail to apply self chunk endorsement. I think it
might be better to carry on rather than crash since this doesn't break
the chain.

Also fixes the failing test `validator_switch_key`

## Patch
### chain/client/src/stateless_validation/chunk_validator/mod.rs
```diff
@@ -225,10 +225,16 @@ pub(crate) fn send_chunk_endorsement_to_block_producers(
     let endorsement = ChunkEndorsement::new(chunk_header.chunk_hash(), signer);
     for block_producer in block_producers {
         if signer.validator_id() == &block_producer {
-            // Unwrap here as we always expect our own endorsements to be valid
-            chunk_endorsement_tracker
+            // Our own endorsements are not always valid (see issue #11750).
+            if let Err(err) = chunk_endorsement_tracker
                 .process_chunk_endorsement(chunk_header, endorsement.clone())
-                .unwrap();
+            {
+                tracing::warn!(
+                    target: "client",
+                    ?chunk_hash,
+                    ?endorsement,
+                    "Failed to process self chunk endorsement ({err:?})");
+            }
         } else {
             network_sender.send(PeerManagerMessageRequest::NetworkRequests(
                 NetworkRequests::ChunkEndorsement(block_producer, endorsement.clone()),
```
